"""
自定义策略引擎 - 支持可视化规则构建
"""
from typing import Dict, List, Any, Optional
import pandas as pd
from loguru import logger

from backend.strategy.base_strategy import BaseStrategy, Signal, TechnicalIndicators


class Condition:
    """条件类 - 表示单个判断条件"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化条件
        Args:
            config: 条件配置
                {
                    "indicator": "MA",  # 指标名称
                    "params": {"period": 5},  # 指标参数
                    "operator": ">",  # 比较运算符
                    "compare_to": "MA",  # 比较对象（另一个指标或固定值）
                    "compare_params": {"period": 20}  # 比较对象参数
                }
        """
        self.indicator = config.get('indicator')
        self.params = config.get('params', {})
        self.operator = config.get('operator')
        self.compare_to = config.get('compare_to')
        self.compare_params = config.get('compare_params', {})
    
    def evaluate(self, data: pd.DataFrame) -> bool:
        """
        评估条件是否满足
        Args:
            data: 历史数据
        Returns:
            True/False
        """
        try:
            # 计算左侧指标值
            left_value = self._calculate_indicator(data, self.indicator, self.params)
            
            # 计算右侧比较值
            if isinstance(self.compare_to, (int, float)):
                right_value = self.compare_to
            else:
                right_value = self._calculate_indicator(data, self.compare_to, self.compare_params)
            
            # 比较
            return self._compare(left_value, right_value, self.operator)
        except Exception as e:
            logger.warning(f"条件评估失败: {e}")
            return False
    
    def _calculate_indicator(self, data: pd.DataFrame, indicator: str, params: Dict) -> float:
        """计算技术指标"""
        close = data['close']
        
        if indicator == 'MA':
            period = params.get('period', 5)
            ma = TechnicalIndicators.SMA(close, period)
            return ma.iloc[-1]
        
        elif indicator == 'EMA':
            period = params.get('period', 5)
            ema = TechnicalIndicators.EMA(close, period)
            return ema.iloc[-1]
        
        elif indicator == 'RSI':
            period = params.get('period', 14)
            rsi = TechnicalIndicators.RSI(close, period)
            return rsi.iloc[-1]
        
        elif indicator == 'MACD':
            fast = params.get('fast', 12)
            slow = params.get('slow', 26)
            signal = params.get('signal', 9)
            macd_line, signal_line, histogram = TechnicalIndicators.MACD(close, fast, slow, signal)
            
            # 返回MACD线或信号线
            if params.get('line') == 'signal':
                return signal_line.iloc[-1]
            elif params.get('line') == 'histogram':
                return histogram.iloc[-1]
            else:
                return macd_line.iloc[-1]
        
        elif indicator == 'BOLL':
            period = params.get('period', 20)
            std_dev = params.get('std_dev', 2.0)
            upper, middle, lower = TechnicalIndicators.BOLL(close, period, std_dev)
            
            # 返回上轨、中轨或下轨
            if params.get('band') == 'upper':
                return upper.iloc[-1]
            elif params.get('band') == 'lower':
                return lower.iloc[-1]
            else:
                return middle.iloc[-1]
        
        elif indicator == 'KDJ':
            high = data['high']
            low = data['low']
            n = params.get('n', 9)
            m1 = params.get('m1', 3)
            m2 = params.get('m2', 3)
            k, d, j = TechnicalIndicators.KDJ(high, low, close, n, m1, m2)
            
            # 返回K线、D线或J线
            if params.get('line') == 'd':
                return d.iloc[-1]
            elif params.get('line') == 'j':
                return j.iloc[-1]
            else:
                return k.iloc[-1]
        
        elif indicator == 'PRICE':
            return close.iloc[-1]
        
        elif indicator == 'VOLUME':
            return data['volume'].iloc[-1]
        
        elif indicator == 'VOLUME_MA':
            period = params.get('period', 5)
            volume_ma = data['volume'].rolling(window=period).mean()
            return volume_ma.iloc[-1]
        
        else:
            raise ValueError(f"不支持的指标: {indicator}")
    
    def _compare(self, left: float, right: float, operator: str) -> bool:
        """比较两个值"""
        if operator == '>':
            return left > right
        elif operator == '>=':
            return left >= right
        elif operator == '<':
            return left < right
        elif operator == '<=':
            return left <= right
        elif operator == '==':
            return abs(left - right) < 1e-6
        elif operator == '!=':
            return abs(left - right) >= 1e-6
        else:
            raise ValueError(f"不支持的运算符: {operator}")


class Rule:
    """规则类 - 表示买入或卖出规则"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化规则
        Args:
            config: 规则配置
                {
                    "name": "金叉买入",
                    "conditions": [...],  # 条件列表
                    "logic": "AND"  # 条件之间的逻辑关系: AND/OR
                }
        """
        self.name = config.get('name', '未命名规则')
        self.conditions = [Condition(c) for c in config.get('conditions', [])]
        self.logic = config.get('logic', 'AND')
    
    def evaluate(self, data: pd.DataFrame) -> bool:
        """
        评估规则是否触发
        Args:
            data: 历史数据
        Returns:
            True/False
        """
        if not self.conditions:
            return False
        
        results = [cond.evaluate(data) for cond in self.conditions]
        
        if self.logic == 'AND':
            return all(results)
        elif self.logic == 'OR':
            return any(results)
        else:
            return False


class CrossCondition:
    """交叉条件 - 特殊的条件类型，用于检测指标交叉"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化交叉条件
        Args:
            config: 配置
                {
                    "indicator1": "MA",
                    "params1": {"period": 5},
                    "indicator2": "MA",
                    "params2": {"period": 20},
                    "cross_type": "golden"  # golden(金叉) 或 death(死叉)
                }
        """
        self.indicator1 = config.get('indicator1')
        self.params1 = config.get('params1', {})
        self.indicator2 = config.get('indicator2')
        self.params2 = config.get('params2', {})
        self.cross_type = config.get('cross_type')
    
    def evaluate(self, data: pd.DataFrame) -> bool:
        """检测是否发生交叉"""
        if len(data) < 2:
            return False
        
        try:
            cond = Condition({'indicator': self.indicator1, 'params': self.params1})
            
            # 计算当前值
            val1_current = cond._calculate_indicator(data, self.indicator1, self.params1)
            val2_current = cond._calculate_indicator(data, self.indicator2, self.params2)
            
            # 计算前一个值
            data_prev = data.iloc[:-1]
            val1_prev = cond._calculate_indicator(data_prev, self.indicator1, self.params1)
            val2_prev = cond._calculate_indicator(data_prev, self.indicator2, self.params2)
            
            # 检测交叉
            if self.cross_type == 'golden':
                # 金叉：从下方上穿
                return val1_prev <= val2_prev and val1_current > val2_current
            elif self.cross_type == 'death':
                # 死叉：从上方下穿
                return val1_prev >= val2_prev and val1_current < val2_current
            else:
                return False
        except Exception as e:
            logger.warning(f"交叉条件评估失败: {e}")
            return False


class CustomStrategy(BaseStrategy):
    """自定义策略 - 基于规则引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化自定义策略
        Args:
            config: 策略配置
                {
                    "name": "我的策略",
                    "buy_rules": [...],  # 买入规则列表
                    "sell_rules": [...],  # 卖出规则列表
                    "params": {"invest_ratio": 0.5}
                }
        """
        name = config.get('name', '自定义策略')
        params = config.get('params', {})
        super().__init__(name, params)
        
        # 解析买入规则
        self.buy_rules = []
        for rule_config in config.get('buy_rules', []):
            if rule_config.get('type') == 'cross':
                # 交叉规则
                self.buy_rules.append(CrossCondition(rule_config))
            else:
                # 普通规则
                self.buy_rules.append(Rule(rule_config))
        
        # 解析卖出规则
        self.sell_rules = []
        for rule_config in config.get('sell_rules', []):
            if rule_config.get('type') == 'cross':
                self.sell_rules.append(CrossCondition(rule_config))
            else:
                self.sell_rules.append(Rule(rule_config))
        
        logger.info(f"自定义策略初始化完成: {name}, 买入规则数: {len(self.buy_rules)}, 卖出规则数: {len(self.sell_rules)}")
    
    def generate_signal(self, data: pd.DataFrame) -> int:
        """
        生成交易信号
        Args:
            data: 历史数据
        Returns:
            Signal.BUY, Signal.SELL, 或 Signal.HOLD
        """
        # 检查买入规则
        for rule in self.buy_rules:
            if rule.evaluate(data):
                logger.debug(f"触发买入规则: {getattr(rule, 'name', 'cross')}")
                return Signal.BUY
        
        # 检查卖出规则
        for rule in self.sell_rules:
            if rule.evaluate(data):
                logger.debug(f"触发卖出规则: {getattr(rule, 'name', 'cross')}")
                return Signal.SELL
        
        return Signal.HOLD
