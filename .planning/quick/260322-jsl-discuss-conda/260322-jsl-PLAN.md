# Quick Task Plan: 配置 pre-commit，集成 ruff、ruff-format 和 mypy

**Quick ID:** 260322-jsl
**Description:** 配置 pre-commit hooks，将 ruff、ruff-format 和 mypy 集成到项目中，确保代码质量检查在提交前自动运行
**Mode:** quick (standard)
**Context:** CONTEXT.md 存在，决策已锁定

---

## Objective

为 RewardsCore 项目配置完整的 pre-commit 质量门禁，集成风格检查（ruff）、格式自动修复（ruff-format）和类型检查（mypy），并添加基础清理钩子，确保所有提交的代码符合项目质量标准。

---

## Tasks

### Task 1: 安装 pre-commit 到开发依赖

**Objective:** 确保 pre-commit 工具作为项目 dev 依赖可用，所有开发者可通过 `pip install -e ".[dev]"` 安装。

**Actions:**
1. 检查 `pyproject.toml` 的 `[project.optional-dependencies]` 中是否已有 `pre-commit`（预期：无）
2. 将 `pre-commit>=3.0.0` 添加到 `dev` 依赖列表（与现有 ruff、mypy、pytest 等并列）
3. 保存文件

**Deliverables:**
- `pyproject.toml` 更新（dev dependencies 包含 pre-commit）

**Success Criteria:**
- `pip show pre-commit` 在 conda 环境成功后显示版本
- `pre-commit --version` 命令可执行

---

### Task 2: 更新 .pre-commit-config.yaml 添加 mypy 和基础钩子

**Objective:** 扩展 pre-commit 配置，集成类型检查和代码清理钩子，形成完整的静态检查链。

**Actions:**
1. 保留现有 ruff 和 ruff-format 钩子（不动）
2. 添加 mypy 钩子（使用 `pre-commit/mirrors-mypy`，rev v1.14.1）：
   ```yaml
   - repo: https://github.com/pre-commit/mirrors-mypy
     rev: v1.14.1
     hooks:
       - id: mypy
         additional_dependencies:
           - pydantic>=2.9.0
   ```
3. 添加 pre-commit-hooks 集合（rev v4.6.0）：
   ```yaml
   - repo: https://github.com/pre-commit/pre-commit-hooks
     rev: v4.6.0
     hooks:
       - id: trailing-whitespace
       - id: end-of-file-fixer
       - id: check-yaml
       - id: check-added-large-files
   ```
4. 确保文件格式正确（YAML 语法）

**Deliverables:**
- `.pre-commit-config.yaml` 更新完成

**Success Criteria:**
- `pre-commit run --all-files` 成功执行（所有钩子通过）
- 无语法错误

---

### Task 3: 安装 git hooks 并验证功能

**Objective:** 在本地仓库安装 git pre-commit hooks，使配置生效，并验证自动检查机制。

**Actions:**
1. 在项目根目录运行 `pre-commit install`（安装到 `.git/hooks/pre-commit`）
2. 运行 `pre-commit run --all-files` 验证所有钩子工作正常
3. 测试：修改一个 Python 文件（故意引入类型错误或格式问题），运行 `git add` 和 `git commit`，确认 hooks 触发
4. 记录安装结果

**Deliverables:**
- `.git/hooks/pre-commit` 文件存在且可执行
- 验证输出（成功或需要修复的提示）

**Success Criteria:**
- `pre-commit run --all-files` 返回 exit code 0
- git commit 时自动触发 pre-commit 检查
- 任何 style/type 错误在提交前被拦截（或自动修复）

---

## Dependencies

- Task 1 必须先完成（pre-commit 工具可用）
- Task 2 依赖 Task 1 的配置文件位置（但不依赖安装）
- Task 3 依赖 Task 1 和 Task 2 都完成

---

## Notes

- **执行命令**：所有 bash 命令使用 conda 环境执行：`${CONDA_PREFIX}/bin/pre-commit` 或 `conda run -n rewards-core pre-commit ...`
- **顺序重要性**：钩子顺序按配置顺序执行（先 ruff 再 mypy），这是 deliberate 的——先修复风格再检查类型
- **缓存**：pre-commit 会自动缓存，后续运行会快很多
- **跳过检查**：必要时开发者可使用 `git commit --no-verify` 跳过，但需有充分理由

---

*Plan Created: 2026-03-22 by gsd-planner (quick mode)*
