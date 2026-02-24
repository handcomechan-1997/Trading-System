"""
双均线策略示例
"""
from backend.data.data_source import DataManager
from backend.strategy.base_strategy import MAStrategy
from backend.backtest.backtest_engine import BacktestEngine
from loguru import logger

def main():
    """双均线策略回测示例"""
    
    # 1. 初始化数据管理器（使用AKShare）
    logger.info("初始化数据管理器...")
    data_manager = DataManager("akshare")
    
    # 2. 获取股票数据
    symbol = "000001"  # 平安银行
    start_date = "20200101"
    end_date = "20231231"
    
    logger.info(f"获取{symbol}的历史数据: {start_date} - {end_date}")
    data = data_manager.get_daily_data(symbol, start_date, end_date)
    logger.info(f"成功获取{len(data)}条数据")
    
    # 3. 创建双均线策略
    logger.info("创建双均线策略...")
    strategy = MAStrategy(params={
        'fast_period': 5,      # 5日均线
        'slow_period': 20,     # 20日均线
        'invest_ratio': 0.5    # 每次使用50%资金
    })
    
    # 4. 创建回测引擎
    logger.info("初始化回测引擎...")
    engine = BacktestEngine(
        strategy=strategy,
        data=data,
        initial_capital=100000,   # 初始资金10万
        commission_rate=0.0003,   # 万三手续费
        slippage=0.0              # 无滑点
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
    
    # 7. 输出部分交易记录
    if result.trades:
        print("\n最近5笔交易:")
        for trade in result.trades[-5:]:
            print(f"{trade.timestamp.strftime('%Y-%m-%d')} | "
                  f"{trade.action.upper():4s} | "
                  f"价格: ¥{trade.price:7.2f} | "
                  f"数量: {trade.shares:5d} | "
                  f"资金: ¥{trade.cash:,.2f}")

if __name__ == "__main__":
    main()
