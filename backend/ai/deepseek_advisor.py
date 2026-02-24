"""
DeepSeek AI投资建议服务
"""
from typing import Optional, List, Dict, Any
from openai import OpenAI
from loguru import logger
import pandas as pd

from config.config import settings


class DeepSeekAdvisor:
    """DeepSeek AI投资顾问"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化DeepSeek顾问
        Args:
            api_key: DeepSeek API密钥，如果不提供则从配置中读取
        """
        self.api_key = api_key or settings.DEEPSEEK_API_KEY
        if not self.api_key:
            logger.warning("DeepSeek API密钥未设置，请在.env文件中配置DEEPSEEK_API_KEY")
            self.client = None
        else:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=settings.DEEPSEEK_API_BASE
            )
            logger.info("DeepSeek AI顾问初始化成功")
    
    def analyze_stock(
        self,
        symbol: str,
        stock_data: pd.DataFrame,
        indicators: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        分析股票并给出投资建议
        Args:
            symbol: 股票代码
            stock_data: 股票历史数据
            indicators: 技术指标数据
        Returns:
            AI生成的投资建议
        """
        if not self.client:
            return "DeepSeek API未配置，无法提供投资建议"
        
        try:
            # 构建分析提示
            prompt = self._build_analysis_prompt(symbol, stock_data, indicators)
            
            # 调用DeepSeek API
            response = self.client.chat.completions.create(
                model=settings.DEEPSEEK_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位专业的A股市场分析师，擅长技术分析和基本面分析。请基于提供的数据给出客观、专业的投资建议。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000,
                timeout=30.0
            )
            
            advice = response.choices[0].message.content
            logger.info(f"成功生成{symbol}的投资建议")
            return advice
            
        except Exception as e:
            logger.error(f"调用DeepSeek API失败: {e}")
            import traceback
            traceback.print_exc()
            return f"生成投资建议时出错: {str(e)}"
    
    def analyze_market_trend(
        self,
        market_data: Dict[str, pd.DataFrame],
        news: Optional[List[str]] = None
    ) -> str:
        """
        分析市场整体趋势
        Args:
            market_data: 多只股票或指数的数据
            news: 相关新闻（可选）
        Returns:
            市场趋势分析
        """
        if not self.client:
            return "DeepSeek API未配置，无法提供市场分析"
        
        try:
            prompt = self._build_market_prompt(market_data, news)
            
            response = self.client.chat.completions.create(
                model=settings.DEEPSEEK_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位资深的市场分析师，请基于提供的市场数据分析当前A股市场的整体趋势和投资机会。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            analysis = response.choices[0].message.content
            logger.info("成功生成市场趋势分析")
            return analysis
            
        except Exception as e:
            logger.error(f"调用DeepSeek API失败: {e}")
            return f"生成市场分析时出错: {str(e)}"
    
    def optimize_strategy(
        self,
        strategy_name: str,
        backtest_results: Dict[str, Any],
        current_params: Dict[str, Any]
    ) -> str:
        """
        策略优化建议
        Args:
            strategy_name: 策略名称
            backtest_results: 回测结果
            current_params: 当前策略参数
        Returns:
            策略优化建议
        """
        if not self.client:
            return "DeepSeek API未配置，无法提供策略优化建议"
        
        try:
            prompt = self._build_strategy_prompt(strategy_name, backtest_results, current_params)
            
            response = self.client.chat.completions.create(
                model=settings.DEEPSEEK_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位量化交易专家，请基于回测结果分析策略表现并给出优化建议。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            advice = response.choices[0].message.content
            logger.info(f"成功生成{strategy_name}的优化建议")
            return advice
            
        except Exception as e:
            logger.error(f"调用DeepSeek API失败: {e}")
            return f"生成策略优化建议时出错: {str(e)}"
    
    def _build_analysis_prompt(
        self,
        symbol: str,
        stock_data: pd.DataFrame,
        indicators: Optional[Dict[str, Any]]
    ) -> str:
        """构建股票分析提示"""
        # 获取最近的数据
        recent_data = stock_data.tail(20)
        latest = stock_data.iloc[-1]
        
        prompt = f"""请分析股票 {symbol} 的投资价值：

最近20天价格走势：
- 最新收盘价: {latest['close']:.2f}
- 最高价: {recent_data['high'].max():.2f}
- 最低价: {recent_data['low'].min():.2f}
- 平均成交量: {recent_data['volume'].mean():.0f}
- 近20日涨跌幅: {((latest['close'] / recent_data.iloc[0]['close'] - 1) * 100):.2f}%
"""
        
        if indicators:
            prompt += f"\n技术指标：\n"
            for key, value in indicators.items():
                prompt += f"- {key}: {value}\n"
        
        prompt += """
请从以下几个方面给出分析：
1. 当前价格趋势判断
2. 技术指标分析
3. 短期和中期投资建议
4. 风险提示

请给出专业、客观的建议。"""
        
        return prompt
    
    def _build_market_prompt(
        self,
        market_data: Dict[str, pd.DataFrame],
        news: Optional[List[str]]
    ) -> str:
        """构建市场分析提示"""
        prompt = "请分析当前A股市场趋势：\n\n"
        
        for symbol, data in market_data.items():
            if not data.empty:
                latest = data.iloc[-1]
                first = data.iloc[0]
                change = (latest['close'] / first['close'] - 1) * 100
                prompt += f"{symbol}: {change:+.2f}%\n"
        
        if news:
            prompt += f"\n相关新闻：\n"
            for item in news[:5]:
                prompt += f"- {item}\n"
        
        prompt += """
请分析：
1. 市场整体趋势
2. 热点板块和机会
3. 风险因素
4. 投资策略建议
"""
        return prompt
    
    def _build_strategy_prompt(
        self,
        strategy_name: str,
        backtest_results: Dict[str, Any],
        current_params: Dict[str, Any]
    ) -> str:
        """构建策略优化提示"""
        prompt = f"""请分析交易策略 "{strategy_name}" 的表现并给出优化建议：

当前参数：
{current_params}

回测结果：
- 总收益率: {backtest_results.get('total_return', 0):.2%}
- 年化收益率: {backtest_results.get('annual_return', 0):.2%}
- 最大回撤: {backtest_results.get('max_drawdown', 0):.2%}
- 夏普比率: {backtest_results.get('sharpe_ratio', 0):.2f}
- 胜率: {backtest_results.get('win_rate', 0):.2%}
- 交易次数: {backtest_results.get('total_trades', 0)}

请从以下方面给出建议：
1. 策略表现评价
2. 参数优化建议
3. 风险控制建议
4. 改进方向
"""
        return prompt
    
    def set_api_key(self, api_key: str):
        """
        设置或更新API密钥
        Args:
            api_key: 新的API密钥
        """
        self.api_key = api_key
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=settings.DEEPSEEK_API_BASE
        )
        logger.info("DeepSeek API密钥已更新")
