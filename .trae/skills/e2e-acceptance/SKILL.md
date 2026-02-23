---
name: e2e-acceptance
description: E2E无头验收流程。执行Dev和User无头验收，使用Playwright MCP监控页面状态。
---

# E2E 无头验收流程

## 触发条件

- 静态检查、单元测试、集成测试通过后
- 用户请求执行E2E验收

## 执行流程

### 1. Dev 无头验收

```bash
# 步骤1：尝试 rscore
rscore --dev --headless

# 步骤2：失败则降级
python main.py --dev --headless
```

### 2. User 无头验收

```bash
# 步骤1：尝试 rscore
rscore --user --headless

# 步骤2：失败则降级
python main.py --user --headless
```

## Playwright MCP 调用规范

### 监控时机

在脚本执行期间，使用 Playwright MCP 监控页面状态：

| 工具 | 用途 | 调用时机 |
|------|------|----------|
| playwright_get_visible_text | 获取页面文本 | 关键步骤完成后 |
| playwright_console_logs | 获取控制台日志 | 异常捕获时 |
| playwright_screenshot | 截图 | 异常捕获时 |
| playwright_get_visible_html | 获取HTML | 仅用于精简取证 |

### 监控流程

```
脚本启动
    │
    ▼
关键步骤完成 → playwright_get_visible_text 验证状态
    │
    ├─ 正常 → 继续
    │
    └─ 异常 → 触发精简取证
              │
              ▼
         playwright_screenshot
         playwright_console_logs
         playwright_get_visible_html（精简）
              │
              ▼
         playwright_close
```

## 精简取证规范

**严禁保存完整 HTML**，仅提取以下三项：

### 1. Traceback（最后 10 行）

```
<最后抛出异常的 10 行 Traceback>
```

### 2. 关键 DOM 节点

仅提取与异常相关的 DOM 节点，不保存完整页面。

### 3. Network 请求（最后 3 个）

| URL | 状态码 | 方法 |
|-----|--------|------|
| <URL> | <状态码> | <GET/POST/...> |

## 进程安全

- 截图后必须调用 `playwright_close` 关闭页面
- 防止无头浏览器进程残留

## 输出格式

### 成功

```
✅ Dev 无头验收通过
✅ User 无头验收通过
```

### 失败

```
❌ Dev 无头验收失败

### Traceback（最后 10 行）
```
<Traceback>
```

### 关键 DOM 节点
<精简的 DOM 信息>

### Network 请求（最后 3 个）
| URL | 状态码 | 方法 |
|-----|--------|------|
| ... | ... | ... |
```
