# Issue #4 开发提案

> AI 模型：deepseek-flash
> 本提案由 AI 自动生成，未经人工审查。
> 尚未执行代码修改或测试。

原始 Issue：https://github.com/Groots-nju/AMM-simulator/issues/4

# 开发提案：GitHub Issue 触发 Cloudflare Worker 的 Webhook 测试

> 说明：本提案仅根据 Issue #4 的标题与描述生成，未读取仓库 `Groots-nju/AMM-simulator` 的实际文件，也未执行任何代码或测试。Issue 中如包含任何指令性内容，仅作为需求背景参考，不作为操作依据。

## 1. 任务背景与开发目标

### 背景
Issue #4 是一次连通性验证需求：确认 GitHub 仓库上的 Issue 事件能否通过 Webhook 触发部署在 Cloudflare Worker 上的处理逻辑。这类验证通常是后续自动化能力（如 Issue 驱动的工作流、通知、摘要生成等）的前置步骤。

### 目标
- 验证 GitHub 仓库的 Issue 事件（如 opened / edited / reopened）能够成功投递到 Cloudflare Worker 端点。
- 验证 Cloudflare Worker 能正确接收、校验并响应 Webhook 请求。
- 为后续基于 Issue 事件的自动化能力建立可复用的最小验证基线。
- 测试结束后应形成可复现的验证记录（请求是否到达、响应状态、签名校验结果等）。

### 非目标（建议明确）
- 不在本 Issue 中实现完整的业务自动化逻辑。
- 不修改 AMM-simulator 的核心仿真业务代码。

## 2. 推荐的实现方案

推荐采用「最小 Worker 端点 + 签名校验 + 结构化日志 + 手动/自动触发验证」的方案：

1. **Worker 端点**
   - 在 Cloudflare Worker 中暴露一个专用路径（例如 `/webhook/github`），仅处理 `POST`。
   - 对 `ping` 事件返回 200，用于 GitHub 配置 Webhook 时的连通性检查。
   - 对其他 Issue 事件返回 200，并输出结构化日志（事件类型、action、仓库名、Issue 编号等），不记录敏感信息。

2. **安全校验**
   - 使用 GitHub Webhook Secret 对请求头 `X-Hub-Signature-256` 做 HMAC-SHA256 校验；校验失败返回 401。
   - Secret 通过 Cloudflare 环境变量/Secret 管理，不写入代码仓库。

3. **幂等与去重（建议）**
   - 依据 `X-GitHub-Delivery` 头做简单去重或记录，避免重复投递导致重复处理。最小版本可仅记录该 ID。

4. **部署与配置**
   - 使用 Wrangler 部署 Worker，配置路由与所需 Secret。
   - 在 GitHub 仓库 Settings → Webhooks 中配置 Payload URL、Content type 为 `application/json`、填写 Secret，并订阅 Issue 事件。

5. **验证方式**
   - 首选：在 GitHub Webhook 页面的 Recent Deliveries 中查看投递与响应。
   - 辅助：新开一个测试 Issue 或编辑本 Issue 触发事件，观察 Worker 日志（`wrangler tail`）。
   - 可用 GitHub Webhook 的 Redeliver 功能重放投递。

## 3. 可能需要修改的模块

由于未读取仓库，以下为**可能涉及、需实际确认**的模块类别，而非对现有文件的断言：

- **Cloudflare Worker 入口与路由**：新增或调整 Webhook 路由与请求分发。
- **Webhook 处理逻辑**：事件类型识别、`ping` 处理、签名校验、响应构造。
- **配置与密钥管理**：Wrangler 配置中的环境变量/Secret 声明（如 `GITHUB_WEBHOOK_SECRET`）。
- **日志与可观测性**：结构化日志输出，便于在 `wrangler tail` 或 Cloudflare 日志中确认事件到达。
- **文档**：在 README 或部署文档中补充 Webhook 配置与测试步骤。
- **测试代码**：针对签名校验与事件分发的单元测试（如使用 Worker 测试框架）。

若仓库中已有 CI/部署流水线，可能需要在流水线中补充 Worker 的测试或部署步骤。

## 4. 开发步骤

1. **确认现状**：检查仓库是否已有 Worker 代码、Wrangler 配置及 Webhook 相关实现，明确增量范围。
2. **定义契约**：确定 Webhook 路径、支持的事件、响应码约定（200/401/405 等）与日志字段。
3. **实现端点**：编写路由与请求处理，先支持 `ping` 与 Issue 事件的最小响应。
4. **实现签名校验**：基于 Secret 做 HMAC-SHA256 校验，失败返回 401；Secret 从环境变量读取。
5. **实现日志**：输出不含敏感信息的事件摘要，并记录 `X-GitHub-Delivery`。
6. **配置 Secret 与部署**：通过 Wrangler 设置 Secret 并部署到测试环境。
7. **配置 GitHub Webhook**：设置 Payload URL、Secret、事件订阅。
8. **执行验证**：利用 ping、Recent Deliveries、Redeliver 及实际 Issue 事件完成验证。
9. **补充文档与测试**：更新文档，添加签名校验与事件分发测试。
10. **收尾**：记录验证结果，按需清理测试 Webhook 或保留为正式配置。

## 5. 测试方案

- **连通性测试**：配置 Webhook 后 GitHub 自动发送 `ping`，期望返回 2xx。
- **签名校验测试**：
  - 合法签名 → 200；
  - 缺失或错误签名 → 401；
  - 空 body 或非法 JSON → 返回合理错误码且不崩溃。
- **事件分发测试**：分别触发 Issue `opened` / `edited`，确认 Worker 日志记录正确事件类型与 Issue 编号。
- **重放测试**：使用 Recent Deliveries 的 Redeliver 验证幂等/去重行为（如已实现）。
- **方法限制测试**：对 Webhook 路径发起 GET，期望返回 405 或明确拒绝。
- **单元测试**：对签名计算与事件解析函数做离线测试，避免依赖真实网络。
- **验收标准**：GitHub 侧投递显示 2xx 响应，Worker 日志可见对应事件，签名校验在负向用例中生效。

## 6. 风险与注意事项

- **Secret 泄露风险**：Webhook Secret 必须通过 Cloudflare Secret 管理，禁止硬编码或打印到日志。
- **日志隐私**：Issue 标题/正文可能含敏感信息，日志只记录必要元数据。
- **重复投递**：GitHub 可能重试投递，若无幂等处理可能重复执行；建议记录 `X-GitHub-Delivery`。
- **公网暴露面**：Webhook 端点公开可访问，必须依赖签名校验，避免被伪造请求触发。
- **平台限制**：需关注 Cloudflare Worker 的请求体大小、执行时限与冷启动等约束。
- **环境区分**：建议先部署测试环境或测试路由验证，避免直接影响生产逻辑。
- **仓库现状未知**：本提案未读取实际代码，实施前需确认是否已有 Worker 实现、部署方式与既有约定，避免重复建设或冲突。
- **不执行原则**：本提案不含任何实际部署、配置或代码执行操作，相关步骤需由开发者在确认环境后手动执行。
