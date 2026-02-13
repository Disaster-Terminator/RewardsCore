# Query Engine 使用指南

## 概述

Query Engine（查询引擎）是 MS Rewards Automator 的智能查询生成系统，可以从多个数据源生成多样化、真实的搜索查询，提高搜索的自然度并降低被检测的风险。

## 功能特性

### 核心功能

1. **多数据源支持**
   - 本地文件源（Local File Source）
   - Bing 建议 API（Bing Suggestions API）
   - 可扩展架构，支持添加更多数据源

2. **智能查询生成**
   - 查询去重（避免重复搜索）
   - 查询随机化（增加不可预测性）
   - 查询扩展（使用 Bing API 扩展基础查询）
   - 查询缓存（减少 API 调用）

3. **容错机制**
   - 自动降级到本地文件源
   - API 失败重试（指数退避）
   - 速率限制保护

## 配置说明

### 启用 Query Engine

在 `config.yaml` 中配置：

```yaml
# 查询引擎配置
query_engine:
  enabled: true              # 启用查询引擎（false = 使用传统生成器）
  cache_ttl: 3600            # 查询缓存时间（秒，默认1小时）
  
  # 查询源配置
  sources:
    local_file:
      enabled: true          # 本地文件源（始终启用作为后备）
    
    bing_suggestions:
      enabled: true          # Bing建议API（无需认证）
  
  # Bing API 配置
  bing_api:
    rate_limit: 10           # 每分钟最大请求数
    max_retries: 3           # 最大重试次数
    timeout: 15              # 请求超时（秒）
    suggestions_per_query: 3 # 每个查询获取的建议数
    suggestions_per_seed: 3  # 每个种子查询获取的建议数
    max_expand: 5            # 最多扩展的查询数
```

### 配置参数说明

| 参数 | 说明 | 默认值 | 推荐值 |
|------|------|--------|--------|
| `enabled` | 是否启用查询引擎 | `false` | `true` |
| `cache_ttl` | 缓存有效期（秒） | `3600` | `3600` |
| `rate_limit` | API 速率限制（请求/分钟） | `10` | `10` |
| `max_retries` | API 失败重试次数 | `3` | `3` |
| `timeout` | API 请求超时（秒） | `15` | `15` |
| `suggestions_per_query` | 每个查询的建议数 | `3` | `3-5` |
| `max_expand` | 最多扩展查询数 | `5` | `5-10` |

## 使用方式

### 基本使用

1. **启用 Query Engine**
   ```yaml
   query_engine:
     enabled: true
   ```

2. **运行程序**
   ```bash
   python main.py
   ```

3. **查看日志**
   ```
   [INFO] QueryEngine initialized with 2 sources
   [INFO] ✓ LocalFileSource enabled
   [INFO] ✓ BingSuggestionsSource enabled
   [INFO] Generated 30 queries from 2 sources
   ```

### 仅使用本地文件源

如果不想使用 Bing API，可以禁用：

```yaml
query_engine:
  enabled: true
  sources:
    bing_suggestions:
      enabled: false  # 禁用 Bing API
```

### 传统模式（不使用 Query Engine）

如果想使用原来的搜索词生成器：

```yaml
query_engine:
  enabled: false  # 禁用查询引擎
```

## 工作原理

### 查询生成流程

```
1. 检查缓存
   ├─ 命中 → 返回缓存的查询
   └─ 未命中 → 继续

2. 从数据源获取查询
   ├─ LocalFileSource → 从本地文件读取
   └─ BingSuggestionsSource → 从 Bing API 获取

3. 查询扩展（可选）
   └─ 使用 Bing API 扩展基础查询

4. 去重处理
   └─ 移除重复查询（不区分大小写）

5. 随机化
   └─ 打乱查询顺序

6. 缓存结果
   └─ 保存到缓存（TTL = 1小时）

7. 返回查询列表
```

### 数据源优先级

1. **缓存**：首先检查缓存
2. **并发获取**：同时从所有启用的数据源获取
3. **合并结果**：合并所有数据源的结果
4. **降级处理**：如果某个源失败，使用其他源的结果

## 扩展功能

### 添加新的数据源

Query Engine 使用插件架构，可以轻松添加新的数据源。

#### 1. 创建数据源类

```python
# src/core/search/query_sources/my_source.py

from .query_source import QuerySource
from typing import List

class MyCustomSource(QuerySource):
    """自定义查询源"""
    
    def __init__(self, config):
        super().__init__(config)
        # 初始化代码
    
    async def fetch_queries(self, count: int) -> List[str]:
        """获取查询"""
        # 实现查询获取逻辑
        return ["query1", "query2", ...]
    
    def get_source_name(self) -> str:
        """返回源名称"""
        return "my_custom_source"
    
    def is_available(self) -> bool:
        """检查源是否可用"""
        return True
```

#### 2. 注册数据源

在 `src/core/search/query_engine.py` 的 `_init_sources` 方法中添加：

```python
# 自定义数据源
if self.config.get("query_engine.sources.my_custom_source.enabled", False):
    try:
        from .query_sources import MyCustomSource
        my_source = MyCustomSource(self.config)
        if my_source.is_available():
            self.sources.append(my_source)
            self.logger.info("✓ MyCustomSource enabled")
    except Exception as e:
        self.logger.error(f"Failed to initialize MyCustomSource: {e}")
```

#### 3. 添加配置

在 `config.yaml` 中添加：

```yaml
query_engine:
  sources:
    my_custom_source:
      enabled: true
      # 其他配置参数
```

### 未来可添加的数据源

以下数据源已在设计文档中规划，可在未来版本中添加：

1. **Wikipedia API**
   - 从维基百科获取热门主题
   - 需要：Wikipedia API 集成

2. **Google Trends API**
   - 获取当前热门搜索词
   - 需要：Google API 认证

3. **Reddit API**
   - 从 Reddit 热门话题获取查询
   - 需要：Reddit API 认证

## 故障排除

### 常见问题

#### 1. Query Engine 未启用

**症状**：日志中没有 "QueryEngine initialized" 消息

**解决方案**：
- 检查 `config.yaml` 中 `query_engine.enabled` 是否为 `true`
- 检查是否有初始化错误日志

#### 2. Bing API 调用失败

**症状**：日志显示 "Bing API request failed"

**解决方案**：
- 检查网络连接
- 检查是否被速率限制
- 系统会自动降级到本地文件源

#### 3. 查询重复

**症状**：搜索词重复出现

**解决方案**：
- 清除缓存（重启程序）
- 增加 `search_terms.txt` 中的搜索词数量
- 启用 Bing Suggestions 源

#### 4. 性能问题

**症状**：查询生成速度慢

**解决方案**：
- 减少 `max_expand` 值
- 增加 `cache_ttl` 值
- 禁用 Bing Suggestions 源

## 性能优化

### 缓存策略

- **默认 TTL**：1小时（3600秒）
- **建议**：根据使用频率调整
  - 频繁使用：增加到 2-4 小时
  - 偶尔使用：保持 1 小时

### API 速率限制

- **默认限制**：10 请求/分钟
- **建议**：不要超过 20 请求/分钟
- **原因**：避免被 Bing API 限制

### 查询扩展

- **默认扩展数**：5 个查询
- **建议**：根据搜索次数调整
  - 30 次搜索：5-10 个扩展
  - 50 次搜索：10-15 个扩展

## 最佳实践

1. **首次使用**
   - 先使用本地文件源测试
   - 确认正常后再启用 Bing Suggestions

2. **日常使用**
   - 启用所有数据源以获得最佳多样性
   - 定期更新 `search_terms.txt`

3. **调试模式**
   - 设置日志级别为 DEBUG
   - 查看详细的查询生成过程

4. **生产环境**
   - 使用默认配置
   - 启用缓存以提高性能

## 相关文档

- [配置指南](../README.md#配置说明)
- [故障排除](TROUBLESHOOTING.md)
- [开发文档](../development/DEVELOPER_NOTES.md)
