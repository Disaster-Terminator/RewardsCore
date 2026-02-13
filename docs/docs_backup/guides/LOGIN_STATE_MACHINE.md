# 登录状态机使用指南

## 概述

登录状态机是 MS Rewards Automator 的新功能，用于自动处理 Microsoft 账户的各种登录场景。它可以自动识别和处理：

- 邮箱输入
- 密码输入
- TOTP 双因素认证（2FA）
- 无密码登录提示
- 邮箱验证码（需要手动干预）
- 短信验证码（需要手动干预）
- 恢复邮箱验证（需要手动干预）

## 快速开始

### 1. 启用登录状态机

在 `config.yaml` 中启用登录状态机：

```yaml
login:
  state_machine_enabled: true    # 启用自动登录
  max_transitions: 10            # 最大状态转换次数
  timeout_seconds: 300           # 登录超时时间（秒）
  stay_signed_in: true           # 保持登录状态
```

### 2. 配置账户凭据

```yaml
account:
  email: "your-email@example.com"     # 你的邮箱
  password: "your-password"           # 你的密码
  totp_secret: ""                     # TOTP密钥（可选）
```

### 3. 使用自动登录

```python
from src.account_manager import AccountManager
from src.config_manager import ConfigManager

# 初始化
config = ConfigManager("config.yaml")
account_manager = AccountManager(config)

# 准备凭据
credentials = {
    "email": config.get("account.email"),
    "password": config.get("account.password"),
    "totp_secret": config.get("account.totp_secret", "")
}

# 自动登录
success = await account_manager.auto_login(page, credentials)

if success:
    print("登录成功！")
else:
    print("登录失败")
```

## 支持的登录场景

### 1. 基础登录（邮箱 + 密码）

最常见的登录方式，状态机会自动：
1. 检测邮箱输入页面
2. 填写邮箱并点击"下一步"
3. 检测密码输入页面
4. 填写密码并点击"登录"
5. 处理"保持登录"提示

**配置要求**:
```yaml
account:
  email: "your-email@example.com"
  password: "your-password"
```

### 2. TOTP 双因素认证

如果账户启用了 TOTP 2FA，状态机会自动：
1. 检测 TOTP 验证页面
2. 使用 TOTP 密钥生成验证码
3. 填写验证码并提交

**配置要求**:
```yaml
account:
  email: "your-email@example.com"
  password: "your-password"
  totp_secret: "JBSWY3DPEHPK3PXP"  # 你的TOTP密钥
```

**如何获取 TOTP 密钥**:
1. 在 Microsoft 账户安全设置中启用 2FA
2. 选择"使用身份验证器应用"
3. 在扫描二维码之前，点击"无法扫描？"
4. 复制显示的密钥（Base32 格式）
5. 将密钥配置到 `totp_secret`

### 3. 无密码登录提示

如果 Microsoft 提示使用无密码登录，状态机会自动：
1. 检测无密码登录提示
2. 点击"使用密码登录"
3. 继续密码登录流程

**无需额外配置**，状态机会自动处理。

### 4. 邮箱/短信验证码（手动干预）

如果 Microsoft 要求邮箱或短信验证码，状态机会：
1. 检测验证码请求页面
2. 记录日志提示需要手动干预
3. 等待配置的超时时间
4. 继续执行或报错

**配置**:
```yaml
login:
  manual_intervention_timeout: 120  # 等待手动干预的时间（秒）
```

**使用方式**:
- 状态机会暂停并等待
- 你需要在超时前手动输入验证码
- 输入后状态机会自动继续

## 配置选项详解

### login 配置节

```yaml
login:
  # 是否启用登录状态机
  state_machine_enabled: true
  
  # 最大状态转换次数（防止无限循环）
  # 通常 3-5 次转换即可完成登录
  max_transitions: 10
  
  # 登录超时时间（秒）
  # 包括所有状态转换和页面加载
  timeout_seconds: 300
  
  # 是否在"保持登录"提示中选择"是"
  stay_signed_in: true
  
  # 需要手动干预时的等待时间（秒）
  manual_intervention_timeout: 120
```

### account 配置节

```yaml
account:
  # Microsoft 账户邮箱
  email: "your-email@example.com"
  
  # 账户密码
  password: "your-password"
  
  # TOTP 密钥（可选，用于 2FA）
  totp_secret: ""
  
  # 会话状态保存路径
  storage_state_path: "storage_state.json"
  
  # 登录页面 URL
  login_url: "https://rewards.microsoft.com/"
```

## 向后兼容性

登录状态机是**可选功能**，不会影响现有的手动登录方式。

### 禁用登录状态机

如果你想继续使用传统的手动登录方式：

```yaml
login:
  state_machine_enabled: false  # 禁用自动登录
```

禁用后，系统会回退到原来的 `wait_for_manual_login()` 方法。

### 混合使用

你可以根据需要选择使用方式：

```python
# 方式1：使用自动登录
if account_manager.use_state_machine:
    success = await account_manager.auto_login(page, credentials)
else:
    success = await account_manager.wait_for_manual_login(page)

# 方式2：总是使用手动登录
success = await account_manager.wait_for_manual_login(page)
```

## 故障排查

### 问题1：登录超时

**症状**: 登录过程中报错 `TimeoutError: Login exceeded timeout`

**原因**: 
- 网络速度慢
- 页面加载时间长
- 状态转换过多

**解决方案**:
```yaml
login:
  timeout_seconds: 600  # 增加超时时间到 10 分钟
```

### 问题2：超过最大转换次数

**症状**: 报错 `RuntimeError: Login exceeded maximum transitions`

**原因**:
- 登录流程异常复杂
- 状态检测不准确
- 陷入循环

**解决方案**:
```yaml
login:
  max_transitions: 20  # 增加最大转换次数
```

同时检查日志，查看状态转换历史：
```python
diag = account_manager.state_machine.get_diagnostic_info()
print(diag['state_history'])
```

### 问题3：TOTP 验证失败

**症状**: TOTP 验证码被拒绝

**原因**:
- TOTP 密钥错误
- 系统时间不同步

**解决方案**:
1. 确认 TOTP 密钥正确
2. 同步系统时间：
   ```bash
   # Windows
   w32tm /resync
   
   # Linux
   sudo ntpdate -s time.nist.gov
   ```

### 问题4：状态检测失败

**症状**: 状态机无法识别当前页面

**原因**:
- Microsoft 更新了页面结构
- 选择器失效

**解决方案**:
1. 查看诊断信息：
   ```python
   diag = account_manager.state_machine.get_diagnostic_info()
   print(f"当前状态: {diag['current_state']}")
   print(f"状态历史: {diag['state_history']}")
   ```

2. 临时禁用状态机，使用手动登录：
   ```yaml
   login:
     state_machine_enabled: false
   ```

3. 报告问题，等待更新

## 安全建议

### 1. 保护配置文件

⚠️ **配置文件包含敏感信息，请妥善保管！**

```bash
# 设置文件权限（Linux/Mac）
chmod 600 config.yaml

# 添加到 .gitignore
echo "config.yaml" >> .gitignore
```

### 2. 使用环境变量

推荐使用环境变量存储敏感信息：

```yaml
account:
  email: "${MS_REWARDS_EMAIL}"
  password: "${MS_REWARDS_PASSWORD}"
  totp_secret: "${MS_REWARDS_TOTP}"
```

```bash
# 设置环境变量
export MS_REWARDS_EMAIL="your-email@example.com"
export MS_REWARDS_PASSWORD="your-password"
export MS_REWARDS_TOTP="your-totp-secret"
```

### 3. 定期更换密码

建议定期更换密码，并更新配置文件。

## 高级用法

### 自定义状态处理器

如果需要处理新的登录场景，可以创建自定义状态处理器：

```python
from src.core.login.state_handler import StateHandler
from src.core.login.login_state_machine import LoginState

class CustomHandler(StateHandler):
    async def can_handle(self, page):
        # 检测逻辑
        return await self.element_exists(page, "custom-selector")
    
    async def handle(self, page, credentials):
        # 处理逻辑
        await self.safe_click(page, "custom-button")
        return True
    
    def get_next_states(self):
        return [LoginState.LOGGED_IN, LoginState.ERROR]

# 注册处理器
account_manager.state_machine.register_handler(
    LoginState.CUSTOM,
    CustomHandler(config, logger)
)
```

### 获取诊断信息

```python
# 获取详细的诊断信息
diag = account_manager.state_machine.get_diagnostic_info()

print(f"当前状态: {diag['current_state']}")
print(f"转换次数: {diag['transition_count']}")
print(f"已注册处理器: {diag['registered_handlers']}")

# 查看状态历史
for transition in diag['state_history']:
    print(f"{transition['from']} → {transition['to']} "
          f"at {transition['timestamp']}")
```

## 更多资源

- [配置示例](../../config-examples.yaml)
- [故障排查指南](TROUBLESHOOTING.md)
- [开发者文档](../development/DEVELOPER_NOTES.md)
