"""
创建演示用的本地数据缓存
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle
from pathlib import Path

# 创建data/cache目录
cache_dir = Path("/Users/handsomechen/workdir/trade/data/cache")
cache_dir.mkdir(parents=True, exist_ok=True)

# 生成模拟的真实数据（基于真实的A股股票特征）
def generate_realistic_stock_data(symbol: str, days: int = 60):
    """生成逼真的股票数据"""
    end_date = datetime.now()
    dates = pd.date_range(end=end_date, periods=days, freq='D')
    
    # 设置随机种子以获得可重复的数据
    np.random.seed(hash(symbol) % 10000)
    
    # 基础价格
    base_prices = {
        '000001': 10.5,   # 平安银行
        '600000': 8.2,    # 浦发银行
        '000002': 18.6,   # 万科A
        '600519': 1680.0, # 贵州茅台
        '000858': 45.3,   # 五粮液
    }
    
    base_price = base_prices.get(symbol, 15.0)
    
    # 生成价格序列（随机游走 + 趋势）
    returns = np.random.randn(days) * 0.02  # 2%的日波动
    trend = np.linspace(0, 0.05, days)  # 轻微上升趋势
    cumulative_returns = np.cumsum(returns + trend / days)
    
    close_prices = base_price * (1 + cumulative_returns)
    
    # 生成OHLC
    df = pd.DataFrame({
        'trade_date': dates,
        'open': close_prices * (1 + np.random.randn(days) * 0.005),
        'high': close_prices * (1 + abs(np.random.randn(days)) * 0.015),
        'low': close_prices * (1 - abs(np.random.randn(days)) * 0.015),
        'close': close_prices,
        'volume': np.random.randint(5000000, 50000000, days),
    })
    
    # 确保high >= close >= low
    df['high'] = df[['high', 'close']].max(axis=1)
    df['low'] = df[['low', 'close']].min(axis=1)
    df['amount'] = df['close'] * df['volume']
    
    return df

# 生成常用股票的缓存数据
symbols = ['000001', '600000', '000002', '600519', '000858']

for symbol in symbols:
    data = generate_realistic_stock_data(symbol)
    cache_file = cache_dir / f"{symbol}.pkl"
    
    with open(cache_file, 'wb') as f:
        pickle.dump(data, f)
    
    print(f"✓ 已生成 {symbol} 的缓存数据 ({len(data)} 条记录)")
    print(f"  最新价: {data['close'].iloc[-1]:.2f}")
    print(f"  涨跌幅: {((data['close'].iloc[-1] / data['close'].iloc[0] - 1) * 100):.2f}%")
    print()

print("所有缓存数据已生成！")
