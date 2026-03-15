# Requirement Doc Manager Skill

## 触发条件
- 命令行：`openclaw req-doc --input <file> [--template standard|lite]`
- 直接调用：提供需求描述文字即可触发

## 功能描述
从需求描述（文字/会议记录/文件）自动生成结构化 PRD 文档，包含：
- 用户故事（标准格式：作为...我想要...以便...）
- 功能需求列表
- 业务规则
- 验收标准
- 风险评估
- 质量报告（完整率/清晰度/一致性评分）

## 输入
```json
{
  "source": "file|meeting_transcript|voice|text",
  "content": "string (需求描述，50-10000 字)",
  "context": {
    "project_name": "string (可选，项目名称)",
    "priority": "P0|P1|P2 (可选，优先级)",
    "template": "standard|lite (可选，默认 standard)"
  }
}
```

## 输出
```json
{
  "prd": {
    "title": "string",
    "version": "vYYYYMMDD-序号",
    "background": "string",
    "user_stories": [{"role": "string", "need": "string", "benefit": "string"}],
    "functional_requirements": [{"id": "string", "title": "string", "description": "string"}],
    "business_rules": ["string"],
    "acceptance_criteria": ["string"],
    "risks": [{"description": "string", "level": "high|medium|low"}],
    "storage": {"type": "markdown", "path": "string"}
  },
  "quality_report": {
    "completeness_score": 0-100,
    "clarity_score": 0-100,
    "consistency_score": 0-100,
    "overall_score": 0-100,
    "missing_items": ["string"],
    "suggestions": ["string"]
  },
  "execution": {
    "duration_ms": number,
    "model_used": "string",
    "token_used": number,
    "cost": number
  }
}
```

## 配置
```yaml
# LLM 配置
llm:
  primary: qwen3.5-plus
  fallback: qwen2
  timeout: 60
  max_retries: 3

# 成本配置
cost:
  daily_limit: 30
  monthly_limit: 100
  estimate_per_request: 2.0

# 模板配置
template:
  default: standard
  versions:
    - standard
    - lite
```

## 工作流程
```
1. 接收请求 → 解析输入源和内容
2. 需求抽取 → LLM 并行抽取（用户故事/功能/规则/验收/风险）
3. 完整性校验 → 检查必填项 + 格式规范
4. 质量评分 → 完整率/清晰度/一致性
5. 文档生成 → 填充模板（标准版/精简版）
6. 推送归档 → 本地 Markdown 存储 + 日志记录
```

## 降级策略
| 故障 | 应对 |
|------|------|
| LLM 超时 | 重试 3 次（指数退避）→ 降级 qwen2 |
| 抽取为空 | 追问用户补充 → 标记"待确认" |
| 成本超支 | 建议精简版 → 用户拒绝则中止 |
| 连续失败 | >3 次触发告警 → 建议人工处理 |

## 错误码
| 错误码 | 说明 |
|--------|------|
| REQ-DOC-101 | 输入格式错误 |
| REQ-DOC-102 | 必填项缺失 |
| REQ-DOC-201 | 抽取超时 |
| REQ-DOC-202 | 抽取结果为空 |
| REQ-DOC-301 | 完整性校验失败 |
| REQ-DOC-401 | 模板渲染失败 |
| REQ-DOC-501 | 存储失败 |
| REQ-DOC-502 | 成本超支 |

## 监控指标
- 成功率：>95%
- P95 延迟：<3 分钟
- 单次成本：<¥2
- 需求完整率：>90%
- 用户满意度：>4.5/5

## 日志
- 路径：`/var/log/openclaw/req-doc.log`
- 格式：JSON 结构化日志
- 级别：INFO（正常）/ WARNING（降级）/ ERROR（失败）

## 示例

### 示例 1：命令行触发
```bash
openclaw req-doc --input requirement.txt --template standard
```

### 示例 2：会议记录触发
```
用户：整理这个会议的需求
用户：[粘贴会议转写内容]

输出：
- 从会议记录提取需求
- 生成 PRD 文档
```

## 相关文件
- `config.yaml` - 配置文件
- `templates/prd_standard.md.j2` - PRD 标准版模板
- `templates/prd_lite.md.j2` - PRD 精简版模板
- `references/user_story_format.md` - 用户故事格式规范
- `tests/` - 测试用例（63 个）

## 版本
- 当前版本：v1.0
- 创建日期：2026-03-14
- 最后更新：2026-03-14
