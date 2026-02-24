# A股量化交易系统

一个功能完整的A股量化交易系统，支持自定义交易策略、历史回测、可视化图表和AI投资建议。

## ✨ 主要功能

- **🔄 多数据源支持**: 优先使用新浪财经（免费稳定），支持Tushare和AKShare作为备选
- **📊 可视化回测**: 实时展示股价走势、交易点位和资金曲线，直观呈现策略表现
- **🎯 策略引擎**: 提供灵活的策略框架，内置双均线和RSI策略，支持自定义策略
- **⚡ 高性能回测**: 基于历史数据快速测试策略，生成详细的回测报告和性能指标
- **🤖 AI投资建议**: 集成DeepSeek AI，提供智能投资分析和专业建议
- **💻 Web界面**: 现代化的可视化界面，支持交互式图表展示

## 🖼️ 功能展示

### 回测可视化
- **股价走势图**: 展示完整的价格走势，用三角形标记买入点（绿色向上）和卖出点（红色向下）
- **资金曲线图**: 双Y轴展示账户资金变化和收益率百分比
- **性能指标**: 实时显示总收益率、年化收益率、最大回撤、夏普比率等关键指标

### AI分析
- 基于DeepSeek AI的深度技术分析
- 趋势判断和支撑阻力位识别
- 短期和中期投资建议
- 风险提示和操作建议

## 🏗️ 系统架构

```
trade/
├── backend/              # 后端代码
│   ├── api/             # FastAPI接口
│   │   └── main.py      # 主API入口，提供RESTful接口
│   ├── data/            # 数据获取模块
│   │   └── data_source.py  # 多数据源实现（Sina/Tushare/AKShare）
│   ├── strategy/        # 策略引擎
│   │   └── base_strategy.py  # 策略基类和内置策略
│   ├── backtest/        # 回测引擎
│   │   └── backtest_engine.py  # 回测逻辑和性能计算
│   ├── ai/              # AI投资建议
│   │   └── deepseek_advisor.py  # DeepSeek API集成
│   └── models/          # 数据模型
├── frontend/            # 前端界面
│   └── public/          
│       └── index.html   # Web界面（集成Chart.js可视化）
├── config/              # 配置文件
│   ├── .env             # 通用配置（可上传）
│   ├── secrets.env      # API密钥（不上传）
│   └── secrets.env.template  # 密钥模板
├── data/                # 数据存储
├── logs/                # 日志文件
└── examples/            # 使用示例
```

## 🚀 快速开始

### 1. 环境准备

**Python环境要求**: Python 3.9+

```bash
# 方式1: 使用conda（推荐）
conda create -n trade python=3.9
conda activate trade

# 方式2: 使用venv
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### 2. 安装依赖

```bash
# 使用清华镜像加速（推荐）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用默认源
pip install -r requirements.txt
```

**核心依赖**:
- `fastapi` & `uvicorn`: Web服务框架
- `pandas` & `numpy`: 数据处理
- `requests`: HTTP请求
- `openai`: DeepSeek API客户端
- `loguru`: 日志管理
- `pydantic` & `pydantic-settings`: 配置管理

### 3. 配置API密钥 🔐

**重要: 为保护API密钥安全，本项目采用独立密钥文件管理**

```bash
# 步骤1: 复制模板文件
cp secrets.env.template secrets.env

# 步骤2: 编辑 secrets.env，填入真实密钥
nano secrets.env  # 或使用任何文本编辑器
```

在 `secrets.env` 中配置：

```env
# Tushare数据源Token（可选，仅在需要使用Tushare时配置）
# 获取方式：https://tushare.pro/register
TUSHARE_TOKEN=你的tushare_token

# DeepSeek AI API密钥（必需，用于AI分析功能）
# 获取方式：https://platform.deepseek.com
DEEPSEEK_API_KEY=你的deepseek_api_key
```

**安全说明**:
- ✅ `secrets.env` 已在 `.gitignore` 中，**不会**上传到GitHub
- ✅ `secrets.env.template` 是模板，**可以**安全分享
- ⚠️ **切勿**将真实密钥提交到版本控制系统

### 4. 启动服务

```bash
# 方式1: 使用uvicorn（推荐）
cd /path/to/trade
source ~/anaconda3/etc/profile.d/conda.sh  # 如果使用conda
conda activate py39
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload

# 方式2: 直接运行
python backend/api/main.py
```

**访问地址**:
- Web界面: http://localhost:8000
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/api/health

### 5. 使用Web界面

1. 在浏览器打开 http://localhost:8000
2. 选择功能标签：
   - **策略回测**: 输入股票代码、日期范围、策略类型，查看可视化回测结果
   - **AI投资建议**: 输入股票代码，获取AI分析报告
   - **设置**: 配置DeepSeek API密钥

## 📖 使用示例

### 示例1: 双均线策略回测

```python
from backend.data.data_source import DataManager
from backend.strategy.base_strategy import MAStrategy
from backend.backtest.backtest_engine import BacktestEngine

# 1. 初始化数据管理器（默认使用新浪财经）
data_manager = DataManager("sina")

# 2. 获取股票数据
data = data_manager.get_daily_data(
    symbol="000001",  # 平安银行
    start_date="20240101",
    end_date="20241231"
)

# 3. 创建双均线策略
strategy = MAStrategy(params={
    'fast_period': 5,    # 5日均线
    'slow_period': 20,   # 20日均线
    'invest_ratio': 0.5  # 每次投入50%资金
})

# 4. 运行回测
engine = BacktestEngine(
    strategy=strategy,
    data=data,
    initial_capital=100000,      # 初始资金10万
    commission_rate=0.0003       # 手续费0.03%
)

result = engine.run("000001")

# 5. 查看结果
print(f"策略名称: {result.strategy_name}")
print(f"总收益率: {result.total_return:.2%}")
print(f"年化收益率: {result.annual_return:.2%}")
print(f"最大回撤: {result.max_drawdown:.2%}")
print(f"夏普比率: {result.sharpe_ratio:.2f}")
print(f"胜率: {result.win_rate:.2%}")
print(f"交易次数: {result.total_trades}")
```

### 示例2: 使用AI获取投资建议

```python
from backend.ai.deepseek_advisor import DeepSeekAdvisor
from backend.data.data_source import DataManager

# 1. 初始化AI顾问和数据管理器
advisor = DeepSeekAdvisor()
data_manager = DataManager("sina")

# 2. 获取股票数据
stock_data = data_manager.get_daily_data(
    symbol="600519",  # 贵州茅台
    start_date="20240101",
    end_date="20240131"
)

# 3. 计算技术指标
from backend.strategy.base_strategy import TechnicalIndicators

rsi = TechnicalIndicators.RSI(stock_data['close'], 14)
macd_line, signal_line, _ = TechnicalIndicators.MACD(stock_data['close'])

indicators = {
    'RSI': round(rsi.iloc[-1], 2),
    'MACD': '金叉' if macd_line.iloc[-1] > signal_line.iloc[-1] else '死叉',
    '价格': round(stock_data['close'].iloc[-1], 2)
}

# 4. 获取AI建议
advice = advisor.analyze_stock(
    symbol="600519",
    stock_data=stock_data,
    indicators=indicators
)

print(advice)
```

### 示例3: 自定义策略

```python
from backend.strategy.base_strategy import BaseStrategy, Signal, TechnicalIndicators
import pandas as pd

class MyCustomStrategy(BaseStrategy):
    """结合RSI和MACD的自定义策略"""
    
    def __init__(self, params=None):
        default_params = {
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'invest_ratio': 0.5
        }
        if params:
            default_params.update(params)
        super().__init__("RSI+MACD策略", default_params)
    
    def generate_signal(self, data: pd.DataFrame) -> int:
        """生成交易信号"""
        if len(data) < 26:  # MACD需要至少26个数据点
            return Signal.HOLD
        
        # 计算技术指标
        rsi = TechnicalIndicators.RSI(
            data['close'], 
            self.params['rsi_period']
        )
        macd_line, signal_line, _ = TechnicalIndicators.MACD(data['close'])
        
        current_rsi = rsi.iloc[-1]
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        
        # 买入条件: RSI超卖 且 MACD金叉
        if (current_rsi < self.params['rsi_oversold'] and 
            current_macd > current_signal):
            return Signal.BUY
        
        # 卖出条件: RSI超买 或 MACD死叉
        if (current_rsi > self.params['rsi_overbought'] or 
            current_macd < current_signal):
            return Signal.SELL
        
        return Signal.HOLD

# 使用自定义策略
strategy = MyCustomStrategy(params={'invest_ratio': 0.6})
engine = BacktestEngine(strategy, data, 100000, 0.0003)
result = engine.run("000001")
```

## 🎯 内置策略

### 1. 双均线策略 (MAStrategy)

**原理**: 快速均线上穿慢速均线时买入（金叉），下穿时卖出（死叉）

**参数**:
- `fast_period`: 快速均线周期（默认: 5日）
- `slow_period`: 慢速均线周期（默认: 20日）
- `invest_ratio`: 每次投资比例（默认: 0.5，即50%）

**适用场景**: 趋势明显的市场，适合中长期持有

### 2. RSI策略 (RSIStrategy)

**原理**: 基于相对强弱指标的超买超卖策略

**参数**:
- `rsi_period`: RSI计算周期（默认: 14）
- `oversold`: 超卖阈值（默认: 30）
- `overbought`: 超买阈值（默认: 70）
- `invest_ratio`: 每次投资比例（默认: 0.5）

**适用场景**: 震荡市场，适合短线交易

## 📊 技术指标库

系统内置多种技术指标，可直接调用：

| 指标 | 说明 | 用途 |
|------|------|------|
| **SMA** | 简单移动平均 | 趋势跟踪 |
| **EMA** | 指数移动平均 | 更敏感的趋势跟踪 |
| **RSI** | 相对强弱指标 | 超买超卖判断 |
| **MACD** | 平滑异同移动平均线 | 趋势和动量 |
| **BOLL** | 布林带 | 波动性和支撑阻力 |
| **ATR** | 平均真实波幅 | 波动性测量 |
| **KDJ** | 随机指标 | 超买超卖和转折点 |

**使用示例**:

```python
from backend.strategy.base_strategy import TechnicalIndicators

# 计算5日和20日均线
sma5 = TechnicalIndicators.SMA(data['close'], 5)
sma20 = TechnicalIndicators.SMA(data['close'], 20)

# 计算RSI
rsi = TechnicalIndicators.RSI(data['close'], 14)

# 计算MACD
macd_line, signal_line, histogram = TechnicalIndicators.MACD(data['close'])

# 计算布林带
upper, middle, lower = TechnicalIndicators.BOLL(data['close'], 20, 2)
```

## 🔌 API文档

启动服务后访问自动生成的API文档: http://localhost:8000/docs

### 主要接口

#### 1. 数据接口

**获取股票历史数据**
```http
GET /api/stocks/{symbol}/data?start_date=20240101&end_date=20241231
```

**获取股票列表**
```http
GET /api/stocks
```

#### 2. 回测接口

**运行策略回测**
```http
POST /api/backtest?symbol=000001&start_date=20240101&end_date=20241231
Content-Type: application/json

{
  "name": "双均线策略",
  "strategy_type": "ma",
  "params": {},
  "initial_capital": 100000,
  "commission_rate": 0.0003
}
```

**返回数据**:
```json
{
  "strategy_name": "双均线策略",
  "total_return": 0.2362,
  "annual_return": 0.2371,
  "max_drawdown": -0.1205,
  "sharpe_ratio": 1.04,
  "win_rate": 0.0,
  "total_trades": 2,
  "trades": [...],
  "price_data": [...]  // 用于绘图的价格数据
}
```

#### 3. AI分析接口

**获取AI投资建议**
```http
POST /api/ai/analyze
Content-Type: application/json

{
  "symbol": "000001",
  "analysis_type": "stock",
  "context": null
}
```

**设置DeepSeek API密钥**
```http
POST /api/ai/set-key?api_key=your_api_key_here
```

## 📈 数据源说明

### 新浪财经（默认，推荐）
- ✅ **完全免费**，无需注册
- ✅ **稳定快速**，响应时间0.1-0.3秒
- ✅ 支持实时行情和历史数据（最多1500个交易日）
- ✅ 数据准确，包含前复权价格

### Tushare（备选）
- ⚠️ 需要注册并获取Token
- ⚠️ 免费账户有权限限制（需要积分）
- ✅ 数据全面，包含财务数据
- 获取方式: https://tushare.pro/register

### AKShare（备选）
- ✅ 完全免费，无需注册
- ⚠️ 网络稳定性一般，可能出现连接超时
- ✅ 数据来源丰富
- 备注: 因网络问题，已降为备选

## ⚙️ 配置说明

### .env 文件（通用配置）

```env
# 应用配置
APP_NAME=A股量化交易系统
DEBUG=false
LOG_LEVEL=INFO

# 数据源配置
AKSHARE_ENABLED=true

# DeepSeek API配置（实际密钥在secrets.env中）
DEEPSEEK_API_BASE=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

### secrets.env 文件（敏感信息）

```env
# API密钥（不要上传到GitHub）
TUSHARE_TOKEN=你的token
DEEPSEEK_API_KEY=sk-xxxxx
```

## ⚠️ 注意事项

1. **数据源选择**:
   - 默认使用新浪财经，稳定快速
   - 如需使用Tushare，需配置token且注意权限限制
   - 系统会自动fallback到备用数据源

2. **API限制**:
   - DeepSeek API有调用频率限制
   - 新浪财经无明确限制，但建议合理使用

3. **回测注意**:
   - 回测结果基于历史数据，不代表未来收益
   - 手续费设置对结果影响较大，建议设置真实的佣金率
   - 回测不考虑滑点、涨跌停等实际交易限制

4. **风险提示**:
   - ⚠️ 本系统仅供学习研究使用
   - ⚠️ 量化交易有风险，实盘操作需谨慎
   - ⚠️ 请勿盲目相信AI建议，需结合自身判断

5. **性能优化**:
   - 大批量回测建议使用并行计算
   - 长周期数据建议分段获取
   - 建议定期清理日志文件

## 🛠️ 故障排除

### 问题1: 数据获取失败

**错误**: `数据解析失败` 或 `连接超时`

**解决方案**:
1. 检查网络连接
2. 尝试切换数据源（在代码中修改 `DataManager("sina")` 参数）
3. 缩短日期范围（单次请求不超过2年）

### 问题2: AI分析失败

**错误**: `DeepSeek API未配置`

**解决方案**:
1. 确认 `secrets.env` 文件中配置了 `DEEPSEEK_API_KEY`
2. 检查API密钥是否有效
3. 确认有足够的API调用额度

### 问题3: 回测图表不显示

**解决方案**:
1. 确保已加载 Chart.js（通过CDN）
2. 检查浏览器控制台是否有JavaScript错误
3. 刷新页面（Ctrl+F5 或 Cmd+Shift+R）

### 问题4: 导入模块失败

**错误**: `ModuleNotFoundError`

**解决方案**:
```bash
# 确认虚拟环境已激活
conda activate py39  # 或 source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 🚀 开发计划

### 已完成 ✅
- [x] 多数据源支持（新浪/Tushare/AKShare）
- [x] 可视化回测图表（股价走势+资金曲线）
- [x] 双均线和RSI策略
- [x] DeepSeek AI集成
- [x] Web界面和API文档

### 进行中 🔄
- [ ] 更多内置策略（MACD、KDJ、网格交易等）
- [ ] 策略参数优化（遗传算法/网格搜索）
- [ ] 多股票组合回测

### 计划中 📋
- [ ] 实时行情监控和提醒
- [ ] 策略回测报告导出（PDF/Excel）
- [ ] 移动端适配
- [ ] 数据库支持（存储历史回测结果）
- [ ] 用户系统和策略分享社区

## 📄 许可证

MIT License - 可自由使用、修改和分发

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

**贡献步骤**:
1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

**代码规范**:
- 遵循PEP 8
- 添加适当的注释和文档字符串
- 提交前运行测试

## 📞 联系方式

- 提交Issue: [GitHub Issues](https://github.com/yourusername/trade/issues)
- 功能建议: 在Issue中标记 `enhancement`
- Bug报告: 在Issue中标记 `bug`

## 🙏 致谢

- 数据源: 新浪财经、Tushare、AKShare
- AI支持: DeepSeek
- 图表库: Chart.js
- Web框架: FastAPI

---

**⭐ 如果这个项目对你有帮助，请给个Star支持一下！**
