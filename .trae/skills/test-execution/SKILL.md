---
name: test-execution
description: 测试执行详细流程。test-agent 执行测试时调用。
---

# 测试执行详细流程

## 触发条件

- 收到 `[REQ_TEST]` 标签
- Master Agent 分发测试任务

## 执行流程

### 1. 读取任务上下文

```
读取 `.trae/current_task.md` 获取任务详情
```

### 2. 环境诊断（优先执行）

**目的**：区分用户环境问题 vs 项目问题。

```bash
pip show rewards-core
python -c "import cli; print(cli.__file__)"
```

**诊断流程**：

1. 检查 `rewards-core` 是否安装
2. 检查依赖是否完整（对比 `pyproject.toml`）
3. 如果环境异常 → 返回错误报告，提示用户执行 `pip install -e ".[test]"`

### 3. 全量验证

```bash
pytest tests/unit -v --cov=src
pytest tests/integration -v
```

### 4. E2E 验收（降级执行）

```bash
# 步骤 1：尝试 rscore
rscore --dev --headless

# 步骤 2：如果 rscore 失败，降级到 python main.py
python main.py --dev --headless
```

**降级逻辑**：

| rscore 结果 | python main.py 结果 | 结论 |
|-------------|---------------------|------|
| ✅ 通过 | - | 正常 |
| ❌ 失败 | ✅ 通过 | rscore 入口问题 |
| ❌ 失败 | ❌ 失败 | 业务逻辑问题 |
| ❌ 不可用 | ✅ 通过 | rscore 未安装 |
| ❌ 不可用 | ❌ 失败 | 业务逻辑问题 |

**注意**：必须执行降级测试，不能因为 rscore 失败就跳过。

### 5. 现场取证模式（Crime Scene Investigation）

**触发条件**：测试失败时

**执行步骤**：

1. 拦截异常，暂停测试脚本
2. 使用 Playwright MCP 捕获当前页面状态：
   - `playwright_get_visible_html`：获取 DOM 树
   - `playwright_console_logs`：获取控制台日志
   - `playwright_screenshot`：截图记录
3. 将终端错误与 DOM 快照打包
4. 写入 `.trae/test_report.md`

### 6. 输出状态标签

| 场景 | 输出标签 |
|------|----------|
| 测试全部通过 | `[REQ_DOCS]` |
| 测试有失败 | `[REQ_DEV]` + `.trae/test_report.md` 路径 |
| 连续 2 次 MCP 调用失败 | `[BLOCK_NEED_MASTER]` + 阻塞原因 |

## 覆写策略（强制）

**写入 `test_report.md` 必须使用完全覆写（Overwrite）模式，禁止追加写入（Append）。**

每次测试完成时，必须覆写整个文件，只保留最新一次的测试结果。

## 精简取证规范（强制）

**严禁保存完整 HTML**，仅允许提取以下三项：

### 1. Traceback（最后 10 行）

```
<最后抛出异常的 10 行 Traceback>
```

### 2. Accessibility Tree（关键节点）

使用 Playwright 的 Accessibility Tree API，仅提取关键节点：

```javascript
// 仅提取关键节点，忽略文本节点和布局节点
const snapshot = await page.accessibility.snapshot({ interestingOnly: true });
```

### 3. Network 请求（最后 3 个）

| URL | 状态码 | 方法 |
|-----|--------|------|
| <URL> | <状态码> | <GET/POST/...> |

## 错误归因与动作

| 错误定性 | 日志特征 | 智能体动作 |
|---------|---------|-----------|
| **环境问题** | `ModuleNotFoundError`<br>`command not found: rscore`<br>依赖版本不匹配 | 返回错误报告，提示用户修复环境 |
| **rscore 入口问题** | rscore 失败 + python main.py 通过 | 报告 rscore 入口问题，建议检查 `pyproject.toml` 配置 |
| **测试脚本过期** | `TimeoutError: waiting for selector`<br>接口断言失败但状态码 200/400<br>前端路由变更导致 404 | 自动修改 `tests/` 目录，自行重试，记录变更 |
| **业务逻辑错误** | rscore 和 python main.py 都失败<br>HTTP 500/502 服务端异常<br>积分数值断言失败 | 生成取证报告，输出 `[REQ_DEV]` |

## 输出格式（强制）

### 成功报告

写入 `.trae/test_report.md`：

```markdown
---
task_id: <任务ID>
status: success
coverage: <XX%>
created_at: <时间戳>
---

### 测试结果

- [x] `ruff check` 通过
- [x] `mypy` 通过
- 单元测试: X/Y 通过
- 集成测试: X/Y 通过
- 覆盖率: XX%
- E2E 验收: 通过
```

### 失败报告（业务逻辑错误）

写入 `.trae/test_report.md`：

```markdown
---
task_id: <任务ID>
status: failed
created_at: <时间戳>
---

### 测试结果

- [x] `ruff check` 通过
- [x] `mypy` 通过
- 单元测试: X/Y 通过
- 集成测试: X/Y 通过
- 覆盖率: XX%
- E2E 验收: 失败

### 精简取证

#### Traceback（最后 10 行）

```
<最后抛出异常的 10 行 Traceback>
```

#### Accessibility Tree（关键节点）

```
<Playwright 提取的 Accessibility Tree，仅限关键节点>
```

#### Network 请求（最后 3 个）

| URL | 状态码 | 方法 |
|-----|--------|------|
| <URL> | <状态码> | <GET/POST/...> |

### 诊断信息

- **错误类型**: 业务代码逻辑错误
- **受影响文件**: `<业务文件路径>`
- **预期行为**: <描述>
- **实际行为**: <描述>
```

## Memory MCP 知识库交互

1. **执行前 (`search_nodes`)**：检索目标页面的历史状态（如查询 "Login_Page_DOM" 或 "Cloudflare_Bypass"），获取最新的选择器或等待策略。
2. **禁止写入 Memory MCP**：如果发现反爬策略更新等需要记录的信息，返回给 Master Agent 处理。

## 截图落盘规范（物理执行序列）

### 触发时机

异常捕获后，立即执行截图。

### 执行序列（禁止跳过）

当捕获测试异常时，必须按以下顺序执行操作：

#### 1. 环境准备

首先在终端执行目录创建命令：

```bash
mkdir -p logs/screenshots
```

**注意**：此步骤不可跳过，Playwright 不会自动创建目录。

#### 2. 截取快照

通过 Playwright MCP 执行截图：

```python
page.screenshot(path=f"logs/screenshots/{task_id}_crash.png", full_page=True)
```

#### 3. 进程释放

立刻执行页面关闭，防止内存泄漏：

```python
page.close()
```

#### 4. 报告覆写

将图片路径注入 `.trae/test_report.md` 的【精简取证】模块末尾：

```markdown
#### 截图取证

![Crash_Site](../../logs/screenshots/{task_id}_crash.png)
```

### 约束

- 截图必须使用 `full_page=True` 参数
- 截图文件命名格式：`{task_id}_crash.png`
- 截图后必须关闭页面，防止无头浏览器进程残留
- 目录创建命令必须在截图前执行
