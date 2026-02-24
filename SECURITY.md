# 安全说明

## API密钥保护

本项目采用了严格的API密钥保护机制，确保你的敏感信息不会被意外上传到GitHub。

### 文件说明

1. **secrets.env** 🔒
   - 包含所有敏感的API密钥
   - 已在 `.gitignore` 中排除，不会上传到Git
   - 仅在本地使用

2. **secrets.env.template** ✅
   - API密钥配置模板
   - 可以安全上传到Git
   - 供其他开发者参考如何配置

3. **.env** ✅
   - 包含非敏感的通用配置
   - 可以安全上传到Git
   - 不包含任何真实的API密钥

### 配置加载顺序

系统会按以下顺序加载配置：

1. 首先加载 `.env`（通用配置）
2. 然后加载 `secrets.env`（会覆盖同名变量）

这样设计的好处：
- 通用配置可以分享给团队
- 敏感信息保存在本地
- 新成员只需复制模板并填入自己的密钥

### 对于贡献者

如果你fork了这个项目：

1. **复制密钥模板**
   ```bash
   cp secrets.env.template secrets.env
   ```

2. **填入你自己的API密钥**
   ```bash
   # 编辑 secrets.env
   nano secrets.env
   ```

3. **永远不要提交 secrets.env**
   - Git已经配置忽略此文件
   - 在提交前务必检查 `git status`

### 检查清单

在提交代码前，请确认：

- [ ] `secrets.env` 不在暂存区
- [ ] `.env` 文件中没有真实的API密钥
- [ ] 代码中没有硬编码的密钥
- [ ] 日志输出中没有包含密钥信息

### 紧急情况

如果不小心将API密钥上传到GitHub：

1. **立即撤销密钥**
   - Tushare: https://tushare.pro/user/token
   - DeepSeek: https://www.deepseek.com

2. **生成新的密钥**

3. **从Git历史中删除敏感信息**
   ```bash
   git filter-branch --force --index-filter \
   "git rm --cached --ignore-unmatch secrets.env" \
   --prune-empty --tag-name-filter cat -- --all
   ```

4. **强制推送**
   ```bash
   git push origin --force --all
   ```

## 最佳实践

1. 定期更换API密钥
2. 不要在公共场所展示包含密钥的屏幕截图
3. 不要将密钥硬编码在代码中
4. 使用环境变量管理所有敏感信息
