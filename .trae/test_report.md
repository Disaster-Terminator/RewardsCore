---
task_id: <任务ID>
status: pending | success | failed
created_at: <时间戳>
---

### 测试结果

- [ ] `ruff check` 通过
- [ ] `mypy` 通过
- 单元测试: X/Y 通过
- 集成测试: X/Y 通过
- 覆盖率: XX%
- E2E 验收: 待执行

### 精简取证（失败时填写）

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

- **错误类型**: <类型>
- **受影响文件**: `<文件路径>`
- **预期行为**: <描述>
- **实际行为**: <描述>
