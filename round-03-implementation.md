# Round 3: 能力拆解 + 实现规范

> 主导 Agent：Engineer（实现工程师）  
> 时间：2026-03-14  
> 状态：进行中

---

## 3.1 任务分解树（28 原子任务）

```
需求文档管理 Skill
├── 1. 接收请求（3 任务）
│   ├── 1.1 解析触发源（飞书/CLI/webhook）
│   ├── 1.2 提取输入内容
│   └── 1.3 验证输入格式（schema 验证）
├── 2. 内容获取（4 任务）
│   ├── 2.1 飞书消息→直接读取
│   ├── 2.2 文件→下载解析
│   ├── 2.3 语音→转写服务（飞书妙计）
│   └── 2.4 链接→抓取内容
├── 3. 需求抽取（6 任务，可并行）
│   ├── 3.1 用户角色抽取
│   ├── 3.2 用户故事抽取
│   ├── 3.3 功能需求抽取
│   ├── 3.4 业务规则抽取
│   ├── 3.5 验收标准抽取
│   └── 3.6 风险项抽取
├── 4. 完整性校验（4 任务）
│   ├── 4.1 必填字段检查
│   ├── 4.2 格式规范检查
│   ├── 4.3 逻辑一致性检查
│   └── 4.4 可测试性检查
├── 5. 质量评分（4 任务）
│   ├── 5.1 完整率计算
│   ├── 5.2 清晰度评分
│   ├── 5.3 一致性评分
│   └── 5.4 生成改进建议
├── 6. 文档生成（4 任务）
│   ├── 6.1 选择模板（标准版/精简版）
│   ├── 6.2 填充内容（Jinja2）
│   ├── 6.3 格式化输出
│   └── 6.4 创建飞书文档
├── 7. 推送归档（3 任务）
│   ├── 7.1 飞书群通知
│   ├── 7.2 版本库存储
│   └── 7.3 日志记录
└── 8. 错误处理（3 任务，并行）
    ├── 8.1 重试机制（指数退避）
    ├── 8.2 降级策略（5 层级）
    └── 8.3 人工升级（告警）
```

---

## 3.2 Skill 目录结构

```
skills/requirement-doc-manager/
├── SKILL.md                      # Skill 描述（触发条件/用法）
├── config.yaml                   # 配置（API key/阈值/模板）
├── src/
│   ├── __init__.py
│   ├── orchestrator.py           # 编排层（5 状态状态机）
│   ├── capabilities/
│   │   ├── __init__.py
│   │   ├── fetcher.py            # 内容获取
│   │   ├── extractor.py          # 需求抽取（LLM）
│   │   ├── validator.py          # 完整性校验
│   │   ├── scorer.py             # 质量评分
│   │   ├── generator.py          # 文档生成
│   │   └── pusher.py             # 推送发布
│   ├── validators/
│   │   ├── schema.py             # 输入输出 schema 验证
│   │   └── rules.py              # 业务规则（必填项/格式）
│   ├── fallbacks/
│   │   ├── simple_extractor.py   # 简化抽取（qwen2）
│   │   └── templates.py          # 降级模板
│   └── utils/
│       ├── logger.py             # 日志工具
│       └── cost_tracker.py       # 成本追踪（复用 openclaw）
├── templates/
│   ├── prd_standard.md.j2        # PRD 标准版（Jinja2）
│   └── prd_lite.md.j2            # PRD 精简版
├── references/
│   ├── user_story_format.md      # 用户故事格式规范
│   ├── acceptance_criteria.md    # 验收标准编写指南
│   └── api_docs.md               # 飞书 API 文档摘要
├── tests/
│   ├── __init__.py
│   ├── test_extractor.py         # 抽取测试（15 用例）
│   ├── test_validator.py         # 校验测试（10 用例）
│   ├── test_generator.py         # 生成测试（10 用例）
│   ├── test_integration.py       # 集成测试（10 用例）
│   ├── test_e2e.py               # E2E 测试（3 用例）
│   ├── test_security.py          # 安全测试（5 用例）
│   └── fixtures/
│       ├── sample_input.json
│       ├── expected_output.json
│       └── meeting_transcript.txt
└── scripts/
    ├── deploy.sh                 # 部署脚本
    ├── init_config.py            # 配置初始化
    └── run_tests.sh              # 测试脚本
```

---

## 3.3 SKILL.md（核心内容）

```markdown
# Requirement Doc Manager Skill

## 触发条件
- 飞书消息："整理需求文档" / "生成 PRD" / "需求文档"
- 命令行：`openclaw req-doc --input <file> [--template standard|lite]`
- Webhook：飞书文档变更（标签：#需求）

## 输入
```json
{
  "source": "feishu_message|file|meeting_transcript|voice",
  "content": "string",
  "context": {
    "project_name": "string (可选)",
    "priority": "P0|P1|P2 (可选)",
    "template": "standard|lite (可选)"
  }
}
```

## 输出
- PRD 文档（飞书文档/Markdown）
- 质量报告（完整率/清晰度/一致性评分）
- 执行元数据（耗时/成本/模型）

## 配置
```yaml
feishu:
  app_id: ${FEISHU_APP_ID}
  app_secret: ${FEISHU_APP_SECRET}
  
llm:
  primary: qwen3.5-plus
  fallback: qwen2
  timeout: 60
  
cost:
  daily_limit: 30
  monthly_limit: 100
  
template:
  default: standard
  storage_folder: /需求文档库
```

## 降级策略
1. LLM 超时→重试 3 次→qwen2
2. 抽取为空→追问用户→标记待确认
3. 飞书失败→本地存储→通知用户
4. 成本超支→建议精简版→中止

## 监控
- 日志：/var/log/openclaw/req-doc.log
- 指标：成功率/P95 延迟/成本/完整率
- 告警：连续失败>3 次→飞书群通知
```

---

## 3.4 核心代码模板

### 3.4.1 Orchestrator（5 状态状态机）

```python
# src/orchestrator.py
from enum import Enum
from typing import Optional

class State(Enum):
    RECEIVE = "receive"
    EXTRACT = "extract"
    VALIDATE = "validate"
    GENERATE = "generate"
    ARCHIVE = "archive"

class ReqDocOrchestrator:
    def __init__(self, config: Config):
        self.config = config
        self.fetcher = ContentFetcher(config)
        self.extractor = RequirementExtractor(config)
        self.validator = RequirementValidator(config)
        self.scorer = QualityScorer(config)
        self.generator = DocumentGenerator(config)
        self.pusher = DocumentPusher(config)
        self.cost_tracker = CostTracker(config)
    
    async def run(self, input_data: ReqDocInput) -> ReqDocOutput:
        state = State.RECEIVE
        context = {"input": input_data, "retries": 0}
        
        try:
            # State 1: RECEIVE
            state = State.RECEIVE
            content = await self._receive(input_data, context)
            
            # State 2: EXTRACT
            state = State.EXTRACT
            extracted = await self._extract(content, context)
            
            # State 3: VALIDATE
            state = State.VALIDATE
            validation = await self._validate(extracted, context)
            if not validation.passed:
                extracted = await self._handle_validation_failure(validation, context)
            
            # State 4: GENERATE
            state = State.GENERATE
            prd = await self._generate(extracted, context)
            
            # State 5: ARCHIVE
            state = State.ARCHIVE
            await self._archive(prd, context)
            
            return self._build_output(prd, context)
            
        except Exception as e:
            await self._handle_error(state, e, context)
            raise
    
    async def _extract(self, content: str, context: dict) -> dict:
        """需求抽取（带重试 + 降级）"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return await self.extractor.extract(
                    content,
                    schema=REQ_SCHEMA,
                    timeout=60
                )
            except TimeoutError:
                if attempt == max_retries - 1:
                    # 降级到小模型
                    return await self.extractor.extract(
                        content,
                        schema=SIMPLE_SCHEMA,
                        model="qwen2"
                    )
                wait_exponential(attempt)
        
        # 最终降级：模板
        return self.extractor.fallback_template(content)
```

### 3.4.2 质量评分

```python
# src/capabilities/scorer.py
class QualityScorer:
    def calculate(self, req: dict) -> QualityReport:
        scores = {
            "completeness": self._calc_completeness(req),
            "clarity": self._calc_clarity(req),
            "consistency": self._calc_consistency(req),
        }
        
        overall = sum(scores.values()) / 3
        suggestions = self._generate_suggestions(scores, req)
        
        return QualityReport(
            completeness_score=scores["completeness"],
            clarity_score=scores["clarity"],
            consistency_score=scores["consistency"],
            overall_score=overall,
            missing_items=self._get_missing_items(req),
            suggestions=suggestions,
        )
    
    def _calc_completeness(self, req: dict) -> float:
        """完整率计算"""
        required_fields = [
            ("user_stories", 30),
            ("functional_requirements", 30),
            ("business_rules", 15),
            ("acceptance_criteria", 15),
            ("risks", 10),
        ]
        
        score = 0
        for field, weight in required_fields:
            if field in req and len(req[field]) > 0:
                score += weight
        
        return score
    
    def _calc_clarity(self, req: dict) -> float:
        """清晰度评分（基于格式规范）"""
        score = 100
        
        # 用户故事格式检查
        for story in req.get("user_stories", []):
            if not all(k in story for k in ["role", "need", "benefit"]):
                score -= 10
        
        # 验收标准可测试性检查
        for criteria in req.get("acceptance_criteria", []):
            if not self._is_testable(criteria):
                score -= 5
        
        return max(0, score)
```

---

## 3.5 测试计划（标准 Skill：63 用例）

| 类别 | 用例数 | 说明 |
|------|--------|------|
| **单元测试** | 35 | 抽取 15 + 校验 10 + 生成 10 |
| **集成测试** | 10 | 状态机流转 + 降级路径 |
| **E2E 测试** | 3 | 飞书/CLI/会议记录场景 |
| **安全测试** | 5 | Prompt Injection + 输入验证 |
| **性能测试** | 5 | 并发 10 文档/分钟 |
| **边界测试** | 5 | 空输入/超长输入/特殊字符 |
| **合计** | **63** | - |

---

## 3.6 评审意见

---

### Validator 评审意见 ✅

**评审时间**: 2026-03-14 09:20  
**评审人**: Validator

**通过项**:
- ✅ 测试计划完整（63 用例，符合标准 Skill）
- ✅ 安全测试已包含
- ✅ 性能测试指标明确

**建议**:
- 补充测试覆盖率目标（>80%）
- 增加降级路径专项测试

**结论**: 通过，进入 Round 4

---

### Architect 评审意见 ✅

**评审时间**: 2026-03-14 09:22  
**评审人**: Architect

**通过项**:
- ✅ 目录结构符合 Skill 规范
- ✅ 状态机实现清晰

**结论**: 通过，进入 Round 4

---

### Orchestrator 评审意见 ✅

**评审时间**: 2026-03-14 09:24  
**评审人**: Orchestrator

**决策**:
- ✅ 批准进入 Round 4（鲁棒性 + 成本优化）
- 实现规范完整

**下一步**: Round 4（鲁棒性 + 成本）  
**负责人**: Validator + Orchestrator  
**预计时间**: 20 分钟

---

## 3.7 修订历史

| 版本 | 日期 | 修改内容 | 修改人 |
|------|------|----------|--------|
| v1.0 | 2026-03-14 | 初始版本 | Engineer |
| v1.1 | 2026-03-14 | 评审修订（测试覆盖率目标） | Engineer |

---

_状态：评审通过，进入 Round 4_
