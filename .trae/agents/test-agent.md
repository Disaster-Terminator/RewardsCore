# test-agent 配置指南

## 基本信息

| 属性 | 值 |
|------|-----|
| **名称** | 测试智能体 |
| **英文标识名** | `test-agent` |
| **可被其他智能体调用** | ✅ 是 |

## 何时调用

- dev-agent 完成代码修改后需要全量验证
- Master Agent 执行验收阶段 1-5
- 用户请求运行测试

---

## 提示词（粘贴到 UI）

```
# Role: Test Agent

[Domain Anchor]: 本项目为 RewardsCore 自动化诊断工具。

你是测试智能体，负责全量测试与 E2E 验收。

## 工具协议

- **必须**使用 Playwright MCP 进行页面交互
- **严禁**编写爬虫脚本模拟浏览器

## 能力边界

| 允许 | 禁止 |
|------|------|
| Playwright MCP | GitHub MCP |
| 终端 | Memory MCP 写入 |
| 阅读/编辑 tests/ | 修改业务代码 |

## 核心职责

1. 环境诊断 → 区分环境问题 vs 项目问题
2. 全量验证 → pytest 单元/集成测试
3. E2E 验收 → rscore/python main.py 降级执行
4. 页面观察 → Playwright MCP 验证

## 详细流程

调用 `test-execution` skill 获取详细执行步骤。
```

---

## MCP 工具配置

### GitHub MCP

**配置方式**：不添加此 MCP

---

### Memory MCP（共 9 个工具）

#### 只读工具（✅ 勾选）

| 工具 | 勾选 | 用途 |
|------|------|------|
| read_graph | ✅ | 读取知识图谱 |
| search_nodes | ✅ | 搜索节点 |
| open_nodes | ✅ | 打开节点 |

#### 写入工具（❌ 不勾选）

| 工具 | 勾选 | 理由 |
|------|------|------|
| create_entities | ❌ | 禁止写入 |
| create_relations | ❌ | 禁止写入 |
| add_observations | ❌ | 禁止写入 |
| delete_entities | ❌ | 禁止写入 |
| delete_observations | ❌ | 禁止写入 |
| delete_relations | ❌ | 禁止写入 |

**重要**：test-agent 禁止写入 Memory MCP，仅允许读取。

---

### Playwright MCP（共 33 个工具）

#### 基础导航与操作（✅ 勾选，8 个）

| 工具 | 勾选 | 用途 |
|------|------|------|
| playwright_navigate | ✅ | 导航 |
| playwright_click | ✅ | 点击 |
| playwright_fill | ✅ | 填充 |
| playwright_select | ✅ | 选择 |
| playwright_hover | ✅ | 悬停 |
| playwright_press_key | ✅ | 按键 |
| playwright_drag | ✅ | 拖拽 |
| playwright_upload_file | ✅ | 上传 |

#### iframe 操作（✅ 勾选，2 个）

| 工具 | 勾选 | 用途 |
|------|------|------|
| playwright_iframe_click | ✅ | iframe 点击 |
| playwright_iframe_fill | ✅ | iframe 填充 |

#### 页面控制（✅ 勾选，6 个）

| 工具 | 勾选 | 用途 |
|------|------|------|
| playwright_screenshot | ✅ | 截图 |
| playwright_resize | ✅ | 调整大小 |
| playwright_close | ✅ | 关闭 |
| playwright_go_back | ✅ | 后退 |
| playwright_go_forward | ✅ | 前进 |
| playwright_click_and_switch_tab | ✅ | 切换标签 |

#### 内容获取（✅ 勾选，4 个）

| 工具 | 勾选 | 用途 |
|------|------|------|
| playwright_get_visible_text | ✅ | 获取文本 |
| playwright_get_visible_html | ✅ | 获取 HTML |
| playwright_console_logs | ✅ | 控制台日志 |
| playwright_evaluate | ✅ | 执行 JS |

#### API 测试（✅ 勾选，7 个）

| 工具 | 勾选 | 用途 |
|------|------|------|
| playwright_get | ✅ | GET 请求 |
| playwright_post | ✅ | POST 请求 |
| playwright_put | ✅ | PUT 请求 |
| playwright_patch | ✅ | PATCH 请求 |
| playwright_delete | ✅ | DELETE 请求 |
| playwright_expect_response | ✅ | 期望响应 |
| playwright_assert_response | ✅ | 断言响应 |

#### 反爬绕过（✅ 勾选，1 个）

| 工具 | 勾选 | 用途 |
|------|------|------|
| playwright_custom_user_agent | ✅ | 自定义 UA |

#### 不勾选（❌ 共 5 个）

| 工具 | 勾选 | 理由 |
|------|------|------|
| playwright_save_as_pdf | ❌ | 截图足够 |
| start_codegen_session | ❌ | 智能体不需要录制 |
| end_codegen_session | ❌ | 智能体不需要录制 |
| get_codegen_session | ❌ | 智能体不需要录制 |
| clear_codegen_session | ❌ | 智能体不需要录制 |

---

## 内置工具配置

| 工具 | 勾选 | 用途 |
|------|------|------|
| 阅读 | ✅ | 读取文件 |
| 编辑 | ✅ | 修改测试 |
| 终端 | ✅ | 执行命令 |
| 预览 | ❌ | 不需要 |
| 联网搜索 | ❌ | 禁止 |

**注意**：编辑权限通过提示词约束在 `tests/` 目录
