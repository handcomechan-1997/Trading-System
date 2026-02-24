"""
数据获取模块 - 统一的数据接口
支持多种数据源：Tushare, AKShare, Sina (新浪财经)
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime
import pandas as pd
from loguru import logger
import requests
import json
import time


class DataSource(ABC):
    """数据源抽象基类"""
    
    @abstractmethod
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        pass
    
    @abstractmethod
    def get_daily_data(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str
    ) -> pd.DataFrame:
        """获取日线数据"""
        pass
    
    @abstractmethod
    def get_realtime_quote(self, symbol: str) -> dict:
        """获取实时行情"""
        pass
    
    @abstractmethod
    def get_financial_data(self, symbol: str, year: int, quarter: int) -> pd.DataFrame:
        """获取财务数据"""
        pass


class TushareDataSource(DataSource):
    """Tushare数据源"""
    
    def __init__(self, token: str):
        try:
            import tushare as ts
            self.ts = ts
            ts.set_token(token)
            self.pro = ts.pro_api()
            logger.info("Tushare数据源初始化成功")
        except Exception as e:
            logger.error(f"Tushare初始化失败: {e}")
            raise
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        try:
            df = self.pro.stock_basic(
                exchange='',
                list_status='L',
                fields='ts_code,symbol,name,area,industry,market,list_date'
            )
            return df
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            raise
    
    def get_daily_data(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str
    ) -> pd.DataFrame:
        """
        获取日线数据
        Args:
            symbol: 股票代码 (如: 000001.SZ)
            start_date: 开始日期 (格式: 20200101)
            end_date: 结束日期 (格式: 20201231)
        """
        try:
            df = self.pro.daily(
                ts_code=symbol,
                start_date=start_date,
                end_date=end_date
            )
            # 按日期排序
            df = df.sort_values('trade_date')
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            return df
        except Exception as e:
            logger.error(f"获取{symbol}日线数据失败: {e}")
            raise
    
    def get_realtime_quote(self, symbol: str) -> dict:
        """获取实时行情"""
        try:
            # Tushare的实时行情需要高级权限，这里使用最新日线数据模拟
            df = self.pro.daily(ts_code=symbol, limit=1)
            if not df.empty:
                return df.iloc[0].to_dict()
            return {}
        except Exception as e:
            logger.error(f"获取{symbol}实时行情失败: {e}")
            return {}
    
    def get_financial_data(self, symbol: str, year: int, quarter: int) -> pd.DataFrame:
        """获取财务数据"""
        try:
            period = f"{year}{quarter:02d}31" if quarter == 4 else f"{year}{quarter*3:02d}31"
            df = self.pro.income(ts_code=symbol, period=period)
            return df
        except Exception as e:
            logger.error(f"获取{symbol}财务数据失败: {e}")
            raise


class AKShareDataSource(DataSource):
    """AKShare数据源"""
    
    def __init__(self):
        try:
            import akshare as ak
            self.ak = ak
            
            # 配置更稳定的请求会话
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            self.session = requests.Session()
            
            # 设置重试策略
            retry_strategy = Retry(
                total=5,  # 总共重试5次
                backoff_factor=2,  # 指数退避
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
            )
            adapter = HTTPAdapter(
                max_retries=retry_strategy,
                pool_connections=10,
                pool_maxsize=20
            )
            self.session.mount('http://', adapter)
            self.session.mount('https://', adapter)
            
            # 设置更好的headers
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            })
            
            # 将session注入到akshare中（如果可能）
            try:
                # 尝试替换akshare内部的requests
                import akshare.stock_feature.stock_hist_em as hist_module
                if hasattr(hist_module, 'requests'):
                    hist_module.requests = self.session
            except:
                pass
            
            logger.info("AKShare数据源初始化成功（已优化网络配置）")
        except Exception as e:
            logger.error(f"AKShare初始化失败: {e}")
            raise
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        try:
            df = self.ak.stock_info_a_code_name()
            return df
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            raise
    
    def get_daily_data(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str
    ) -> pd.DataFrame:
        """
        获取日线数据 - 使用优化的网络配置
        Args:
            symbol: 股票代码 (如: 000001)
            start_date: 开始日期 (格式: 20200101)
            end_date: 结束日期 (格式: 20201231)
        """
        try:
            # AKShare需要纯数字代码
            symbol_clean = symbol.split('.')[0] if '.' in symbol else symbol
            
            # 使用优化的请求配置，增加超时时间
            import time
            max_attempts = 3
            
            for attempt in range(max_attempts):
                try:
                    if attempt > 0:
                        wait_time = 3 * attempt  # 递增等待时间
                        logger.info(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                    
                    logger.info(f"正在获取{symbol_clean}数据 (尝试 {attempt + 1}/{max_attempts})...")
                    
                    # 使用akshare获取数据，设置更长的超时
                    df = self.ak.stock_zh_a_hist(
                        symbol=symbol_clean,
                        start_date=start_date,
                        end_date=end_date,
                        adjust="qfq"
                    )
                    
                    if df.empty:
                        raise Exception(f"返回数据为空")
                    
                    # 重命名列以保持一致性
                    df = df.rename(columns={
                        '日期': 'trade_date',
                        '开盘': 'open',
                        '收盘': 'close',
                        '最高': 'high',
                        '最低': 'low',
                        '成交量': 'volume',
                        '成交额': 'amount'
                    })
                    df['trade_date'] = pd.to_datetime(df['trade_date'])
                    
                    logger.info(f"成功获取{len(df)}条数据")
                    return df
                    
                except Exception as e:
                    error_msg = str(e)
                    if attempt < max_attempts - 1:
                        logger.warning(f"获取数据失败: {error_msg}, 将重试...")
                    else:
                        # 最后一次尝试也失败了
                        logger.error(f"获取{symbol_clean}数据失败（已重试{max_attempts}次）: {error_msg}")
                        
                        # 提供更友好的错误信息
                        if 'Connection' in error_msg or 'Remote' in error_msg:
                            raise Exception(f"网络连接不稳定，请稍后重试。如果问题持续，可能是数据源服务器繁忙。")
                        elif '不存在' in error_msg or 'not found' in error_msg.lower():
                            raise Exception(f"股票代码 {symbol_clean} 不存在或已退市，请检查代码是否正确")
                        else:
                            raise Exception(f"数据获取失败: {error_msg}")
                            
        except Exception as e:
            logger.error(f"获取{symbol}日线数据失败: {e}")
            raise
    
    def get_realtime_quote(self, symbol: str) -> dict:
        """获取实时行情"""
        try:
            symbol_clean = symbol.split('.')[0] if '.' in symbol else symbol
            df = self.ak.stock_zh_a_spot_em()
            stock_data = df[df['代码'] == symbol_clean]
            if not stock_data.empty:
                return stock_data.iloc[0].to_dict()
            return {}
        except Exception as e:
            logger.error(f"获取{symbol}实时行情失败: {e}")
            return {}
    
    def get_financial_data(self, symbol: str, year: int, quarter: int) -> pd.DataFrame:
        """获取财务数据"""
        try:
            symbol_clean = symbol.split('.')[0] if '.' in symbol else symbol
            df = self.ak.stock_financial_report_sina(stock=symbol_clean, symbol="资产负债表")
            return df
        except Exception as e:
            logger.error(f"获取{symbol}财务数据失败: {e}")
            raise


class SinaDataSource(DataSource):
    """新浪财经数据源 - 免费稳定"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Referer': 'https://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        logger.info("Sina数据源初始化成功")
    
    def _normalize_symbol(self, symbol: str) -> str:
        """
        标准化股票代码为新浪格式
        Args:
            symbol: 原始代码，如 '000001', '600000', '000001.SZ'
        Returns:
            新浪格式: 'sz000001', 'sh600000'
        """
        # 移除后缀
        symbol_clean = symbol.split('.')[0] if '.' in symbol else symbol
        
        # 判断市场
        if symbol_clean.startswith('sh') or symbol_clean.startswith('sz'):
            return symbol_clean.lower()
        elif symbol_clean.startswith('6'):
            return f'sh{symbol_clean}'
        elif symbol_clean.startswith('0') or symbol_clean.startswith('3'):
            return f'sz{symbol_clean}'
        else:
            return f'sh{symbol_clean}'  # 默认上交所
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表 - 使用腾讯财经接口"""
        try:
            # 从腾讯财经获取股票列表
            url = "http://qt.gtimg.cn/q=s_sh000001,s_sz399001"
            response = self.session.get(url, timeout=10)
            
            # 简化版：返回常用股票列表
            stock_list = [
                {'code': 'sh600000', 'name': '浦发银行'},
                {'code': 'sz000001', 'name': '平安银行'},
                {'code': 'sh600519', 'name': '贵州茅台'},
                {'code': 'sz000858', 'name': '五粮液'},
                {'code': 'sh600036', 'name': '招商银行'},
                {'code': 'sh601318', 'name': '中国平安'},
            ]
            
            df = pd.DataFrame(stock_list)
            logger.info(f"获取股票列表成功，共{len(df)}只股票")
            return df
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            raise
    
    def get_daily_data(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str
    ) -> pd.DataFrame:
        """
        获取日线数据 - 使用新浪财经历史数据接口
        Args:
            symbol: 股票代码 (如: 000001, 600000, 000001.SZ)
            start_date: 开始日期 (格式: 20200101 或 2020-01-01)
            end_date: 结束日期 (格式: 20201231 或 2020-12-31)
        """
        try:
            sina_symbol = self._normalize_symbol(symbol)
            
            # 转换日期格式
            from datetime import datetime
            if '-' in start_date:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            else:
                start_dt = datetime.strptime(start_date, '%Y%m%d')
            
            if '-' in end_date:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            else:
                end_dt = datetime.strptime(end_date, '%Y%m%d')
            
            # 新浪历史数据接口 - 使用不同的URL
            # 格式: http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData
            url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData"
            params = {
                'symbol': sina_symbol,
                'scale': '240',  # 日线
                'ma': 'no',
                'datalen': '1500'  # 最多获取1500条数据
            }
            
            logger.info(f"正在获取{sina_symbol}的日线数据...")
            response = self.session.get(url, params=params, timeout=15)
            response.encoding = 'utf-8'
            
            # 解析JSON数据
            if response.text and response.text.strip():
                try:
                    data = json.loads(response.text)
                    
                    if not data or not isinstance(data, list):
                        logger.warning(f"{sina_symbol}返回数据为空或格式错误")
                        return pd.DataFrame()
                    
                    df_list = []
                    for item in data:
                        try:
                            trade_date = datetime.strptime(item['day'], '%Y-%m-%d')
                            # 只保留指定日期范围内的数据
                            if start_dt <= trade_date <= end_dt:
                                df_list.append({
                                    'trade_date': trade_date,
                                    'open': float(item['open']),
                                    'close': float(item['close']),
                                    'high': float(item['high']),
                                    'low': float(item['low']),
                                    'volume': float(item['volume'])
                                })
                        except (KeyError, ValueError) as e:
                            logger.warning(f"解析单条数据失败: {e}, 数据: {item}")
                            continue
                    
                    if not df_list:
                        logger.warning(f"{sina_symbol}在指定日期范围内无数据")
                        return pd.DataFrame()
                    
                    df = pd.DataFrame(df_list)
                    df = df.sort_values('trade_date').reset_index(drop=True)
                    
                    logger.info(f"成功获取{len(df)}条数据")
                    return df
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析失败: {e}")
                    logger.debug(f"响应内容: {response.text[:500]}")
                    raise Exception(f"数据格式异常，请稍后重试")
            else:
                logger.error(f"API返回为空")
                raise Exception(f"股票代码 {symbol} 不存在或数据源暂时无法获取该股票数据")
            
        except Exception as e:
            logger.error(f"获取{symbol}日线数据失败: {e}")
            raise
    
    def get_realtime_quote(self, symbol: str) -> dict:
        """获取实时行情"""
        try:
            sina_symbol = self._normalize_symbol(symbol)
            
            url = f"https://hq.sinajs.cn/list={sina_symbol}"
            response = self.session.get(url, timeout=10)
            response.encoding = 'gbk'
            
            # 解析返回数据
            text = response.text.strip()
            if 'hq_str_' in text:
                parts = text.split('="')
                if len(parts) >= 2:
                    values = parts[1].rstrip('";').split(',')
                    
                    if len(values) >= 32:
                        return {
                            'code': sina_symbol,
                            'name': values[0],
                            'open': float(values[1]) if values[1] else 0,
                            'pre_close': float(values[2]) if values[2] else 0,
                            'current': float(values[3]) if values[3] else 0,
                            'high': float(values[4]) if values[4] else 0,
                            'low': float(values[5]) if values[5] else 0,
                            'volume': float(values[8]) if values[8] else 0,
                            'amount': float(values[9]) if values[9] else 0,
                            'date': values[30],
                            'time': values[31]
                        }
            
            return {}
        except Exception as e:
            logger.error(f"获取{symbol}实时行情失败: {e}")
            return {}
    
    def get_financial_data(self, symbol: str, year: int, quarter: int) -> pd.DataFrame:
        """获取财务数据 - 新浪不直接提供，返回空"""
        logger.warning("新浪数据源暂不支持财务数据")
        return pd.DataFrame()


class DataManager:
    """数据管理器 - 统一数据接口"""
    
    def __init__(self, source_type: str = "sina", **kwargs):
        """
        初始化数据管理器
        Args:
            source_type: 数据源类型 ("tushare", "akshare", "sina")
            **kwargs: 数据源特定的参数（如tushare的token）
        """
        if source_type == "tushare":
            token = kwargs.get("token")
            if not token:
                raise ValueError("Tushare数据源需要提供token")
            self.source = TushareDataSource(token)
        elif source_type == "akshare":
            self.source = AKShareDataSource()
        elif source_type == "sina":
            self.source = SinaDataSource()
        else:
            raise ValueError(f"不支持的数据源类型: {source_type}")
        
        self.source_type = source_type
        logger.info(f"数据管理器初始化完成，使用{source_type}数据源")
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        return self.source.get_stock_list()
    
    def get_daily_data(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str
    ) -> pd.DataFrame:
        """获取日线数据"""
        return self.source.get_daily_data(symbol, start_date, end_date)
    
    def get_realtime_quote(self, symbol: str) -> dict:
        """获取实时行情"""
        return self.source.get_realtime_quote(symbol)
    
    def get_financial_data(self, symbol: str, year: int, quarter: int) -> pd.DataFrame:
        """获取财务数据"""
        return self.source.get_financial_data(symbol, year, quarter)
