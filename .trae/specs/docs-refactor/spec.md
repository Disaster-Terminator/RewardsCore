# 文档重构规范

## 概述

重构 docs 文件夹中的所有文件和 README.md，确保文档符合当前项目实际情况，消除重复和冗余。

## 目标

1. 修复所有断裂引用
2. 同步配置文档与代码
3. 精简重复内容
4. 更新过时信息

## 范围

### 需要修改的文件

| 文件 | 操作类型 | 优先级 |
|------|----------|--------|
| `docs/README.md` | 重写 | 高 |
| `README.md` | 修改 | 高 |
| `docs/guides/用户指南.md` | 重写 | 高 |
| `docs/reference/CONFIG.md` | 更新 | 高 |
| `docs/reference/审查评论处理工作流指南.md` | 精简 | 中 |
| `docs/task_system.md` | 更新 | 中 |
| `docs/reports/技术参考.md` | 更新日期 | 低 |

### 不修改的文件

- `docs/reference/SCHEDULER.md` - 内容正确
- `docs/reference/评论处理系统说明.md` - 完整系统文档
- `docs/reference/archive/*` - 归档文档
- `docs/reports/archive/*` - 归档文档
- `docs/tasks/archive/*` - 归档文档
- `CHANGELOG.md` - 版本历史

## 详细规范

### 1. docs/README.md

**当前问题**：
- 引用不存在的 `reference/BRANCH_GUIDE.md`
- 文档结构图包含不存在的文件
- 归档目录引用路径错误

**修改要求**：
- 移除所有 `BRANCH_GUIDE.md` 引用（第 20、52、70、91 行）
- 更新文档结构图，移除 `BRANCH_GUIDE.md`
- 修正"开发中的功能"章节（移除或更新过时信息）
- 更新"如何参与开发"章节，移除 BRANCH_GUIDE 引用

**保留内容**：
- 文档索引功能
- 导航表格结构
- 贡献指南章节

### 2. README.md

**当前问题**：
- 第 225 行引用不存在的 `docs/reference/BRANCH_GUIDE.md`
- 第 308 行项目结构列出 `tests/autonomous/`（目录不存在）

**修改要求**：
- 移除第 225 行的 BRANCH_GUIDE 引用
- 移除第 308 行的 `tests/autonomous/` 目录

**保留内容**：
- 其他所有内容保持不变

### 3. docs/guides/用户指南.md

**当前问题**：
- 项目名称使用 `ms-rewards-automator`
- 搜索次数 30+20 与当前配置 20 不一致
- 缺少 `rscore` 命令说明

**修改要求**：
- 项目名称改为 `RewardsCore`
- 仓库 URL 改为 `RewardsCore`
- 搜索次数改为桌面 20 次
- 添加 `rscore` 命令说明
- 更新命令行参数表格：
  - 默认模式：20 次搜索
  - `--user`：3 次搜索
  - `--dev`：2 次搜索
- 更新配置示例中的搜索次数

**保留内容**：
- 快速开始结构
- 配置文件说明格式
- 故障排除章节

### 4. docs/reference/CONFIG.md

**当前问题**：
- 搜索次数过时（desktop_count=30, mobile_count=20）
- 缺少配置节：query_engine, bing_theme, monitoring, error_handling, logging

**修改要求**：
- 更新搜索次数默认值（desktop_count=20, mobile_count=0）
- 添加缺失的配置章节：
  - 十、查询引擎配置（query_engine）
  - 十一、Bing 主题配置（bing_theme）
  - 十二、监控配置（monitoring）
  - 十三、错误处理配置（error_handling）
  - 十四、日志配置（logging）
- 更新完整配置示例

**配置来源**：
- 参考 `src/infrastructure/app_config.py`
- 参考 `config.example.yaml`

### 5. docs/reference/审查评论处理工作流指南.md

**当前问题**：
- 与 `评论处理系统说明.md` 内容重复

**修改要求**：
- 精简为快速入门指南
- 移除重复的 CLI 命令详情（保留简要说明和链接）
- 移除重复的三种 AI 工具对比表格
- 移除重复的问题分类规则
- 移除重复的严禁事项
- 添加"详细文档"链接指向 `评论处理系统说明.md`

**保留内容**：
- 快速入门定位
- Agent 工作流示例
- 问题类型判断代码
- 常见问题 Q&A

### 6. docs/task_system.md

**当前问题**：
- Phase 1 状态未更新
- 测试脚本路径错误（scripts/ 目录不存在）

**修改要求**：
- Phase 1 状态更新：
  - `[ ] 实战验证` → `[x] 实战验证`
- 测试脚本路径修正：
  - `scripts/automated_test.py` → `tools/diagnose.py`
  - `scripts/diagnose_earn_page.py` → `tools/diagnose_earn_page.py`

**保留内容**：
- 页面结构详解
- 任务分类
- 代码实现要点

### 7. docs/reports/技术参考.md

**当前问题**：
- 最后更新日期过时

**修改要求**：
- 更新最后更新日期为 2026-02-24

**保留内容**：
- 所有技术内容

## 验证标准

### 引用验证

- [ ] 所有文档内部链接可访问
- [ ] 所有文件路径引用存在
- [ ] 所有命令行参数与 cli.py 一致

### 配置验证

- [ ] CONFIG.md 配置项与 app_config.py 一致
- [ ] CONFIG.md 默认值与 config.example.yaml 一致
- [ ] 用户指南配置与 README.md 一致

### 内容验证

- [ ] 项目名称统一为 RewardsCore
- [ ] 搜索次数统一为桌面 20 次
- [ ] 无重复内容

## 执行顺序

1. 阶段 1：修复断裂引用（docs/README.md, README.md）
2. 阶段 2：同步配置文档（用户指南.md, CONFIG.md）
3. 阶段 3：精简重复内容（审查评论处理工作流指南.md）
4. 阶段 4：更新过时内容（task_system.md, 技术参考.md）
5. 阶段 5：验证
