# 通知功能配置指南

## 📋 目录

- [概述](#概述)
- [Telegram Bot 配置](#telegram-bot-配置)
- [Server酱配置（微信推送）](#server酱配置微信推送)
- [WhatsApp 配置](#whatsapp-配置)
- [同时使用多种方式](#同时使用多种方式)
- [故障排除](#故障排除)
- [禁用通知](#禁用通知)

---

## 概述

MS Rewards Automator 支持三种通知方式：
1. **Telegram Bot** - 通过 Telegram 机器人推送消息
2. **Server酱** - 通过微信推送消息  
3. **WhatsApp** - 通过 WhatsApp 推送消息

## 完整配置示例

```yaml
notification:
  enabled: true
  
  telegram:
    enabled: true
    bot_token: "你的Bot Token"
    chat_id: "你的Chat ID"
  
  serverchan:
    enabled: true
    key: "你的SendKey"
    
  whatsapp:
    enabled: true
    phone: "+8613800138000"
    apikey: "你的API Key"
```

## Telegram Bot 配置

### 1. 创建 Bot

1. 在 Telegram 中搜索 `@BotFather`
2. 发送 `/newbot` 命令
3. 按提示设置机器人名称
4. 获得 Bot Token

### 2. 获取 Chat ID

1. 在 Telegram 中搜索 `@userinfobot`
2. 发送任意消息
3. 获得你的 Chat ID（纯数字）

### 3. 配置

编辑 `config.yaml`：

```yaml
telegram:
  enabled: true
  bot_token: "你的Bot Token"
  chat_id: "你的Chat ID"
```

## Server酱配置（微信推送）

### 1. 注册

1. 访问 https://sct.ftqq.com/
2. 微信扫码登录
3. 获取 SendKey

### 2. 配置

```yaml
serverchan:
  enabled: true
  key: "你的SendKey"
```

## WhatsApp 配置

### 1. 获取 API Key

**注意**：由于运营商限制，CallMeBot 对中国大陆 (+86) 手机号的支持并不稳定。如果无法收到消息，建议优先使用 Telegram 或 Server酱。

1. **添加 CallMeBot 到 WhatsApp**
   - 将此号码添加到你的 WhatsApp 联系人：**+34 644 44 71 67**
   - 联系人名称可以设为：CallMeBot

2. **发送激活消息**
   - 打开与 CallMeBot 的聊天
   - 发送消息：`I allow callmebot to send me messages`
   - 等待回复（通常几秒钟）

3. **获取 API Key**
   - CallMeBot 会回复一条消息，包含你的 API Key
   - API Key 格式类似：`123456`
   - **保存这个 API Key**

### 2. 配置

```yaml
whatsapp:
  enabled: true
  phone: "+8613800138000"  # 你的手机号（国际格式）
  apikey: "123456"         # 你的 API Key
```

**注意事项**：
- 手机号必须是国际格式：`+国家代码+手机号`
- 不要有空格或其他符号

### 3. 常见问题

**没有收到激活消息？**
1. 确认已正确添加联系人：+34 644 44 71 67
2. 确认发送的消息完全正确（复制粘贴）
3. 等待几分钟，有时会延迟

**测试通知失败？**
1. 手机号格式是否正确（国际格式）
2. API Key 是否正确（纯数字）
3. 是否已完成激活步骤

## 同时使用多种方式

可以同时启用多种通知方式：

```yaml
notification:
  enabled: true
  telegram:
    enabled: true
    bot_token: "你的Bot Token"
    chat_id: "你的Chat ID"
  serverchan:
    enabled: true
    key: "你的SendKey"
  whatsapp:
    enabled: true
    phone: "+8613800138000"
    apikey: "你的API Key"
```

## 故障排除

### Telegram 发送失败

- 检查 Bot Token 和 Chat ID 是否正确
- 确认网络可以访问 api.telegram.org

### Server酱 发送失败

- 检查 SendKey 是否正确
- 确认微信已绑定
- 检查是否超过每日发送限制

### WhatsApp 发送失败

- 检查手机号格式（国际格式：+8613800138000）
- 确认已完成激活步骤
- 检查 API Key 是否正确

## 禁用通知

如果不需要通知功能：

```yaml
notification:
  enabled: false
```

---

每次任务完成后，会收到包含搜索次数、积分情况和执行状态的通知消息。
