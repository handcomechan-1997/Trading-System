"""
交易策略基类和常用技术指标
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
import numpy as np
from loguru import logger


class Signal:
    """交易信号"""
    BUY = 1
    SELL = -1
    HOLD = 0


class Position:
    """持仓信息"""
    
    def __init__(self, symbol: str, shares: int, avg_price: float, timestamp: datetime):
        self.symbol = symbol
        self.shares = shares
        self.avg_price = avg_price
        self.timestamp = timestamp
        self.value = shares * avg_price
    
    def update(self, shares: int, price: float, timestamp: datetime):
        """更新持仓"""
        total_value = self.value + shares * price
        self.shares += shares
        if self.shares > 0:
            self.avg_price = total_value / self.shares
        self.timestamp = timestamp
        self.value = self.shares * self.avg_price


class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, name: str, params: Optional[Dict[str, Any]] = None):
        self.name = name
        self.params = params or {}
        self.positions: Dict[str, Position] = {}
        self.cash = 100000.0  # 初始资金
        self.initial_cash = 100000.0
        self.commission_rate = 0.0003  # 手续费率
        logger.info(f"策略初始化: {name}, 参数: {params}")
    
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> int:
        """
        生成交易信号
        Args:
            data: 包含OHLCV数据的DataFrame
        Returns:
            Signal.BUY, Signal.SELL, 或 Signal.HOLD
        """
        pass
    
    def on_bar(self, symbol: str, bar: pd.Series) -> int:
        """
        处理新的K线数据
        Args:
            symbol: 股票代码
            bar: 当前K线数据
        Returns:
            交易信号
        """
        # 子类可以重写此方法来处理单根K线
        return Signal.HOLD
    
    def calculate_position_size(self, symbol: str, signal: int, price: float) -> int:
        """
        计算开仓数量
        Args:
            symbol: 股票代码
            signal: 交易信号
            price: 当前价格
        Returns:
            交易数量（股）
        """
        if signal == Signal.BUY:
            # 使用可用现金的一定比例买入
            invest_ratio = self.params.get('invest_ratio', 0.5)
            max_invest = self.cash * invest_ratio
            shares = int(max_invest / price / 100) * 100  # A股以100股为单位
            return shares
        elif signal == Signal.SELL:
            # 卖出全部持仓
            if symbol in self.positions:
                return -self.positions[symbol].shares
        return 0
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """
        计算投资组合总价值
        Args:
            current_prices: 当前各股票价格
        Returns:
            总价值
        """
        position_value = sum(
            pos.shares * current_prices.get(symbol, pos.avg_price)
            for symbol, pos in self.positions.items()
        )
        return self.cash + position_value
    
    def reset(self):
        """重置策略状态"""
        self.positions = {}
        self.cash = self.initial_cash


class TechnicalIndicators:
    """技术指标计算工具类"""
    
    @staticmethod
    def SMA(data: pd.Series, period: int) -> pd.Series:
        """简单移动平均"""
        return data.rolling(window=period).mean()
    
    @staticmethod
    def EMA(data: pd.Series, period: int) -> pd.Series:
        """指数移动平均"""
        return data.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def RSI(data: pd.Series, period: int = 14) -> pd.Series:
        """相对强弱指标"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def MACD(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
        """MACD指标"""
        ema_fast = TechnicalIndicators.EMA(data, fast)
        ema_slow = TechnicalIndicators.EMA(data, slow)
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.EMA(macd_line, signal)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    @staticmethod
    def BOLL(data: pd.Series, period: int = 20, std_dev: float = 2.0) -> tuple:
        """布林带"""
        sma = TechnicalIndicators.SMA(data, period)
        std = data.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, sma, lower
    
    @staticmethod
    def ATR(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """平均真实波幅"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
    
    @staticmethod
    def KDJ(high: pd.Series, low: pd.Series, close: pd.Series, 
            n: int = 9, m1: int = 3, m2: int = 3) -> tuple:
        """KDJ指标"""
        llv = low.rolling(window=n).min()
        hhv = high.rolling(window=n).max()
        rsv = (close - llv) / (hhv - llv) * 100
        k = rsv.ewm(com=m1-1, adjust=False).mean()
        d = k.ewm(com=m2-1, adjust=False).mean()
        j = 3 * k - 2 * d
        return k, d, j


class MAStrategy(BaseStrategy):
    """双均线策略示例"""
    
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        default_params = {
            'fast_period': 5,
            'slow_period': 20,
            'invest_ratio': 0.5
        }
        if params:
            default_params.update(params)
        super().__init__("双均线策略", default_params)
    
    def generate_signal(self, data: pd.DataFrame) -> int:
        """
        双均线策略信号生成
        当快线上穿慢线时买入，下穿时卖出
        """
        if len(data) < self.params['slow_period']:
            return Signal.HOLD
        
        fast_ma = TechnicalIndicators.SMA(data['close'], self.params['fast_period'])
        slow_ma = TechnicalIndicators.SMA(data['close'], self.params['slow_period'])
        
        # 当前值和前一个值
        current_fast = fast_ma.iloc[-1]
        current_slow = slow_ma.iloc[-1]
        prev_fast = fast_ma.iloc[-2]
        prev_slow = slow_ma.iloc[-2]
        
        # 金叉：买入信号
        if prev_fast <= prev_slow and current_fast > current_slow:
            return Signal.BUY
        
        # 死叉：卖出信号
        if prev_fast >= prev_slow and current_fast < current_slow:
            return Signal.SELL
        
        return Signal.HOLD


class RSIStrategy(BaseStrategy):
    """RSI策略示例"""
    
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        default_params = {
            'rsi_period': 14,
            'oversold': 30,
            'overbought': 70,
            'invest_ratio': 0.5
        }
        if params:
            default_params.update(params)
        super().__init__("RSI策略", default_params)
    
    def generate_signal(self, data: pd.DataFrame) -> int:
        """
        RSI策略信号生成
        RSI < oversold 时买入，RSI > overbought 时卖出
        """
        if len(data) < self.params['rsi_period'] + 1:
            return Signal.HOLD
        
        rsi = TechnicalIndicators.RSI(data['close'], self.params['rsi_period'])
        current_rsi = rsi.iloc[-1]
        
        if current_rsi < self.params['oversold']:
            return Signal.BUY
        elif current_rsi > self.params['overbought']:
            return Signal.SELL
        
        return Signal.HOLD
