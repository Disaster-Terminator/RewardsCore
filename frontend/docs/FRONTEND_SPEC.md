# 前端开发规范与验收流程

## 目录

1. [验收测试流程](#验收测试流程)
2. [测试覆盖范围](#测试覆盖范围)
3. [运行测试](#运行测试)
4. [开发规范](#开发规范)
5. [常见问题排查](#常见问题排查)

---

## 验收测试流程

### 测试前准备

```bash
# 1. 启动后端服务
python web_server.py

# 2. 启动前端开发服务器（新终端）
cd frontend && npm run tauri dev

# 3. 等待服务完全启动（约10秒）
```

### 执行验收测试

```bash
# 运行自动化验收测试
python tests/frontend/test_frontend_acceptance.py
```

### 验收标准

所有测试项必须通过（13/13）：

| 类别 | 测试项 | 验证内容 |
|------|--------|----------|
| 基础连接 | 后端连接 | API `/api/health` 返回正常 |
| 基础连接 | 前端加载 | 页面标题正确显示 |
| Dashboard | 显示 | 统计卡片、控制按钮存在 |
| Dashboard | 启动任务 | 点击按钮后任务状态变化 |
| Dashboard | 停止任务 | 点击按钮后任务停止 |
| WebSocket | 消息接收 | 收到 `connected`、`log` 等消息 |
| 页面功能 | 配置页面 | 表单元素、开关存在 |
| 页面功能 | 日志页面 | 日志显示区域存在 |
| 页面功能 | 历史记录 | 历史列表存在 |
| 导航布局 | 侧边栏导航 | 所有页面可访问 |
| 导航布局 | 响应式布局 | desktop/laptop/tablet 正常 |
| 错误处理 | 控制台错误 | 无严重 JavaScript 错误 |
| 错误处理 | API错误处理 | 错误响应正确处理 |

---

## 测试覆盖范围

### 功能测试

- **启动/停止任务流程**
  - 验证按钮状态变化
  - 验证 API 调用成功
  - 验证后端状态同步

- **WebSocket 连接**
  - 验证连接建立
  - 验证消息类型正确
  - 验证断线重连机制

- **页面导航**
  - 验证所有路由可访问
  - 验证页面内容正确渲染

### UI 测试

- **响应式布局**
  - Desktop (1920x1080)
  - Laptop (1366x768)
  - Tablet (768x1024)

- **组件显示**
  - 统计卡片
  - 控制按钮
  - 表单元素
  - 日志区域

### 错误处理测试

- 控制台无严重错误
- API 错误响应正确处理
- 网络断开时 UI 反馈

---

## 运行测试

### 环境要求

- Python 3.10+
- Node.js 18+
- Playwright 浏览器已安装

```bash
# 安装 Playwright 浏览器（首次运行）
python -m playwright install chromium
```

### 测试命令

```bash
# 完整验收测试
python tests/frontend/test_frontend_acceptance.py

# 仅测试后端连接
curl http://localhost:8000/api/health

# 仅测试前端加载
curl http://localhost:3000/
```

### 测试输出解读

```
✅ 测试项: 通过信息     # 通过
❌ 测试项: 失败原因     # 失败，需要修复
```

---

## 开发规范

### 代码规范

1. **组件命名**
   - 页面组件：`XxxPage.tsx` 或 `Xxx.tsx`
   - 通用组件：`components/ui/` 目录
   - 使用 PascalCase

2. **样式规范**
   - 使用 Tailwind CSS
   - 颜色使用主题变量（`primary-500`、`danger-400` 等）
   - 暗色模式适配

3. **状态管理**
   - 全局状态使用 Zustand (`store/index.ts`)
   - 局部状态使用 `useState`

4. **API 调用**
   - 统一在 `api/index.ts` 中定义
   - 使用 async/await
   - 错误处理必须有用户反馈

### 提交前检查清单

- [ ] `npm run lint` 无错误
- [ ] `npm run build` 成功
- [ ] 验收测试全部通过
- [ ] 无 console.error 残留
- [ ] 新功能有对应测试

### 文件结构

```
frontend/src/
├── api/           # API 调用
├── components/    # 通用组件
│   └── ui/        # 基础 UI 组件
├── lib/           # 工具函数
├── pages/         # 页面组件
├── store/         # 状态管理
└── App.tsx        # 路由配置
```

---

## 常见问题排查

### 问题：前端无法连接后端

**检查步骤：**
```bash
# 1. 检查后端是否运行
curl http://localhost:8000/api/health

# 2. 检查端口占用
netstat -ano | findstr :8000

# 3. 检查 Vite 代理配置
# frontend/vite.config.ts 中 proxy 配置
```

### 问题：WebSocket 连接失败

**检查步骤：**
```bash
# 1. 检查 WebSocket 端点
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Key: test" -H "Sec-WebSocket-Version: 13" \
  http://localhost:8000/ws

# 2. 检查浏览器控制台 WebSocket 错误
```

### 问题：测试超时

**可能原因：**
- 服务未完全启动
- 网络延迟
- 页面加载慢

**解决方案：**
- 增加等待时间
- 检查服务状态
- 使用 `domcontentloaded` 替代 `networkidle`

### 问题：Rust 编译警告

**常见警告：**
- `unused import` - 开发模式下正常，release 会使用
- `dead_code` - 条件编译代码，release 会使用

**处理方式：**
- 仅修复 `error` 级别问题
- `warning` 级别在 release 构建时验证

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0 | 2026-02-17 | 初始版本，包含基础验收流程 |
