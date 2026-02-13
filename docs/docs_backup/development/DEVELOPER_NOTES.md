# 开发技术要点

## 概述

本文档记录项目开发过程中的关键技术决策和非显而易见的实现细节。

## 目录

- [异步生命周期异常处理](#异步生命周期异常处理)
- [动态 DOM 解析策略](#动态-dom-解析策略)
- [会话状态管理](#会话状态管理)
- [跨平台脚本兼容性](#跨平台脚本兼容性)
- [调度器时间处理](#调度器时间处理)
- [资源回收与日志审计](#资源回收与日志审计)

---

## 异步生命周期异常处理

### 页面加载策略选择

对于包含大量异步资源的 SPA 页面，`networkidle` 等待策略可能导致超时。

```python
# 针对 Microsoft Rewards 页面的优化策略
await page.goto(
    url, 
    wait_until="domcontentloaded",  # 而非 networkidle
    timeout=30000
)
```

**原理**：Microsoft Rewards 页面包含持续的网络请求（如广告、分析脚本），`networkidle` 难以满足。`domcontentloaded` 确保 DOM 结构完整，足以进行后续操作。

### 异步页面状态处理

针对异步环境下页面可能意外关闭的情况，在核心操作中引入了异常捕获机制，确保任务流不因单页崩溃而中断。

## 动态 DOM 解析策略

### 多选择器降级策略

页面结构变化时，单一选择器容易失效。实现多选择器降级策略：

```python
POINTS_SELECTORS = [
    "span.mee-rewards-user-status-balance",  # 主要选择器
    "span[class*='balance']",                # 通配符匹配
    "div[class*='points'] span",             # 层级匹配
    ".rewards-balance",                      # 通用类名
]

async def get_points_with_fallback(page):
    for selector in POINTS_SELECTORS:
        try:
            element = page.locator(selector).first
            if await element.is_visible(timeout=2000):
                return await element.text_content()
        except TimeoutError:
            continue
    return None
```

### 积分数值解析

利用正则提取逻辑兼容不同地区（如带逗号分隔符）的积分显示格式。

## 会话状态管理

### 状态文件完整性验证

`storage_state.json` 文件可能因程序异常终止而损坏，需要验证文件完整性：

```python
def validate_storage_state(file_path):
    """验证会话状态文件的完整性"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        # 验证必要的数据结构
        required_keys = ['cookies', 'origins']
        if not all(key in state for key in required_keys):
            return False
            
        # 验证 cookies 结构
        if not isinstance(state['cookies'], list):
            return False
            
        return True
    except (json.JSONDecodeError, FileNotFoundError, KeyError):
        return False
```

## 跨平台脚本兼容性

### Windows 批处理编码处理

Windows 批处理脚本需要注意字符编码问题：

```batch
@echo off
chcp 65001 >nul 2>&1
REM 设置 UTF-8 编码以支持 Unicode 字符
```

### Conda 环境激活

在批处理脚本中激活 Conda 环境需要使用 `call` 命令：

```batch
call conda activate ms-rewards-bot
if errorlevel 1 (
    echo Environment activation failed
    exit /b 1
)
```

**技术原因**：`conda activate` 修改当前 shell 环境，不使用 `call` 会导致环境变量无法正确传递。

## 调度器时间处理

### 时区感知的时间计算

调度器需要处理本地时区和夏令时变化（需要 Python 3.9+）：

```python
from datetime import datetime, timezone
import zoneinfo

def get_next_execution_time(start_hour, end_hour):
    """计算下次执行时间，考虑本地时区"""
    try:
        # 使用系统时区（Python 3.9+）
        local_tz = zoneinfo.ZoneInfo("Asia/Shanghai")
    except:
        # 降级到 UTC 偏移
        local_tz = timezone(timedelta(hours=8))
    
    now = datetime.now(local_tz)
    # 时间计算逻辑...
```

### 加权随机时间分布

避免简单随机导致的时间分布不均，实现反检测优化：

```python
def generate_weighted_random_time(start_hour, end_hour, peak_hours=None):
    """生成加权随机时间，避免在高峰时段集中"""
    if peak_hours is None:
        peak_hours = [12, 18, 21]  # 避开常见的高峰时段
    
    total_minutes = (end_hour - start_hour) * 60
    weights = []
    
    for minute in range(total_minutes):
        hour = start_hour + minute // 60
        # 降低高峰时段的权重
        weight = 0.5 if hour in peak_hours else 1.0
        weights.append(weight)
    
    # 使用加权随机选择
    selected_minute = random.choices(range(total_minutes), weights=weights)[0]
    hour = start_hour + selected_minute // 60
    minute = selected_minute % 60
    
    return hour, minute
```

## 资源回收与日志审计

### 异步资源管理

通过异步上下文管理器确保浏览器资源在任何情况下都能正确释放。

### 日志轮转配置

防止日志文件无限增长：

```python
from logging.handlers import RotatingFileHandler

def setup_rotating_logger(name, log_file, max_bytes=10*1024*1024, backup_count=5):
    """设置轮转日志记录器"""
    logger = logging.getLogger(name)
    handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
```

---

## 调试技巧

### 网络请求监控

```python
def setup_request_monitoring(page):
    """设置网络请求监控，用于调试"""
    def log_request(request):
        if 'rewards.microsoft.com' in request.url:
            logger.debug(f"Request: {request.method} {request.url}")
    
    def log_response(response):
        if response.status >= 400:
            logger.warning(f"HTTP {response.status}: {response.url}")
    
    page.on("request", log_request)
    page.on("response", log_response)
```

### 元素定位调试

```python
async def debug_element_location(page, selector, screenshot_name=None):
    """调试元素定位问题"""
    try:
        element = page.locator(selector)
        count = await element.count()
        logger.debug(f"Found {count} elements for selector: {selector}")
        
        if count > 0:
            is_visible = await element.first.is_visible()
            logger.debug(f"First element visible: {is_visible}")
        
        if screenshot_name:
            await page.screenshot(path=f"debug_{screenshot_name}.png")
            
    except Exception as e:
        logger.error(f"Debug failed for selector {selector}: {e}")
```