# P0模块集成指南

本文档说明如何使用已集成的P0核心模块（Login State Machine、Task System、Query Engine）。

## 📋 模块状态

### ✅ 已完成的P0模块

1. **Login State Machine (Phase 1)** - 自动登录状态机
   - 自动检测登录状态
   - 支持多种登录方式（邮箱/密码、TOTP 2FA、无密码登录等）
   - 状态转换历史追踪

2. **Task System (Phase 2)** - 任务系统
   - 自动发现和解析任务
   - 支持多种任务类型（URL奖励、测验、投票）
   - 任务执行报告

3. **Query Engine (Phase 3)** - 智能查询引擎
   - 多数据源支持（本地文件 + Bing建议API）
   - 查询缓存和去重
   - 速率限制和重试机制

## 🚀 快速开始

### 1. 运行集成测试

首先验证所有P0模块是否正确集成：

```bash
python test_p0_integration.py
```

预期输出：
```
✓ 所有测试通过！P0模块已正确集成
```

### 2. 配置模块

编辑 `config.yaml`，启用P0模块：

```yaml
# 查询引擎配置
query_engine:
  enabled: true              # 启用智能查询引擎
  cache_ttl: 3600
  sources:
    local_file:
      enabled: true
    bing_suggestions:
      enabled: true

# 登录状态机配置
login:
  state_machine_enabled: true  # 启用自动登录
  max_transitions: 20
  transition_timeout: 300

# 任务系统配置
task_system:
  enabled: true              # 启用任务系统
  min_delay: 2
  max_delay: 5
  skip_completed: true
```

### 3. 运行主程序

```bash
# 完整运行（桌面搜索 + 移动搜索 + 任务）
python main.py

# 快速测试（仅桌面搜索）
python main.py --mode fast --desktop-only

# 无头模式
python main.py --headless
```

## 📖 详细使用说明

### Query Engine（查询引擎）

**功能**：
- 自动生成多样化的搜索查询
- 从多个数据源获取查询（本地文件 + Bing建议）
- 自动去重和随机化
- 缓存查询以提高性能

**配置选项**：
```yaml
query_engine:
  enabled: true              # 是否启用
  cache_ttl: 3600           # 缓存时间（秒）
  
  sources:
    local_file:
      enabled: true          # 本地文件源
    bing_suggestions:
      enabled: true          # Bing建议API
  
  bing_api:
    rate_limit: 10           # 每分钟最大请求数
    max_retries: 3           # 最大重试次数
    timeout: 15              # 请求超时（秒）
```

**使用示例**：
```python
from src.core.search.query_engine import QueryEngine

query_engine = QueryEngine(config)
queries = await query_engine.get_queries(30)  # 获取30个查询
```

### Login State Machine（登录状态机）

**功能**：
- 自动检测当前登录状态
- 自动处理各种登录流程
- 支持TOTP 2FA
- 状态转换历史追踪

**配置选项**：
```yaml
login:
  state_machine_enabled: true  # 是否启用
  max_transitions: 20          # 最大状态转换次数
  transition_timeout: 300      # 超时时间（秒）
  
  credentials:                 # 自动登录凭据（可选）
    email: ""
    password: ""
    totp_secret: ""            # TOTP密钥（用于2FA）
```

**使用示例**：
```python
from src.account_manager import AccountManager

account_mgr = AccountManager(config)

# 检查登录状态
is_logged_in = await account_mgr.is_logged_in(page)

# 自动登录（如果配置了凭据）
credentials = {
    'email': 'your@email.com',
    'password': 'your_password',
    'totp_secret': 'your_totp_secret'  # 可选
}
success = await account_mgr.auto_login(page, credentials)
```

### Task System（任务系统）

**功能**：
- 自动发现Microsoft Rewards任务
- 解析任务元数据（标题、积分、状态）
- 执行各种任务类型
- 生成执行报告

**配置选项**：
```yaml
task_system:
  enabled: true                # 是否启用
  min_delay: 2                 # 任务间最小延迟（秒）
  max_delay: 5                 # 任务间最大延迟（秒）
  skip_completed: true         # 跳过已完成的任务
  
  task_types:
    url_reward: true           # URL奖励任务
    quiz: true                 # 测验任务
    poll: true                 # 投票任务
```

**使用示例**：
```python
from src.core.tasks import TaskManager

task_manager = TaskManager(config)

# 发现任务
tasks = await task_manager.discover_tasks(page)

# 执行任务
report = await task_manager.execute_tasks(page, tasks)

print(f"完成: {report.completed}")
print(f"失败: {report.failed}")
print(f"获得积分: {report.points_earned}")
```

## 🔧 故障排除

### Query Engine无法获取查询

**问题**：Query Engine返回空列表或错误

**解决方案**：
1. 检查 `tools/search_terms.txt` 文件是否存在
2. 检查网络连接（Bing API需要网络）
3. 查看日志文件 `logs/automator.log`

### Login State Machine无法自动登录

**问题**：自动登录失败

**解决方案**：
1. 确保配置了正确的凭据
2. 检查TOTP密钥是否正确（如果使用2FA）
3. 首次运行使用手动登录：删除 `storage_state.json`
4. 查看状态转换历史：检查日志中的状态转换记录

### Task System找不到任务

**问题**：TaskManager返回0个任务

**解决方案**：
1. 确保已登录Microsoft Rewards账户
2. 检查任务面板是否可访问
3. 某些任务可能已完成或不可用
4. 查看日志了解详细错误信息

## 📊 性能优化建议

### 1. 查询引擎优化
- 增加缓存时间以减少API调用：`cache_ttl: 7200`
- 禁用不需要的数据源
- 调整速率限制以匹配你的网络

### 2. 任务系统优化
- 增加任务间延迟以降低检测风险：`max_delay: 10`
- 启用 `skip_completed` 以跳过已完成任务
- 在非高峰时段运行

### 3. 登录优化
- 保存会话状态以避免重复登录
- 使用TOTP 2FA提高安全性
- 定期更新 `storage_state.json`

## 📝 日志和调试

### 查看日志

```bash
# 实时查看日志
tail -f logs/automator.log

# 搜索特定模块的日志
grep "QueryEngine" logs/automator.log
grep "TaskManager" logs/automator.log
grep "LoginStateMachine" logs/automator.log
```

### 启用调试模式

```bash
# 使用dry-run模式测试
python main.py --dry-run

# 查看详细日志
# 编辑 config.yaml:
logging:
  level: "DEBUG"
```

## 🎯 下一步

P0模块已完成并集成，你可以：

1. **测试P0功能**：运行主程序验证所有功能
2. **开始Phase 4**：错误处理和数据持久化
3. **开始Phase 5**：多账户支持
4. **开始Phase 6**：反检测增强

## 📚 相关文档

- [Query Engine详细指南](./guides/QUERY_ENGINE_GUIDE.md)
- [任务列表](./.kiro/specs/ms-rewards-core-improvements/tasks.md)
- [设计文档](./.kiro/specs/ms-rewards-core-improvements/design.md)

## ❓ 常见问题

**Q: 我需要同时启用所有P0模块吗？**
A: 不需要。你可以单独启用任何模块。但建议至少启用Query Engine以提高搜索质量。

**Q: 自动登录安全吗？**
A: 凭据存储在本地配置文件中。建议使用环境变量或密钥管理工具。不要将包含凭据的配置文件提交到版本控制。

**Q: Task System支持哪些任务类型？**
A: 目前支持：URL奖励任务、基础测验、投票任务。更多任务类型将在后续版本中添加。

**Q: 如何禁用某个模块？**
A: 在 `config.yaml` 中设置对应的 `enabled: false` 即可。
