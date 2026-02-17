# 配置文件参考

## 一、搜索配置

```yaml
search:
  desktop_count: 30              # 桌面端搜索次数
  mobile_count: 20               # 移动端搜索次数
  wait_interval:
    min: 5                       # 最小等待时间（秒）
    max: 15                      # 最大等待时间（秒）
  search_terms_file: "tools/search_terms.txt"
```

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `desktop_count` | 30 | 桌面搜索次数 |
| `mobile_count` | 20 | 移动搜索次数 |
| `wait_interval.min` | 5 | 最小等待时间 |
| `wait_interval.max` | 15 | 最大等待时间 |

---

## 二、浏览器配置

```yaml
browser:
  headless: false                # 是否无头模式
  type: "chromium"               # 浏览器类型
  force_dark_mode: false         # 强制深色模式
```

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `headless` | false | 无头模式（后台运行） |
| `type` | chromium | 浏览器类型：chromium/edge/chrome |

---

## 三、登录配置

```yaml
login:
  auto_login:
    enabled: false               # 是否启用自动登录
    email: ""                    # Microsoft 账号
    password: ""                 # 密码
    totp_secret: ""              # 2FA 密钥
```

**推荐**：使用手动登录（首次运行时浏览器打开，手动登录后保存会话）。

---

## 四、调度器配置

```yaml
scheduler:
  enabled: true                  # 默认启用
  timezone: "Asia/Shanghai"
  mode: "scheduled"
  scheduled_hour: 17             # 基准执行时间
  max_offset_minutes: 45         # 随机偏移范围
```

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `enabled` | true | 是否启用调度器 |
| `timezone` | Asia/Shanghai | 时区 |
| `mode` | scheduled | 调度模式 |
| `scheduled_hour` | 17 | 基准执行时间 |
| `max_offset_minutes` | 45 | 随机偏移范围 |

**禁用调度器**：设置 `enabled: false`，程序执行一次后退出。

详细说明参见 [调度器文档](SCHEDULER.md)。

---

## 五、通知配置

```yaml
notification:
  enabled: false
  telegram:
    bot_token: ""
    chat_id: ""
  serverchan:
    key: ""
```

| 配置项 | 说明 |
|--------|------|
| `telegram.bot_token` | Telegram Bot Token |
| `telegram.chat_id` | Telegram Chat ID |
| `serverchan.key` | Server酱 SendKey |

---

## 六、任务系统配置

```yaml
task_system:
  enabled: false                 # 是否启用每日任务
  debug_mode: false
```

---

## 七、监控配置

```yaml
monitoring:
  health_check:
    enabled: false
    interval: 30
```

---

## 八、完整配置示例

```yaml
search:
  desktop_count: 30
  mobile_count: 20
  wait_interval:
    min: 5
    max: 15

browser:
  headless: false
  type: "chromium"

account:
  storage_state_path: "storage_state.json"

login:
  auto_login:
    enabled: false

scheduler:
  enabled: true
  timezone: "Asia/Shanghai"
  mode: "scheduled"
  scheduled_hour: 17
  max_offset_minutes: 45

notification:
  enabled: false
  telegram:
    bot_token: ""
    chat_id: ""

task_system:
  enabled: false

monitoring:
  health_check:
    enabled: false
```
