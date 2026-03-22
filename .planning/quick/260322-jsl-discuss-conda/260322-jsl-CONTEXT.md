# Quick Task 260322-jsl: 配置 pre-commit，集成 ruff、ruff-format 和 mypy - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

---

<domain>
## Task Boundary

配置 pre-commit hooks，将 ruff、ruff-format 和 mypy 集成到项目中，确保代码质量检查在提交前自动运行。

</domain>

<decisions>
## Implementation Decisions

### pre-commit 工具安装位置
- 作为 dev 依赖安装到 conda 环境（通过 `pip install -e ".[dev]"` 安装）

### mypy 集成
- ✅ 集成到 pre-commit，与 ruff 并行检查

### 检查范围
- 检查所有 staged Python 文件（包括 tests/ 目录），不跳过任何子目录

### 基础钩子
- 添加 `pre-commit-hooks` 集合：
  - `trailing-whitespace`
  - `end-of-file-fixer`
  - `check-yaml`
  - `check-added-large-files`

### 钩子顺序
- 顺序执行：先 ruff（含 --fix 自动修复），后 mypy（类型检查）

### 工具重叠问题
- ruff 负责代码风格和语法问题（lint + format）
- mypy 负责类型注解正确性检查
- 两者互补，无功能重叠，需要同时使用

</decisions>

<specifics>
## Specific Ideas

- `.pre-commit-config.yaml` 已存在，当前只有 ruff 钩子（无 pre-commit 工具本身）
- 需要：1) 安装 pre-commit 到 dev 依赖；2) 更新配置文件添加 mypy 和基础钩子；3) 运行 `pre-commit install` 安装 git hooks
- 参考版本：mypy 使用 `pre-commit/mirrors-mypy` v1.14.1，pre-commit-hooks v4.6.0
- 无需修改 `pyproject.toml`（mypy 配置已存在）
- 安装后验证：`pre-commit run --all-files`

</specifics>

<canonical_refs>
## Canonical References

- `.pre-commit-config.yaml` — 目标配置文件（需修改）
- `pyproject.toml` — 包含 mypy 配置（将被读取）
- `.planning/RULES.md` — E2E 测试项目执行规则（无关，此为配置任务）

</canonical_refs>
