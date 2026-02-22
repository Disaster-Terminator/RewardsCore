---
name: test-execution
description: 测试执行详细流程。test-agent 执行测试时调用。
---

# 测试执行详细流程

## 1. 环境诊断（优先执行）

**目的**：区分用户环境问题 vs 项目问题。

```bash
# 检查是否正确安装项目
pip show rewards-core
# 或
python -c "import cli; print(cli.__file__)"
```

**诊断流程**：

1. 检查 `rewards-core` 是否安装
2. 检查依赖是否完整（对比 `pyproject.toml`）
3. 如果环境异常 → 返回错误报告，提示用户执行 `pip install -e ".[test]"`

## 2. 全量验证

```bash
pytest tests/unit -v --cov=src
pytest tests/integration -v
```

## 3. E2E 验收

**降级执行策略**：

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

## 4. 页面观察（Playwright MCP）

**目的**：通过 Playwright MCP 观察页面真实环境，验证程序运行状态。

**使用场景**：

- CLI 无头验收运行时，观察浏览器页面状态
- 检查登录、搜索、任务执行等关键流程
- 截图记录问题现场

**关键工具**：

- `playwright_navigate`：导航到目标页面
- `playwright_screenshot`：截图记录
- `playwright_get_visible_text`：获取页面文本
- `playwright_evaluate`：执行 JS 检查 DOM

## 错误归因与动作

| 错误定性 | 日志特征 | 智能体动作 |
|---------|---------|-----------|
| **环境问题** | `ModuleNotFoundError`<br>`command not found: rscore`<br>依赖版本不匹配 | 返回错误报告，提示用户修复环境 |
| **rscore 入口问题** | rscore 失败 + python main.py 通过 | 报告 rscore 入口问题，建议检查 `pyproject.toml` 配置 |
| **测试脚本过期** | `TimeoutError: waiting for selector`<br>接口断言失败但状态码 200/400<br>前端路由变更导致 404 | 自动修改 `tests/` 目录，自行重试，记录变更 |
| **业务逻辑错误** | rscore 和 python main.py 都失败<br>HTTP 500/502 服务端异常<br>积分数值断言失败 | 生成 `failed` 报告，移交 dev-agent |

## 输出格式（强制）

### 成功报告

```
---
task_id: <任务ID>
status: success
coverage: <XX%>
---

### 测试结果

- [ ] `ruff check` 通过
- [ ] `mypy` 通过
- 单元测试: X/Y 通过
- 集成测试: X/Y 通过
- 覆盖率: XX%
- E2E 验收: 通过

### 测试代码同步说明

（如有修改 `tests/` 目录，在此说明变更）
```

### 失败报告（业务逻辑错误）

```
---
task_id: <任务ID>
status: failed
---

### 错误溯源

[Error Traceback 或 Pytest 报错输出]

### 诊断信息

- **错误类型**: 业务代码逻辑错误
- **受影响文件**: `<业务文件路径>`
- **预期行为**: <描述>
- **实际行为**: <描述>

### Playwright 日志

[关键节点的 DOM 结构 / 控制台报错]
```

## Memory MCP 知识库交互

1. **执行前 (`search_nodes`)**：检索目标页面的历史状态（如查询 "Login_Page_DOM" 或 "Cloudflare_Bypass"），获取最新的选择器或等待策略。
2. **禁止写入 Memory MCP**：如果发现反爬策略更新等需要记录的信息，返回给 Master Agent 处理。
