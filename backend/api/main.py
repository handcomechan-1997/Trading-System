"""
FastAPI后端主应用
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
from typing import List, Optional
from loguru import logger

from backend.data.data_source import DataManager
from backend.strategy.base_strategy import MAStrategy, RSIStrategy
from backend.backtest.backtest_engine import BacktestEngine
from backend.ai.deepseek_advisor import DeepSeekAdvisor
from backend.models.data_models import StockInfo
from backend.models.strategy_models import BacktestResult, StrategyConfig
from backend.models.ai_models import AIAnalysisRequest, AIAnalysisResponse
from config.config import settings

# 创建FastAPI应用
app = FastAPI(
    title="A股量化交易系统",
    description="支持策略回测、AI投资建议的A股交易系统",
    version="1.0.0"
)

# 挂载静态文件目录
frontend_path = project_root / "frontend" / "public"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局实例
data_manager: Optional[DataManager] = None
ai_advisor: Optional[DeepSeekAdvisor] = None


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    global data_manager, ai_advisor
    
    logger.info("正在初始化应用...")
    
    # 初始化数据管理器 - 优先使用Sina（新浪财经，免费且稳定）
    try:
        data_manager = DataManager("sina")
        logger.info("使用新浪财经作为主数据源（免费、稳定、快速）")
    except Exception as e:
        logger.error(f"新浪数据源初始化失败: {e}")
        # 回退到其他数据源
        try:
            if settings.TUSHARE_TOKEN:
                data_manager = DataManager("tushare", token=settings.TUSHARE_TOKEN)
                logger.info("回退到Tushare数据源")
            elif settings.AKSHARE_ENABLED:
                data_manager = DataManager("akshare")
                logger.info("回退到AKShare数据源")
            else:
                logger.warning("未配置备用数据源，请在.env中设置TUSHARE_TOKEN或启用AKSHARE")
        except Exception as e2:
            logger.error(f"备用数据源初始化失败: {e2}")
    
    # 初始化AI顾问
    try:
        ai_advisor = DeepSeekAdvisor()
    except Exception as e:
        logger.error(f"AI顾问初始化失败: {e}")
    
    logger.info("应用初始化完成")


@app.get("/")
async def root():
    """根路径 - 返回Web界面"""
    return FileResponse(str(frontend_path / "index.html"))


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "data_source": data_manager is not None,
        "ai_advisor": ai_advisor is not None and ai_advisor.client is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/stocks", response_model=List[StockInfo])
async def get_stock_list(limit: int = 100):
    """获取股票列表"""
    if not data_manager:
        raise HTTPException(status_code=503, detail="数据源未初始化")
    
    try:
        df = data_manager.get_stock_list()
        stocks = []
        for _, row in df.head(limit).iterrows():
            if data_manager.source_type == "tushare":
                stocks.append(StockInfo(
                    symbol=row.get('ts_code', ''),
                    name=row.get('name', ''),
                    industry=row.get('industry', ''),
                    market=row.get('market', ''),
                    list_date=row.get('list_date', '')
                ))
            else:  # akshare
                stocks.append(StockInfo(
                    symbol=row.get('code', ''),
                    name=row.get('name', ''),
                    industry=None,
                    market=None,
                    list_date=None
                ))
        return stocks
    except Exception as e:
        logger.error(f"获取股票列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stocks/{symbol}/data")
async def get_stock_data(
    symbol: str,
    start_date: str,
    end_date: str
):
    """获取股票历史数据"""
    if not data_manager:
        raise HTTPException(status_code=503, detail="数据源未初始化")
    
    try:
        df = data_manager.get_daily_data(symbol, start_date, end_date)
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取股票数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/backtest")
async def run_backtest(config: StrategyConfig, symbol: str, start_date: str, end_date: str):
    """运行回测"""
    if not data_manager:
        raise HTTPException(status_code=503, detail="数据源未初始化")
    
    try:
        # 获取数据
        data = data_manager.get_daily_data(symbol, start_date, end_date)
        
        # 创建策略
        if config.strategy_type == "ma":
            strategy = MAStrategy(config.params)
        elif config.strategy_type == "rsi":
            strategy = RSIStrategy(config.params)
        else:
            raise HTTPException(status_code=400, detail=f"不支持的策略类型: {config.strategy_type}")
        
        # 运行回测
        engine = BacktestEngine(
            strategy=strategy,
            data=data,
            initial_capital=config.initial_capital,
            commission_rate=config.commission_rate
        )
        result = engine.run(symbol)
        
        # 添加价格数据用于绘图
        price_data = data[['trade_date', 'close']].copy()
        price_data['trade_date'] = price_data['trade_date'].astype(str)
        
        # 构建返回结果
        return {
            **result.dict(),
            "price_data": price_data.to_dict('records')
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"回测失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/analyze", response_model=AIAnalysisResponse)
async def ai_analyze(request: AIAnalysisRequest):
    """AI分析"""
    if not ai_advisor:
        raise HTTPException(status_code=503, detail="AI顾问未初始化")
    
    if not ai_advisor.client:
        raise HTTPException(status_code=503, detail="DeepSeek API未配置")
    
    try:
        if request.analysis_type == "stock":
            # 获取股票数据
            if not data_manager:
                raise HTTPException(status_code=503, detail="数据源未初始化")
            
            # 缩短时间范围以提高成功率（最近1个月数据）
            end_date = datetime.now().strftime('%Y%m%d')
            from datetime import timedelta
            start_datetime = datetime.now() - timedelta(days=30)
            start_date = start_datetime.strftime('%Y%m%d')
            
            logger.info(f"正在获取{request.symbol}的数据: {start_date} - {end_date}")
            
            try:
                stock_data = data_manager.get_daily_data(request.symbol, start_date, end_date)
                
                if stock_data.empty:
                    raise HTTPException(status_code=404, detail=f"无法获取股票 {request.symbol} 的数据，请检查股票代码是否正确")
                
                logger.info(f"成功获取{len(stock_data)}条数据")
                
            except Exception as data_error:
                logger.error(f"数据获取失败: {data_error}")
                raise HTTPException(status_code=500, detail=f"数据获取失败: {str(data_error)}。AKShare服务可能不稳定，请稍后重试")
            
            indicators = request.context.get('indicators') if request.context else None
            
            logger.info("正在调用DeepSeek AI分析...")
            advice = ai_advisor.analyze_stock(request.symbol, stock_data, indicators)
            
        elif request.analysis_type == "strategy":
            backtest_results = request.context.get('backtest_results', {})
            current_params = request.context.get('current_params', {})
            strategy_name = request.context.get('strategy_name', '未知策略')
            
            advice = ai_advisor.optimize_strategy(strategy_name, backtest_results, current_params)
            
        else:
            raise HTTPException(status_code=400, detail=f"不支持的分析类型: {request.analysis_type}")
        
        return AIAnalysisResponse(
            symbol=request.symbol if request.analysis_type == "stock" else None,
            analysis_type=request.analysis_type,
            advice=advice,
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/set-key")
async def set_deepseek_key(api_key: str):
    """设置DeepSeek API密钥"""
    global ai_advisor
    
    try:
        if not ai_advisor:
            ai_advisor = DeepSeekAdvisor(api_key)
        else:
            ai_advisor.set_api_key(api_key)
        
        return {"message": "API密钥设置成功"}
    except Exception as e:
        logger.error(f"设置API密钥失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
