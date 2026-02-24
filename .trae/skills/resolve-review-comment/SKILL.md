---
name: resolve-review-comment
description: 解决PR审查评论。通过 CLI 工具执行解决操作，支持多种解决类型。
---

# 解决审查评论

## 执行命令

```bash
python tools/manage_reviews.py resolve --thread-id {thread_id} --type {resolution_type} [--reply "{reply_content}"]
```

## 参数说明

| 参数 | 必需 | 说明 |
|------|------|------|
| `--thread-id` | 是 | Thread ID（从 fetch-reviews 获取） |
| `--type` | 是 | 解决类型 |
| `--reply` | 条件 | rejected/false_positive 时必需 |

## 解决类型

| 类型 | 含义 | 需要回复 |
|------|------|----------|
| `code_fixed` | 代码已修复 | 否 |
| `adopted` | 已采纳建议 | 否 |
| `rejected` | 拒绝建议 | **是** |
| `false_positive` | 误报 | **是** |
| `outdated` | 已过时 | 否 |

## 使用示例

### 代码已修复

```bash
python tools/manage_reviews.py resolve --thread-id "MDI0OlB1bGxSZXF1ZXN0UmV2aWV3VGhyZWFkMTIz" --type code_fixed
```

### 拒绝建议（需回复）

```bash
python tools/manage_reviews.py resolve --thread-id "MDI0OlB1bGxSZXF1ZXN0UmV2aWV3VGhyZWFkNDU2" --type rejected --reply "此建议不适用于当前场景，因为该代码路径在异步上下文中运行。"
```

### 误报（需回复）

```bash
python tools/manage_reviews.py resolve --thread-id "MDI0OlB1bGxSZXF1ZXN0UmV2aWV3VGhyZWFkNzg5" --type false_positive --reply "此警告为误报，变量在使用前已通过类型守卫确保非空。"
```

## JSON 输出

```json
{
    "success": true,
    "message": "线程 {thread_id} 已解决",
    "resolution_type": "code_fixed",
    "reply_posted": false
}
```

## 严禁事项

| 禁止行为 | 原因 |
|----------|------|
| 无依据标记解决 | 必须先修复代码或有合理理由 |
| 跳过说明评论 | rejected/false_positive 必须回复说明原因 |
| 猜测 Thread ID | 必须使用 fetch-reviews 获取的 Thread ID |

## 降级策略

如果 CLI 工具失败，参考 `docs/reference/archive/v1-ai-reviewer-guide.md`。
