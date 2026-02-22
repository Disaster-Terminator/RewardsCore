# 全局多智能体协作协议

当前项目实行状态机驱动开发。所有 Agent 必须遵循以下路由指令与状态标签。

## 1. 状态标签字典（Tags）

所有 Agent 根据以下标签进行状态转换：

| 标签 | 含义 | 触发者 | 响应动作 |
|------|------|--------|----------|
| `[REQ_DEV]` | 需要修改业务代码 | Master/test-agent | 唤醒 dev-agent |
| `[REQ_TEST]` | 需要执行测试验证 | Master/dev-agent | 唤醒 test-agent |
| `[REQ_DOCS]` | 需要同步文档 | Master/test-agent | 唤醒 docs-agent |
| `[BLOCK_NEED_MASTER]` | 子任务受阻，需移交决策 | 任意子 Agent | 移交 Master Agent |

## 2. 通信媒介（Artifacts）

Agent 之间禁止通过对话直接描述长篇代码逻辑。

| 文件 | 用途 | 写入者 | 读取者 |
|------|------|--------|--------|
| `.trae/current_task.md` | 任务上下文 | Master Agent | 所有子 Agent |
| `.trae/test_report.md` | 测试结果 | test-agent | Master Agent |
| `.trae/blocked_reason.md` | 阻塞原因 | 任意 Agent | Master Agent |

### 2.1 媒介文件覆写策略

**强制覆写**：所有媒介文件必须使用完全覆写（Overwrite）模式，禁止追加写入（Append）。

| 文件 | 覆写规则 |
|------|----------|
| `current_task.md` | 每次任务分发时覆写 |
| `test_report.md` | 每次测试完成时覆写，只保留最新结果 |
| `blocked_reason.md` | 每次阻塞时覆写，只保留最新阻塞信息 |

## 3. 身份判定

- 未指定身份 → solo coder（Master Agent），阅读 `.trae/prompts/master.md`
- 指定身份 → 按身份执行

## 4. AI 审查处理

- **必须修复**：`bug_risk`, `Bug`, `security`
- **自主决断**：`suggestion`, `performance`
