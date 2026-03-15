# Requirement Doc Manager - 使用指南

> Skill 已集成到 OpenClaw，可以直接调用

---

## 🚀 快速开始

### 1. 配置 API Key

```bash
# 编辑 .env 文件
cd ~/.openclaw/workspace/skills/requirement-doc-manager
nano .env

# 确保以下内容（替换为你的真实 API Key）:
DASHSCOPE_API_KEY="sk-your-real-api-key"
FEISHU_APP_ID="cli_xxx"
FEISHU_APP_SECRET="xxx"
```

### 2. 激活 API Key

访问：https://dashscope.console.aliyun.com/
- 登录账号
- 进入「API-KEY 管理」
- 确认 Key 状态为「已激活」
- 如未开通，点击「开通服务」

---

## 📱 调用方式

### 方式 1: OpenClaw 对话触发

直接在 OpenClaw 中发送：

```
整理需求文档：需要一个用户登录功能，支持手机号和邮箱
```

或

```
生成 PRD --project 用户管理系统
```

### 方式 2: 命令行调用

```bash
cd ~/.openclaw/workspace/skills/requirement-doc-manager
source .venv/bin/activate

# 加载环境变量
set -a && source .env && set +a

# 运行 Skill
python main.py "需要一个登录功能"
```

### 方式 3: Python 代码调用

```python
from main import run

result = run("需要一个用户登录功能，支持手机号注册")
print(result)
```

### 方式 4: 使用快捷脚本

```bash
python scripts/generate_prd.py "需要一个登录功能" \
  --project 用户系统 \
  --priority P1 \
  --template standard
```

---

## 📋 参数说明

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `content` | 需求描述（必需） | - | "需要一个登录功能" |
| `--project` | 项目名称 | "需求文档" | "--project 用户系统" |
| `--priority` | 优先级 (P0/P1/P2) | "P1" | "--priority P0" |
| `--template` | 模板类型 (standard/lite) | "standard" | "--template lite" |

---

## 💡 使用示例

### 示例 1: 简单需求

```
整理需求文档：需要一个用户注册功能
```

**输出**:
```
✅ **PRD 文档生成成功！**

📄 **标题**: 需求文档
🏷️ **版本**: v20260314-2230
📊 **完整率**: 85/100
⏱️  **耗时**: 2500ms
💰 **成本**: ¥0.008

📦 **用户故事**: 3 条
📦 **功能需求**: 5 条
📦 **验收标准**: 4 条

🔗 **飞书文档**: https://feishu.cn/docx/xxx
```

### 示例 2: 指定项目

```
生成 PRD --project 电商平台 --priority P0
```

### 示例 3: 精简版

```
写一个 prd，精简版，项目：内部管理系统
```

---

## 📊 输出说明

### 完整输出包含

1. **文档信息**: 标题、版本、完整率、耗时、成本
2. **内容统计**: 用户故事、功能需求、验收标准数量
3. **存储位置**: 飞书文档链接 或 本地文件路径
4. **改进建议**: 质量报告中的建议
5. **内容预览**: 前 3 条用户故事

### 质量评分说明

| 分数 | 说明 |
|------|------|
| 90-100 | 优秀，可直接使用 |
| 80-89 | 良好，少量修改 |
| 70-79 | 一般，需要补充 |
| <70 | 需完善，建议人工审核 |

---

## ⚠️ 常见问题

### 问题 1: `401 Incorrect API key provided`

**原因**: API Key 未激活或格式错误

**解决**:
1. 访问 https://dashscope.console.aliyun.com/
2. 确认 Key 状态为「已激活」
3. 检查 `.env` 文件中的 Key 是否正确

### 问题 2: `余额不足`

**原因**: 账号余额不足

**解决**:
1. 访问控制台「费用中心」
2. 充值即可（新用户有免费额度）

### 问题 3: 飞书文档创建失败

**原因**: 飞书 API 未配置或权限不足

**解决**:
1. 配置 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`
2. 在飞书应用管理中添加文档权限
3. 失败时会自动降级到本地存储

### 问题 4: 完整率低

**原因**: 需求描述过于简单

**解决**:
- 提供更详细的需求描述
- 参考改进建议补充内容
- 人工审核后补充

---

## 📁 文件结构

```
requirement-doc-manager/
├── main.py                    # OpenClaw Skill 入口 ✅
├── skill.json                 # Skill 配置 ✅
├── .env                       # API Key 配置 ✅
├── src/                       # 核心代码
│   ├── orchestrator.py        # 编排器
│   └── capabilities/          # 能力模块
├── templates/                 # PRD 模板
├── scripts/
│   ├── generate_prd.py        # 快捷脚本 ✅
│   └── check_api.sh           # API 检查 ✅
└── docs/
    ├── USAGE.md               # 本文档 ✅
    ├── QUICK_START.md         # 快速开始
    └── API_SETUP.md           # API 配置指南
```

---

## 🔧 高级配置

### 自定义模板

编辑 `templates/prd_standard.md.j2` 自定义 PRD 格式

### 调整预算

编辑 `config.yaml`:

```yaml
cost:
  daily_limit: 50      # 日预算
  monthly_limit: 200   # 月预算
```

### 自定义模型

编辑 `config.yaml`:

```yaml
llm:
  primary: qwen-max    # 使用更强大的模型
  fallback: qwen-plus
```

---

## 📞 支持

- **技能文档**: 查看 `SKILL.md`
- **API 配置**: 查看 `API_SETUP.md`
- **故障排除**: 查看 `API_STATUS.md`
- **测试报告**: 查看 `TEST_REPORT.md`

---

_最后更新：2026-03-14_
