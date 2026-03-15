# OpenClaw Skill 集成说明

## 环境变量

本 Skill **不需要**在 `.env` 文件中配置 API Key，直接使用 OpenClaw 系统环境变量：

| 环境变量 | 说明 | 必需 |
|----------|------|------|
| `DASHSCOPE_API_KEY` | 阿里云百炼 API Key | 是 |
| `FEISHU_APP_ID` | 飞书应用 ID | 否（无则本地存储） |
| `FEISHU_APP_SECRET` | 飞书应用密钥 | 否（无则本地存储） |

## 调用方式

### 1. OpenClaw 对话

```
整理需求文档：需要一个用户登录功能
```

### 2. OpenClaw 命令行

```bash
openclaw req-doc --input "需要一个登录功能"
```

### 3. Python 代码

```python
from main import run
result = run("需要一个登录功能")
```

## 注意事项

- ✅ API Key 由 OpenClaw 统一管理
- ✅ 不需要在 Skill 中重复配置
- ✅ 本地测试时可创建 `.env` 文件（已 gitignore）
