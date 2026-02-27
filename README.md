<div align="center">

# 📈 A股量化交易系统

### *智能策略 · 可视化回测 · AI投资建议*

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**一个功能完整的A股量化交易系统，让量化投资变得简单**

[快速开始](#-5分钟快速部署) · [功能介绍](#-核心功能) · [使用文档](#-使用指南)

</div>

---

## 💡 核心亮点

🎯 **零编程自定义策略** - 可视化拖拽构建交易策略，4种预设模板一键应用  
📊 **实时可视化回测** - 股价走势、交易点位、资金曲线一目了然  
🤖 **AI智能分析** - 集成DeepSeek AI，提供专业投资建议  
⚡ **稳定数据源** - 新浪财经免费数据，响应快速无需注册  

---

## 🚀 5分钟快速部署

### 步骤1：克隆项目

```bash
git clone https://github.com/yourusername/trading-system.git
cd trading-system
```

### 步骤2：创建Python环境

```bash
# 使用conda（推荐）
conda create -n trade python=3.9
conda activate trade

# 或使用venv
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
```

### 步骤3：安装依赖

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 步骤4：配置API密钥（可选）

```bash
# 复制配置模板
cp secrets.env.template secrets.env

# 编辑secrets.env文件，填入你的DeepSeek API密钥
# 如果只想体验回测功能，可以跳过此步骤
```

**获取DeepSeek API密钥**：访问 [platform.deepseek.com](https://platform.deepseek.com) 注册并创建API密钥

### 步骤5：启动服务

```bash
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 步骤6：打开浏览器

在浏览器中访问：**http://localhost:8000**

🎉 **完成！** 现在您可以开始使用了

---

## 🎯 快速上手

### 第一次使用？试试这个！

1. 打开浏览器访问 http://localhost:8000
2. 点击"**自定义策略**"标签页
3. 点击"**双均线策略**"模板卡片（带"推荐"标签）
4. 直接点击"**开始回测**"按钮
5. 查看可视化结果：交易次数、收益率、买卖点图表

**预期结果**：
- 📊 10笔交易
- 📉 -9.57% 收益率（2023年平安银行下跌趋势）
- 🎨 图表上显示5个绿色买入点和5个红色卖出点

---

## 🌟 核心功能

### 1️⃣ 可视化策略构建器

**零编程创建交易策略**，像搭积木一样简单！

#### 📋 预设模板（一键应用）
- **双均线策略** - MA5/MA20金叉死叉（推荐新手）
- **RSI超买超卖** - RSI指标动量策略
- **MACD金叉死叉** - MACD信号线交叉策略
- **多指标组合** - 均线+RSI组合策略

#### 🎨 可视化规则编辑器
- **流程图风格**：`[指标A]` → `[>]` → `[指标B]`
- **交叉规则**：金叉/死叉信号
- **条件规则**：自定义指标比较
- **实时预览**：配置即时生效

#### 支持的技术指标
| 指标 | 说明 | 用途 |
|------|------|------|
| MA/EMA | 移动平均线 | 趋势跟踪 |
| RSI | 相对强弱指标 | 超买超卖 |
| MACD | 平滑异同移动平均 | 趋势动量 |
| BOLL | 布林带 | 波动性分析 |
| KDJ | 随机指标 | 转折点判断 |
| VOLUME | 成交量 | 量价分析 |

---

### 2️⃣ 高性能回测引擎

**完整的历史数据回测，专业级性能指标**

#### 📊 可视化图表
- **股价走势图**：完整价格走势 + 买卖点标记
  - 🟢 绿色三角形：买入点
  - 🔴 红色倒三角：卖出点
- **资金曲线图**：账户价值变化 + 收益率曲线
- **悬停提示**：查看具体交易价格和数量

#### 📈 性能指标
- **总收益率** - 策略整体表现
- **年化收益率** - 折算为年化数据
- **最大回撤** - 最大亏损幅度
- **夏普比率** - 风险调整后收益
- **胜率** - 盈利交易占比
- **交易次数** - 总交易笔数

#### ⚙️ 回测设置
- 自定义初始资金
- 设置手续费率
- 选择回测时间范围
- 支持任意A股代码

---

### 3️⃣ AI投资建议

**DeepSeek AI驱动的智能分析**

- 📊 **技术分析**：趋势判断、支撑阻力位识别
- 🎯 **投资建议**：短期和中期操作建议
- ⚠️ **风险提示**：潜在风险识别和提醒
- 📝 **Markdown格式**：清晰易读的分析报告

**推荐股票（已缓存，响应快速）**：
- 000001（平安银行）
- 600000（浦发银行）
- 000002（万科A）
- 600519（贵州茅台）
- 000858（五粮液）

---

### 4️⃣ 数据源管理

#### 🌐 新浪财经（默认推荐）
- ✅ **完全免费**，无需注册
- ✅ **快速稳定**，响应时间 0.1-0.3秒
- ✅ **数据准确**，支持前复权价格
- ✅ 最多获取 1500 个交易日数据

#### 🔄 备选数据源
- **Tushare**：需要Token，数据全面但有权限限制
- **AKShare**：免费但网络不稳定

系统会自动在数据源间切换，确保服务可用性。

---

## 📖 使用指南

### 策略回测

1. 点击"**策略回测**"标签
2. 选择预设策略（双均线/RSI）
3. 输入股票代码（如：000001）
4. 设置日期范围（如：20230101-20231231）
5. 设置初始资金和手续费率
6. 点击"**开始回测**"

### 自定义策略

#### 方法1：使用模板（推荐）
1. 点击"**自定义策略**"标签
2. 选择一个策略模板卡片
3. 系统自动配置规则和参数
4. 点击"**开始回测**"

#### 方法2：手动创建
1. 点击"**+ 添加交叉规则**"或"**+ 添加条件规则**"
2. 配置买入规则：
   - 选择指标（如：MA）
   - 设置参数（如：周期5）
   - 选择比较方式（如：金叉）
   - 选择对比指标（如：MA，周期20）
3. 配置卖出规则（同上）
4. 设置回测参数并开始回测

#### 方法3：保存/加载策略
- 点击"**保存策略**"导出为JSON文件
- 点击"**加载策略**"导入已保存的配置

### AI投资建议

1. 点击"**AI投资建议**"标签
2. 输入股票代码（推荐使用已缓存的代码）
3. 点击"**获取AI建议**"
4. 等待AI分析完成（约5-10秒）
5. 查看Markdown格式的分析报告

---

## 🛠️ API文档

启动服务后访问：**http://localhost:8000/docs**

### 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/indicators` | GET | 获取可用指标列表 |
| `/api/backtest` | POST | 运行策略回测 |
| `/api/strategy/validate` | POST | 验证策略配置 |
| `/api/ai/analyze` | POST | AI投资分析 |
| `/api/stocks/{symbol}/data` | GET | 获取股票数据 |

详细参数说明请查看Swagger文档。

---

## 🔧 故障排除

### ❌ 数据获取失败

**问题**：显示"数据获取失败"或"连接超时"

**解决方案**：
1. 检查网络连接
2. 缩短日期范围（建议单次不超过3年）
3. 更换股票代码重试
4. 查看终端日志获取详细错误信息

### ❌ 回测无交易记录

**问题**：回测完成但显示"交易次数: 0"

**解决方案**：
1. 使用预设模板重新配置策略
2. 检查买入/卖出规则是否都已配置
3. 确认规则配置合理（如：MA5与MA20对比）
4. 尝试更换时间范围或股票代码

### ❌ 图表不显示

**问题**：回测结果没有图表

**解决方案**：
1. 刷新页面（Ctrl+F5 / Cmd+Shift+R）
2. 检查浏览器是否阻止了CDN加载
3. 打开浏览器控制台查看JavaScript错误
4. 尝试更换浏览器（推荐Chrome/Safari）

### ❌ AI分析失败

**问题**：显示"AI顾问未初始化"

**解决方案**：
1. 确认已创建 `secrets.env` 文件
2. 检查 `DEEPSEEK_API_KEY` 是否正确配置
3. 验证API密钥是否有效（访问DeepSeek平台）
4. 确认账户有足够的API额度

### ❌ 模块导入错误

**问题**：`ModuleNotFoundError: No module named 'xxx'`

**解决方案**：
```bash
# 确认虚拟环境已激活
conda activate trade  # 或 source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 📂 项目结构

```
trade/
├── backend/                    # 后端服务
│   ├── api/                   # FastAPI接口
│   │   └── main.py           # 主应用入口
│   ├── data/                  # 数据模块
│   │   └── data_source.py    # 多数据源管理
│   ├── strategy/              # 策略引擎
│   │   ├── base_strategy.py  # 策略基类和内置策略
│   │   └── custom_strategy.py # 自定义策略引擎
│   ├── backtest/              # 回测引擎
│   │   └── backtest_engine.py
│   ├── ai/                    # AI模块
│   │   └── deepseek_advisor.py
│   └── models/                # 数据模型
├── frontend/                   # 前端界面
│   └── public/
│       └── index.html         # Web单页应用
├── config/                     # 配置文件
│   ├── config.py             # 配置加载
│   ├── secrets.env           # API密钥（不上传）
│   └── secrets.env.template  # 密钥模板
├── examples/                   # 使用示例
│   ├── example_ma_strategy.py
│   └── example_rsi_strategy.py
├── requirements.txt           # Python依赖
├── .gitignore                # Git忽略文件
└── README.md                 # 项目文档
```

---

## ⚠️ 重要提示

### 🔐 安全性
- ✅ `secrets.env` 已在 `.gitignore` 中，不会上传到GitHub
- ⚠️ 切勿将API密钥提交到版本控制系统
- ⚠️ 不要在公共场合分享 `secrets.env` 文件

### 📊 回测说明
- ⚠️ 回测结果基于**历史数据**，不代表未来表现
- ⚠️ 实际交易会受到滑点、涨跌停等限制
- ⚠️ 手续费设置对结果影响较大，建议使用真实佣金率

### 🤖 AI建议
- ⚠️ AI分析仅供**参考**，不构成投资建议
- ⚠️ 请结合自身判断和风险承受能力
- ⚠️ 投资有风险，入市需谨慎

### 📜 免责声明
- ⚠️ 本系统**仅供学习研究使用**
- ⚠️ 作者不对使用本系统产生的任何损失负责
- ⚠️ 实盘交易请谨慎决策

---

## 🚀 未来计划

### ✅ 已完成
- [x] 多数据源支持（新浪/Tushare/AKShare）
- [x] 可视化回测引擎
- [x] 内置双均线和RSI策略
- [x] DeepSeek AI集成
- [x] Web界面和API文档
- [x] **可视化策略构建器**
- [x] **预设策略模板系统**
- [x] **流程图风格的规则编辑器**

### 📋 开发中
- [ ] 实时预览效果（配置规则时显示历史信号数量）
- [ ] 策略参数优化（遗传算法/网格搜索）
- [ ] 多股票组合回测
- [ ] 实时行情监控和提醒
- [ ] 策略回测报告导出（PDF/Excel）
- [ ] 更多预设策略模板

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

**贡献步骤**：
1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

**代码规范**：
- 遵循PEP 8代码风格
- 添加必要的注释和文档字符串
- 确保所有测试通过

---

## 🙏 致谢

### 数据来源
- [新浪财经](https://finance.sina.com.cn/) - 免费稳定的股票数据
- [Tushare](https://tushare.pro/) - 专业金融数据接口
- [AKShare](https://akshare.akfamily.xyz/) - 开源财经数据接口

### 技术支持
- [DeepSeek](https://platform.deepseek.com/) - AI智能分析
- [FastAPI](https://fastapi.tiangolo.com/) - 高性能Web框架
- [Chart.js](https://www.chartjs.org/) - 图表可视化库
- [Pandas](https://pandas.pydata.org/) - 数据分析工具

---

<div align="center">

### ⭐ 如果这个项目对你有帮助，请给个Star支持一下！

**让量化投资变得简单** 🚀

[报告问题](https://github.com/yourusername/trading-system/issues) · 
[功能建议](https://github.com/yourusername/trading-system/issues) · 
[查看文档](https://github.com/yourusername/trading-system/wiki)

</div>
