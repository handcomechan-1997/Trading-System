"""
数据模型定义
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class StockInfo(BaseModel):
    """股票基本信息"""
    symbol: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    industry: Optional[str] = Field(None, description="所属行业")
    market: Optional[str] = Field(None, description="市场类型")
    list_date: Optional[str] = Field(None, description="上市日期")


class OHLCV(BaseModel):
    """OHLCV数据模型"""
    trade_date: datetime = Field(..., description="交易日期")
    open: float = Field(..., description="开盘价")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    close: float = Field(..., description="收盘价")
    volume: float = Field(..., description="成交量")
    amount: Optional[float] = Field(None, description="成交额")


class RealtimeQuote(BaseModel):
    """实时行情"""
    symbol: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    current_price: float = Field(..., description="当前价")
    change_pct: float = Field(..., description="涨跌幅")
    volume: float = Field(..., description="成交量")
    amount: float = Field(..., description="成交额")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    open: float = Field(..., description="开盘价")
    pre_close: float = Field(..., description="昨收价")
