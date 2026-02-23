# test-agent 执行问题分析

## 核心问题

**Master Agent 无法看到子 agent 的执行过程，只能看到最终结果**

这导致：
1. 我无法判断 test-agent 是否正确执行了任务
2. 我无法发现 test-agent 的决策错误
3. 需要用户提醒才能发现问题

## test_report.md 矛盾分析

### 矛盾 1：阶段 5 状态不一致

```
#### 阶段 5：User 无头验证
- 状态：跳过（无会话文件）
```

但后面又写了：

```
#### 阶段 5: User 无头验证
**命令**: `python main.py --user --headless`
**状态**: 失败
**Traceback**: RuntimeError: Headless 模式需要会话文件...
```

**结论**：test-agent 实际执行了阶段 5，失败了，但报告说"跳过"。

### 矛盾 2：会话文件判断错误

用户说"事实上有会话文件"，但 test-agent 判断"无会话文件"。

**可能原因**：
1. test-agent 没有检查会话文件是否存在
2. 检查路径错误
3. 二维矩阵干扰了判断流程

### 矛盾 3：没有使用 Playwright MCP

test-execution/SKILL.md 第 97-109 行明确说：

```markdown
### 5. 现场取证模式（Crime Scene Investigation）

**触发条件**：测试失败时

**执行步骤**：
1. 拦截异常，暂停测试脚本
2. 使用 Playwright MCP 捕获当前页面状态：
   - `playwright_get_visible_html`：获取 DOM 树
   - `playwright_console_logs`：获取控制台日志
   - `playwright_screenshot`：截图记录
```

但 test-agent 完全没有调用 Playwright MCP。

## 根因分析

### 问题 1：二维矩阵干扰了流程

二维矩阵的第一行：

```
| ✅ 成功（Exit 0） | - | 验证通过 | `[REQ_DOCS]` |
```

test-agent 看到 rscore 成功（Exit 0），就直接判定"验证通过"，跳过了：
- 检查会话文件
- 执行阶段 5
- 使用 Playwright MCP 观察

### 问题 2：Skill 与实际执行不一致

SKILL.md 说"测试失败时使用 Playwright MCP"，但：
- 阶段 4 rscore 成功 → 没触发
- 阶段 5 失败 → 应该触发，但没有

### 问题 3：Master Agent 缺乏监控能力

我看不到子 agent 的执行过程，无法：
- 判断它是否正确执行了 Skill
- 发现它的决策错误
- 验证它的报告是否准确

## 改进方向

### 方向 1：增强 Master Agent 监控能力

**方案 A**：子 agent 返回详细执行日志
- 不仅是结果摘要，还要包含执行步骤
- Master Agent 可以验证执行过程

**方案 B**：Master Agent 读取 test_report.md 后分析
- 主动检查报告中的矛盾
- 发现异常时追问子 agent

### 方向 2：修正二维矩阵逻辑

当前逻辑：rscore 成功 → 验证通过

应该改为：
1. rscore 成功 → 检查会话文件 → 执行阶段 5
2. 阶段 5 成功 → 验证通过
3. 阶段 5 失败 → 使用 Playwright MCP 取证

### 方向 3：明确 Playwright MCP 使用时机

**问题**：是每次测试都调用，还是只在开发阶段？

**建议**：
- **每次 E2E 测试都调用**：观察页面状态，验证程序行为
- **测试失败时额外调用**：现场取证

## 待确认问题

1. **Playwright MCP 使用频率**：每次 E2E 测试都调用，还是只在失败时？
2. **会话文件检查**：应该在哪里检查？阶段 4 之前？阶段 5 之前？
3. **Master Agent 监控**：如何让 Master Agent 能看到子 agent 的执行过程？
