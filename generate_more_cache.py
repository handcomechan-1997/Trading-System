"""
批量生成更多股票的缓存数据
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle
from pathlib import Path

# 创建data/cache目录
cache_dir = Path("/Users/handsomechen/workdir/trade/data/cache")
cache_dir.mkdir(parents=True, exist_ok=True)

def generate_realistic_stock_data(symbol: str, name: str, base_price: float, days: int = 60):
    """生成逼真的股票数据"""
    end_date = datetime.now()
    dates = pd.date_range(end=end_date, periods=days, freq='D')
    
    # 设置随机种子
    np.random.seed(hash(symbol) % 10000)
    
    # 生成价格序列
    returns = np.random.randn(days) * 0.02
    trend = np.linspace(-0.02, 0.08, days)  # 趋势
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
    
    df['high'] = df[['high', 'close']].max(axis=1)
    df['low'] = df[['low', 'close']].min(axis=1)
    df['amount'] = df['close'] * df['volume']
    
    return df

# 扩展股票列表
stocks = [
    # 银行
    ('000001', '平安银行', 10.5),
    ('600000', '浦发银行', 8.2),
    ('600036', '招商银行', 32.5),
    ('601398', '工商银行', 5.8),
    ('601939', '建设银行', 6.9),
    
    # 白酒
    ('600519', '贵州茅台', 1680.0),
    ('000858', '五粮液', 45.3),
    ('000568', '泸州老窖', 180.0),
    
    # 地产
    ('000002', '万科A', 18.6),
    ('000001', '平安银行', 10.5),
    
    # 科技
    ('600276', '恒瑞医药', 52.0),
    ('300059', '东方财富', 18.5),
    ('002475', '立讯精密', 28.0),
    
    # 其他
    ('601318', '中国平安', 45.0),
    ('600887', '伊利股份', 28.5),
]

print("正在生成股票缓存数据...\n")

for symbol, name, base_price in stocks:
    try:
        data = generate_realistic_stock_data(symbol, name, base_price)
        cache_file = cache_dir / f"{symbol}.pkl"
        
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f)
        
        change_pct = ((data['close'].iloc[-1] / data['close'].iloc[0] - 1) * 100)
        print(f"✓ {symbol:6s} {name:10s} | 最新价: {data['close'].iloc[-1]:8.2f} | 涨跌幅: {change_pct:6.2f}%")
    except Exception as e:
        print(f"✗ {symbol:6s} {name:10s} | 失败: {e}")

print(f"\n已生成 {len(stocks)} 只股票的缓存数据！")
print(f"缓存目录: {cache_dir}")
