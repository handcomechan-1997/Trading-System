"""
策略模型定义
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class StrategyConfig(BaseModel):
    """策略配置"""
    name: str = Field(..., description="策略名称")
    strategy_type: str = Field(..., description="策略类型")
    params: Dict[str, Any] = Field(default_factory=dict, description="策略参数")
    initial_capital: float = Field(100000.0, description="初始资金")
    commission_rate: float = Field(0.0003, description="手续费率")


class TradeRecord(BaseModel):
    """交易记录"""
    timestamp: datetime = Field(..., description="交易时间")
    symbol: str = Field(..., description="股票代码")
    action: str = Field(..., description="操作类型: buy/sell")
    price: float = Field(..., description="成交价格")
    shares: int = Field(..., description="成交数量")
    commission: float = Field(..., description="手续费")
    cash: float = Field(..., description="剩余现金")
    portfolio_value: float = Field(..., description="组合总价值")


class BacktestResult(BaseModel):
    """回测结果"""
    strategy_name: str = Field(..., description="策略名称")
    start_date: str = Field(..., description="回测开始日期")
    end_date: str = Field(..., description="回测结束日期")
    initial_capital: float = Field(..., description="初始资金")
    final_capital: float = Field(..., description="最终资金")
    total_return: float = Field(..., description="总收益率")
    annual_return: float = Field(..., description="年化收益率")
    max_drawdown: float = Field(..., description="最大回撤")
    sharpe_ratio: float = Field(..., description="夏普比率")
    win_rate: float = Field(..., description="胜率")
    total_trades: int = Field(..., description="总交易次数")
    trades: List[TradeRecord] = Field(default_factory=list, description="交易记录")
