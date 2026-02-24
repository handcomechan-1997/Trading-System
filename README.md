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

## 🚀 快速开始

### 1. 环境准备

**Python环境要求**: Python 3.9+

```bash
# 使用conda（推荐）
conda create -n trade python=3.9
conda activate trade

# 或使用venv
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
# Tushare数据源Token（可选）
# 获取方式：https://tushare.pro/register
TUSHARE_TOKEN=你的tushare_token

# DeepSeek AI API密钥（必需）
# 获取方式：https://platform.deepseek.com
DEEPSEEK_API_KEY=你的deepseek_api_key
```

**安全说明**:
- ✅ `secrets.env` 已在 `.gitignore` 中，**不会**上传到GitHub
- ✅ `secrets.env.template` 是模板，**可以**安全分享
- ⚠️ **切勿**将真实密钥提交到版本控制系统

### 4. 启动服务

```bash
# 启动服务
cd /path/to/trade
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

**访问地址**:
- Web界面: http://localhost:8000
- API文档: http://localhost:8000/docs

### 5. 使用Web界面

1. 在浏览器打开 http://localhost:8000
2. 选择功能标签：
   - **策略回测**: 输入股票代码、日期范围、策略类型，查看可视化回测结果
   - **AI投资建议**: 输入股票代码，获取AI分析报告
   - **设置**: 配置DeepSeek API密钥

## 🎯 内置策略

### 1. 双均线策略 (MAStrategy)
- **原理**: 快速均线上穿慢速均线时买入（金叉），下穿时卖出（死叉）
- **适用**: 趋势明显的市场，适合中长期持有

### 2. RSI策略 (RSIStrategy)
- **原理**: 基于相对强弱指标的超买超卖策略
- **适用**: 震荡市场，适合短线交易

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

## 🔌 API文档

启动服务后访问: http://localhost:8000/docs

### 主要接口

- `GET /api/stocks/{symbol}/data` - 获取股票历史数据
- `POST /api/backtest` - 运行策略回测
- `POST /api/ai/analyze` - 获取AI投资建议
- `POST /api/ai/set-key` - 设置DeepSeek API密钥

详细的API参数说明请查看自动生成的文档。

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
- 备注: 因网络问题，已降为备选

## 🛠️ 故障排除

### 数据获取失败
**问题**: `数据解析失败` 或 `连接超时`

**解决**:
1. 检查网络连接
2. 缩短日期范围（单次请求不超过2年）
3. 尝试切换数据源

### AI分析失败
**问题**: `DeepSeek API未配置`

**解决**:
1. 确认 `secrets.env` 文件中配置了 `DEEPSEEK_API_KEY`
2. 检查API密钥是否有效
3. 确认有足够的API调用额度

### 回测图表不显示
**解决**:
1. 确保浏览器已加载 Chart.js（通过CDN）
2. 检查浏览器控制台是否有JavaScript错误
3. 刷新页面（Ctrl+F5 或 Cmd+Shift+R）

### 导入模块失败
**问题**: `ModuleNotFoundError`

**解决**:
```bash
# 确认虚拟环境已激活
conda activate trade  # 或 source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## ⚠️ 注意事项

1. **数据源选择**: 默认使用新浪财经，稳定快速。如需使用Tushare，需配置token且注意权限限制

2. **API限制**: DeepSeek API有调用频率限制，建议合理使用

3. **回测注意**: 
   - 回测结果基于历史数据，不代表未来收益
   - 手续费设置对结果影响较大，建议设置真实的佣金率
   - 回测不考虑滑点、涨跌停等实际交易限制

4. **风险提示**: 
   - ⚠️ 本系统仅供学习研究使用
   - ⚠️ 量化交易有风险，实盘操作需谨慎
   - ⚠️ 请勿盲目相信AI建议，需结合自身判断

## 📂 项目结构

```
trade/
├── backend/              # 后端代码
│   ├── api/             # FastAPI接口
│   ├── data/            # 数据获取模块
│   ├── strategy/        # 策略引擎
│   ├── backtest/        # 回测引擎
│   ├── ai/              # AI投资建议
│   └── models/          # 数据模型
├── frontend/            # 前端界面
│   └── public/          
│       └── index.html   # Web界面
├── config/              # 配置文件
│   ├── secrets.env      # API密钥（不上传）
│   └── secrets.env.template  # 密钥模板
├── examples/            # 使用示例
├── requirements.txt     # 项目依赖
└── README.md           # 项目文档
```

## 🚀 开发计划

### 已完成 ✅
- [x] 多数据源支持
- [x] 可视化回测图表
- [x] 双均线和RSI策略
- [x] DeepSeek AI集成
- [x] Web界面和API文档

### 计划中 📋
- [ ] 更多内置策略（MACD、KDJ、网格交易等）
- [ ] 策略参数优化（遗传算法/网格搜索）
- [ ] 多股票组合回测
- [ ] 实时行情监控和提醒
- [ ] 策略回测报告导出（PDF/Excel）

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

**贡献步骤**:
1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

## 🙏 致谢

- 数据源: 新浪财经、Tushare、AKShare
- AI支持: DeepSeek
- 图表库: Chart.js
- Web框架: FastAPI

---

**⭐ 如果这个项目对你有帮助，请给个Star支持一下！**
