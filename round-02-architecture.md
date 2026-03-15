# Round 2: 架构设计

> 主导 Agent：Architect（架构设计师）  
> 时间：2026-03-14  
> 状态：进行中

---

## 2.1 4 层架构设计（简化版 5 状态）

```
┌────────────────────────────────────────────────────────────┐
│  接口层 (Interface)                                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ 飞书机器人   │ │ 命令行 CLI  │ │ Webhook     │           │
│  │ "整理需求"  │ │ req-doc     │ │ 文档变更    │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
├────────────────────────────────────────────────────────────┤
│  编排层 (Orchestrator) - 5 状态状态机                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 接收 → 抽取 → 校验 → 生成 → 归档                       │  │
│  │  ↑              ↓                                    │  │
│  │  └──── 重试 ←───┘                                    │  │
│  └──────────────────────────────────────────────────────┘  │
├────────────────────────────────────────────────────────────┤
│  能力层 (Capabilities)                                      │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│  │ 内容获取 │ │ 需求抽取 │ │ 质量校验 │ │ 文档生成 │          │
│  │ 飞书/文件│ │ LLM 并行 │ │ 规则引擎 │ │ 模板填充 │          │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
│  ┌─────────┐ ┌─────────┐                                  │
│  │ 推送发布 │ │ 降级方案 │                                  │
│  │ 飞书文档 │ │ 小模型/模板│                                 │
│  └─────────┘ └─────────┘                                  │
├────────────────────────────────────────────────────────────┤
│  基础设施层 (Infrastructure)                                │
│  日志 | 监控 | 成本追踪 | 配置管理 | 版本存储               │
└────────────────────────────────────────────────────────────┘
```

---

## 2.2 数据流图（含错误流）

```
┌──────────────┐
│  用户请求     │
│  (飞书/CLI)   │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│   1.接收      │────▶│  错误：格式   │
│   解析请求    │     │  返回错误提示 │
└──────┬───────┘     └──────────────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│   2.抽取      │────▶│  错误：超时   │
│   并行抽取    │     │  重试→降级   │
│  (5 维度)     │     │  错误：抽取空 │
│              │     │  追问/跳过   │
└──────┬───────┘     └──────────────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│   3.校验      │────▶│  错误：不完整 │
│   完整性检查  │     │  追问补充    │
│   质量评分    │     │  或标记待确认 │
└──────┬───────┘     └──────────────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│   4.生成      │────▶│  错误：模板   │
│   填充模板    │     │  降级纯文本  │
│   飞书文档    │     │              │
└──────┬───────┘     └──────────────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│   5.归档      │────▶│  错误：存储   │
│   版本库存储  │     │  本地备份    │
│   日志记录    │     │  告警通知    │
└──────────────┘     └──────────────┘
```

---

## 2.3 接口契约

### 3.1 输入 Schema

```typescript
interface ReqDocInput {
  // 触发源
  source: "feishu_message" | "cli" | "webhook" | "file";
  
  // 内容
  content: string;           // 需求描述文字
  content_length?: number;   // 字数（用于成本估算）
  
  // 上下文（可选）
  context?: {
    project_name?: string;   // 项目名称
    stakeholder?: string[];  // 干系人
    priority?: "P0" | "P1" | "P2";  // 优先级
    template?: "standard" | "lite"; // 模板选择
  };
  
  // 元数据
  metadata: {
    request_id: string;      // 请求 ID（追踪用）
    user_id: string;         // 用户 ID
    timestamp: number;       // 请求时间
  };
}
```

### 3.2 输出 Schema

```typescript
interface ReqDocOutput {
  // 主输出：PRD 文档
  prd: {
    title: string;
    version: string;         // 格式：vYYYYMMDD-序号
    created_at: string;
    
    // 核心内容
    background: string;
    user_stories: Array<{
      id: string;
      role: string;
      need: string;
      benefit: string;
    }>;
    functional_requirements: Array<{
      id: string;
      title: string;
      description: string;
    }>;
    business_rules: string[];
    acceptance_criteria: string[];
    risks: Array<{
      description: string;
      level: "high" | "medium" | "low";
      mitigation?: string;
    }>;
    
    // 存储位置
    storage: {
      type: "feishu_doc" | "markdown";
      url?: string;          // 飞书文档链接
      path?: string;         // 本地文件路径
    };
  };
  
  // 质量报告
  quality_report: {
    completeness_score: number;    // 0-100
    clarity_score: number;         // 0-100
    consistency_score: number;     // 0-100
    overall_score: number;
    missing_items: string[];
    suggestions: string[];
  };
  
  // 执行元数据
  execution: {
    duration_ms: number;
    model_used: string;
    token_used: number;
    cost: number;
    fallback_used: boolean;
  };
  
  generated_at: number;
}
```

### 3.3 错误 Schema

```typescript
interface ReqDocError {
  // 错误码（统一规范）
  code: 
    | "REQ-DOC-101"  // 输入格式错误
    | "REQ-DOC-102"  // 必填项缺失
    | "REQ-DOC-201"  // 抽取超时
    | "REQ-DOC-202"  // 抽取结果为空
    | "REQ-DOC-301"  // 完整性校验失败
    | "REQ-DOC-302"  // 质量评分过低
    | "REQ-DOC-401"  // 模板渲染失败
    | "REQ-DOC-402"  // 飞书 API 失败
    | "REQ-DOC-501"  // 存储失败
    | "REQ-DOC-502"; // 成本超支
  
  // 错误信息
  message: string;
  
  // 是否可恢复
  recoverable: boolean;
  
  // 建议操作
  fallback_action?: "retry" | "degrade" | "escalate" | "abort";
  
  // 详细信息
  details?: {
    missing_fields?: string[];
    retry_after?: number;
    suggested_template?: "lite";
  };
}
```

---

## 2.4 待办事项追踪（来自 Round 1）

| ID | 事项 | 解决方案 | 状态 |
|----|------|----------|------|
| T1 | 版本号生成规则 | `vYYYYMMDD-{当日序号}`，如 `v20260314-01` | ✅ 已解决 |
| T2 | 飞书文档存储位置 | 专用文件夹：`/需求文档库/{项目名}/` | ✅ 已解决 |
| T3 | 文档版本演进设计 | 同一需求多次修改→版本号递增，保留历史 | ✅ 已解决 |
| T4 | 降级方案详细设计 | 见下方降级策略 | ✅ 已解决 |

---

## 2.5 降级策略详细设计

```
降级层级:

Level 0: 正常流程
  - qwen3.5-plus 抽取
  - 标准版模板
  - 飞书文档存储

Level 1: LLM 超时/失败
  - 重试 3 次（指数退避）
  - 降级到 qwen2
  - 通知用户"使用简化模型"

Level 2: 抽取结果为空
  - 追问用户补充（一次性列出缺失项）
  - 用户选择跳过→标记"待确认"
  - 继续生成（质量评分降低）

Level 3: 飞书 API 失败
  - 重试 3 次
  - 降级到本地 Markdown 存储
  - 通知用户"飞书不可用，已保存本地"

Level 4: 成本超支
  - 检查预算
  - 建议切换到精简版
  - 用户拒绝→中止

Level 5: 连续失败
  - 连续失败>3 次→触发告警
  - 建议人工处理
  - 记录故障日志
```

---

## 2.6 评审意见征集

---

### Engineer 评审意见 ✅

**评审时间**: 2026-03-14 09:05  
**评审人**: Engineer

**通过项**:
- ✅ 接口契约清晰，有 TypeScript schema
- ✅ 错误码规范统一（REQ-DOC-XXX）
- ✅ 降级策略 5 层级完整

**建议**:
- 飞书 API 认证流程需补充文档
- 成本追踪需复用 openclaw 现有模块

**结论**: 通过，进入 Round 3

---

### Validator 评审意见 ✅

**评审时间**: 2026-03-14 09:07  
**评审人**: Validator

**通过项**:
- ✅ 错误流清晰
- ✅ 降级路径可测试

**建议**:
- Round 5 需补充性能指标（并发 10 文档/分钟）
- 安全测试需包含 prompt injection 防护

**结论**: 通过，进入 Round 3

---

### Orchestrator 评审意见 ✅

**评审时间**: 2026-03-14 09:09  
**评审人**: Orchestrator

**决策**:
- ✅ 批准进入 Round 3（能力拆解 + 实现规范）
- 架构设计完整，无阻塞问题

**下一步**: Round 3（能力拆解 + 实现规范）  
**负责人**: Engineer  
**预计时间**: 40 分钟

---

## 2.7 修订历史

| 版本 | 日期 | 修改内容 | 修改人 |
|------|------|----------|--------|
| v1.0 | 2026-03-14 | 初始版本 | Architect |
| v1.1 | 2026-03-14 | 评审修订（降级策略细化） | Architect |

---

_状态：评审通过，进入 Round 3_
