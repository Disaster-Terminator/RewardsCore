# 项目规则

## 仓库信息

| 属性 | 值 |
|------|-----|
| owner | `Disaster-Terminator` |
| repo | `RewardsCore` |
| default_branch | `main` |

## 环境安全

- 零污染：禁止在 global/base 环境执行 pip install 或 conda install
- 依赖缺失：停止并报告给用户，禁止自行安装

## 文件操作

- 移动/重命名：使用 Move-Item 命令
- 批量删除：使用 Remove-Item 命令

## 熔断机制

| 条件 | 动作 |
|------|------|
| 连续 3 次验证失败 | 停止执行，向用户报告 |
| 缺少必要上下文 | 停止执行，向用户请求信息 |
| 依赖缺失 | 停止执行，向用户报告 |

## 禁止事项

- 禁止自行安装依赖
- 禁止猜测 DOM 选择器（需从 Memory 或实际页面获取）
- 禁止保存完整 HTML（仅精简取证）
- 禁止在 E2E 测试后不关闭 Playwright 页面
