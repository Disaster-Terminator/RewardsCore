---
name: request-reviews
description: 请求PR的AI审查。发送Sourcery/Qodo审查命令并轮询等待响应。
---

# 请求AI审查流程

## 触发条件

- 用户请求"新审查"或"重新审查"
- PR代码更新后需要重新审查

## 执行流程

### 步骤 1：发送审查命令

**重要**：评论必须只包含命令，不能有多余内容。

```
# 评论1：触发 Sourcery
add_issue_comment(owner, repo, issue_number, body="@sourcery-ai review")

# 评论2：触发 Qodo
add_issue_comment(owner, repo, issue_number, body="/review")
```

### 步骤 2：轮询等待响应

**参数**：
- 间隔：30秒
- 最大次数：10次（5分钟）
- 停止条件：检测到新评论 或 达到最大次数

**逻辑**：
```
1. 记录 baseline_time = 当前时间
2. 循环：
   a. 等待 30 秒
   b. 调用 get_pull_request_comments 获取评论
   c. 筛选 created_at > baseline_time 且 author 是 bot 的评论
   d. 如果有新评论 → 停止轮询，返回成功
   e. 如果达到最大次数 → 告知用户，返回超时
```

## 输出格式

### 成功
```
✅ 审查请求已发送，检测到新评论响应
```

### 超时
```
⏳ 审查请求已发送，但5分钟内未检测到响应
建议：稍后手动刷新查看
```
