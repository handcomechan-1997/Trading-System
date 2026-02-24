"""
AI模型定义
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class AIAnalysisRequest(BaseModel):
    """AI分析请求"""
    symbol: str = Field(..., description="股票代码")
    analysis_type: str = Field(..., description="分析类型: stock/market/strategy")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文数据")


class AIAnalysisResponse(BaseModel):
    """AI分析响应"""
    symbol: Optional[str] = Field(None, description="股票代码")
    analysis_type: str = Field(..., description="分析类型")
    advice: str = Field(..., description="投资建议")
    timestamp: str = Field(..., description="生成时间")
