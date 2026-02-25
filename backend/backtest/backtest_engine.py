"""
回测引擎
"""
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
import numpy as np
from loguru import logger

from backend.strategy.base_strategy import BaseStrategy, Signal, Position
from backend.models.strategy_models import TradeRecord, BacktestResult


class BacktestEngine:
    """回测引擎"""
    
    def __init__(
        self,
        strategy: BaseStrategy,
        data: pd.DataFrame,
        initial_capital: float = 100000.0,
        commission_rate: float = 0.0003,
        slippage: float = 0.0
    ):
        """
        初始化回测引擎
        Args:
            strategy: 交易策略
            data: 历史数据
            initial_capital: 初始资金
            commission_rate: 手续费率
            slippage: 滑点
        """
        self.strategy = strategy
        self.data = data.copy()
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage = slippage
        
        # 回测状态
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.trades: List[TradeRecord] = []
        self.equity_curve: List[float] = []
        self.dates: List[datetime] = []
        
        # 更新策略的初始资金
        self.strategy.initial_cash = initial_capital
        self.strategy.cash = initial_capital
        self.strategy.commission_rate = commission_rate
        
        logger.info(f"回测引擎初始化完成: {strategy.name}")
    
    def run(self, symbol: str) -> BacktestResult:
        """
        运行回测
        Args:
            symbol: 股票代码
        Returns:
            回测结果
        """
        logger.info(f"开始回测: {symbol}")
        
        # 重置状态
        self.cash = self.initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []
        self.dates = []
        self.strategy.reset()
        
        # 逐条处理数据
        for idx in range(len(self.data)):
            # 获取当前和历史数据
            current_data = self.data.iloc[:idx+1]
            current_bar = self.data.iloc[idx]
            
            # 生成交易信号
            signal = self.strategy.generate_signal(current_data)
            
            # 执行交易
            if signal != Signal.HOLD:
                self._execute_trade(symbol, signal, current_bar)
            
            # 记录净值
            current_price = current_bar['close']
            portfolio_value = self._calculate_portfolio_value({symbol: current_price})
            self.equity_curve.append(portfolio_value)
            self.dates.append(current_bar['trade_date'])
        
        # 计算回测指标
        result = self._calculate_metrics(symbol)
        logger.info(f"回测完成: {symbol}, 总收益率: {result.total_return:.2%}")
        
        return result
    
    def _execute_trade(self, symbol: str, signal: int, bar: pd.Series):
        """执行交易"""
        price = bar['close'] * (1 + self.slippage if signal == Signal.BUY else 1 - self.slippage)
        
        # 更新策略的现金和持仓信息（重要：让策略能看到实际持仓）
        self.strategy.cash = self.cash
        self.strategy.positions = self.positions
        
        # 计算交易数量
        shares = self.strategy.calculate_position_size(symbol, signal, price)
        
        if shares == 0:
            return
        
        # 计算交易成本
        trade_value = abs(shares) * price
        commission = trade_value * self.commission_rate
        
        # 买入
        if signal == Signal.BUY and shares > 0:
            total_cost = trade_value + commission
            if total_cost <= self.cash:
                self.cash -= total_cost
                
                # 更新持仓
                if symbol in self.positions:
                    self.positions[symbol].update(shares, price, bar['trade_date'])
                else:
                    self.positions[symbol] = Position(symbol, shares, price, bar['trade_date'])
                
                # 记录交易
                self._record_trade(bar['trade_date'], symbol, 'buy', price, shares, commission)
                logger.debug(f"买入: {symbol}, 价格: {price:.2f}, 数量: {shares}, 手续费: {commission:.2f}")
        
        # 卖出
        elif signal == Signal.SELL and shares < 0:
            if symbol in self.positions and self.positions[symbol].shares >= abs(shares):
                self.cash += trade_value - commission
                
                # 更新持仓
                self.positions[symbol].update(shares, price, bar['trade_date'])
                if self.positions[symbol].shares == 0:
                    del self.positions[symbol]
                
                # 记录交易
                self._record_trade(bar['trade_date'], symbol, 'sell', price, abs(shares), commission)
                logger.debug(f"卖出: {symbol}, 价格: {price:.2f}, 数量: {abs(shares)}, 手续费: {commission:.2f}")
    
    def _record_trade(
        self,
        timestamp: datetime,
        symbol: str,
        action: str,
        price: float,
        shares: int,
        commission: float
    ):
        """记录交易"""
        portfolio_value = self._calculate_portfolio_value({symbol: price})
        trade = TradeRecord(
            timestamp=timestamp,
            symbol=symbol,
            action=action,
            price=price,
            shares=shares,
            commission=commission,
            cash=self.cash,
            portfolio_value=portfolio_value
        )
        self.trades.append(trade)
    
    def _calculate_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """计算投资组合价值"""
        position_value = sum(
            pos.shares * current_prices.get(symbol, pos.avg_price)
            for symbol, pos in self.positions.items()
        )
        return self.cash + position_value
    
    def _calculate_metrics(self, symbol: str) -> BacktestResult:
        """计算回测指标"""
        equity_series = pd.Series(self.equity_curve, index=self.dates)
        
        # 总收益率
        total_return = (equity_series.iloc[-1] / self.initial_capital - 1)
        
        # 年化收益率
        days = (self.dates[-1] - self.dates[0]).days
        years = days / 365.25
        annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        # 最大回撤
        cummax = equity_series.cummax()
        drawdown = (equity_series - cummax) / cummax
        max_drawdown = drawdown.min()
        
        # 夏普比率
        returns = equity_series.pct_change().dropna()
        sharpe_ratio = (returns.mean() / returns.std() * np.sqrt(252)) if len(returns) > 0 and returns.std() > 0 else 0
        
        # 胜率
        win_trades = 0
        total_trades = 0
        for i in range(0, len(self.trades) - 1, 2):
            if i + 1 < len(self.trades):
                buy_trade = self.trades[i]
                sell_trade = self.trades[i + 1]
                if buy_trade.action == 'buy' and sell_trade.action == 'sell':
                    total_trades += 1
                    profit = (sell_trade.price - buy_trade.price) * buy_trade.shares - buy_trade.commission - sell_trade.commission
                    if profit > 0:
                        win_trades += 1
        
        win_rate = win_trades / total_trades if total_trades > 0 else 0
        
        return BacktestResult(
            strategy_name=self.strategy.name,
            start_date=self.dates[0].strftime('%Y-%m-%d'),
            end_date=self.dates[-1].strftime('%Y-%m-%d'),
            initial_capital=self.initial_capital,
            final_capital=equity_series.iloc[-1],
            total_return=total_return,
            annual_return=annual_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            win_rate=win_rate,
            total_trades=len(self.trades),
            trades=self.trades
        )
