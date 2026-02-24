"""
AI投资建议示例
"""
from backend.ai.deepseek_advisor import DeepSeekAdvisor
from backend.data.data_source import DataManager
from backend.strategy.base_strategy import TechnicalIndicators
from loguru import logger
from datetime import datetime, timedelta

def main():
    """AI投资建议示例"""
    
    # 1. 初始化
    logger.info("初始化系统...")
    data_manager = DataManager("akshare")
    
    # 注意: 需要先设置DEEPSEEK_API_KEY环境变量
    advisor = DeepSeekAdvisor()
    
    if not advisor.client:
        print("\n请先配置DeepSeek API密钥:")
        print("1. 在.env文件中设置DEEPSEEK_API_KEY")
        print("2. 或通过代码设置: advisor.set_api_key('your_key')")
        return
    
    # 2. 获取股票数据
    symbol = "000001"
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')
    
    logger.info(f"获取{symbol}的数据...")
    stock_data = data_manager.get_daily_data(symbol, start_date, end_date)
    
    # 3. 计算技术指标
    logger.info("计算技术指标...")
    rsi = TechnicalIndicators.RSI(stock_data['close'], 14)
    macd_line, signal_line, histogram = TechnicalIndicators.MACD(stock_data['close'])
    upper, middle, lower = TechnicalIndicators.BOLL(stock_data['close'])
    
    indicators = {
        'RSI': f"{rsi.iloc[-1]:.2f}",
        'MACD': "金叉" if histogram.iloc[-1] > 0 else "死叉",
        'MACD值': f"{macd_line.iloc[-1]:.2f}",
        '布林带位置': "上轨" if stock_data['close'].iloc[-1] > upper.iloc[-1] else 
                       "下轨" if stock_data['close'].iloc[-1] < lower.iloc[-1] else "中轨"
    }
    
    # 4. 获取AI建议
    logger.info("请求AI分析...")
    print("\n" + "="*50)
    print("AI投资建议")
    print("="*50)
    
    advice = advisor.analyze_stock(
        symbol=symbol,
        stock_data=stock_data,
        indicators=indicators
    )
    
    print(advice)
    print("="*50)

if __name__ == "__main__":
    main()
