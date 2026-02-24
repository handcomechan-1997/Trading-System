"""
RSI策略示例
"""
from backend.data.data_source import DataManager
from backend.strategy.base_strategy import RSIStrategy
from backend.backtest.backtest_engine import BacktestEngine
from loguru import logger

def main():
    """RSI策略回测示例"""
    
    # 1. 初始化数据管理器
    logger.info("初始化数据管理器...")
    data_manager = DataManager("akshare")
    
    # 2. 获取股票数据
    symbol = "600519"  # 贵州茅台
    start_date = "20200101"
    end_date = "20231231"
    
    logger.info(f"获取{symbol}的历史数据: {start_date} - {end_date}")
    data = data_manager.get_daily_data(symbol, start_date, end_date)
    logger.info(f"成功获取{len(data)}条数据")
    
    # 3. 创建RSI策略
    logger.info("创建RSI策略...")
    strategy = RSIStrategy(params={
        'rsi_period': 14,      # 14日RSI
        'oversold': 30,        # 超卖阈值
        'overbought': 70,      # 超买阈值
        'invest_ratio': 0.5    # 每次使用50%资金
    })
    
    # 4. 创建回测引擎
    logger.info("初始化回测引擎...")
    engine = BacktestEngine(
        strategy=strategy,
        data=data,
        initial_capital=100000,
        commission_rate=0.0003
    )
    
    # 5. 运行回测
    logger.info("开始回测...")
    result = engine.run(symbol)
    
    # 6. 输出结果
    print("\n" + "="*50)
    print("回测结果")
    print("="*50)
    print(f"策略名称: {result.strategy_name}")
    print(f"回测周期: {result.start_date} - {result.end_date}")
    print(f"初始资金: ¥{result.initial_capital:,.2f}")
    print(f"最终资金: ¥{result.final_capital:,.2f}")
    print(f"总收益率: {result.total_return:.2%}")
    print(f"年化收益率: {result.annual_return:.2%}")
    print(f"最大回撤: {result.max_drawdown:.2%}")
    print(f"夏普比率: {result.sharpe_ratio:.2f}")
    print(f"胜率: {result.win_rate:.2%}")
    print(f"交易次数: {result.total_trades}")
    print("="*50)

if __name__ == "__main__":
    main()
