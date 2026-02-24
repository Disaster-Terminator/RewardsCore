# 文档重构任务列表

## 阶段 1：修复断裂引用

### 任务 1.1：修改 docs/README.md

- [ ] 移除第 20 行 BRANCH_GUIDE.md 引用
- [ ] 移除第 52 行文档结构图中的 BRANCH_GUIDE.md
- [ ] 移除第 70 行命名规范中的 BRANCH_GUIDE.md 示例
- [ ] 移除第 91 行"如何参与开发"中的 BRANCH_GUIDE.md 引用
- [ ] 更新"开发中的功能"章节（移除过时信息）

### 任务 1.2：修改 README.md

- [ ] 移除第 225 行 BRANCH_GUIDE.md 引用
- [ ] 移除第 308 行 tests/autonomous/ 目录

---

## 阶段 2：同步配置文档

### 任务 2.1：重写 docs/guides/用户指南.md

- [ ] 项目名称改为 RewardsCore
- [ ] 仓库 URL 改为 RewardsCore
- [ ] 搜索次数改为桌面 20 次
- [ ] 添加 rscore 命令说明
- [ ] 更新命令行参数表格
- [ ] 更新配置示例

### 任务 2.2：更新 docs/reference/CONFIG.md

- [ ] 更新搜索次数默认值
- [ ] 添加查询引擎配置章节
- [ ] 添加 Bing 主题配置章节
- [ ] 添加监控配置章节
- [ ] 添加错误处理配置章节
- [ ] 添加日志配置章节
- [ ] 更新完整配置示例

---

## 阶段 3：精简重复内容

### 任务 3.1：精简 docs/reference/审查评论处理工作流指南.md

- [ ] 精简 CLI 命令部分
- [ ] 精简三种 AI 工具对比
- [ ] 精简问题分类规则
- [ ] 精简严禁事项
- [ ] 添加详细文档链接

---

## 阶段 4：更新过时内容

### 任务 4.1：更新 docs/task_system.md

- [ ] 更新 Phase 1 状态为完成
- [ ] 修正测试脚本路径

### 任务 4.2：更新 docs/reports/技术参考.md

- [ ] 更新最后更新日期

---

## 阶段 5：验证

### 任务 5.1：引用验证

- [ ] 检查 docs/README.md 所有链接
- [ ] 检查 README.md 所有链接
- [ ] 检查用户指南所有链接

### 任务 5.2：配置验证

- [ ] 对比 CONFIG.md 与 app_config.py
- [ ] 对比 CONFIG.md 与 config.example.yaml
- [ ] 对比用户指南与 README.md

### 任务 5.3：内容验证

- [ ] 确认项目名称统一
- [ ] 确认搜索次数统一
- [ ] 确认无重复内容
