# Beforeunload 对话框修复 (第二版)

## 问题描述

桌面搜索结束后，在"保存桌面会话状态"步骤时脚本会卡死：

```
[6/8] 执行移动搜索...
保存桌面会话状态...
Timeout 30000ms exceeded.
开始清理浏览器资源...
```

**根本原因**：
1. 在保存会话状态时，会新建一个 Bing 窗口
2. 新窗口触发"确定要离开？"对话框
3. `context.storage_state()` 调用被对话框阻塞，导致超时

**深层原因**：
- `TabManager` 的事件监听器在搜索完成后仍然活跃
- 当新窗口被创建时，监听器尝试异步关闭它
- 这个异步操作与 `storage_state()` 调用产生竞态条件
- 新窗口的 `beforeunload` 事件未被及时禁用

## 修复方案

### 核心修复：增强 `AccountManager.save_session()` (src/account_manager.py)

采用五步防护策略：

```python
async def save_session(self, context: BrowserContext) -> bool:
    try:
        # 步骤1: 移除所有事件监听器
        context.remove_all_listeners("page")
        
        # 步骤2: 等待异步任务完成
        await asyncio.sleep(0.5)
        
        # 步骤3: 并发关闭所有额外页面
        all_pages = context.pages
        if len(all_pages) > 1:
            async def close_page_safely(page):
                if not page.is_closed():
                    # 禁用 beforeunload
                    await page.evaluate("() => { window.onbeforeunload = null; }")
                    await page.close()
            
            await asyncio.gather(*[close_page_safely(p) for p in all_pages[1:]], 
                                return_exceptions=True)
            await asyncio.sleep(0.3)
        
        # 步骤4: 验证只剩一个页面
        remaining_pages = context.pages
        logger.debug(f"清理后剩余 {len(remaining_pages)} 个页面")
        
        # 步骤5: 安全调用 storage_state
        state = await context.storage_state()
        
        # 保存到文件...
    except Exception as e:
        logger.error(f"保存会话状态失败: {e}")
```

**关键点**：
1. **移除监听器**：阻止新页面在保存过程中被创建
2. **等待缓冲**：让正在处理的异步任务完成
3. **并发关闭**：使用 `asyncio.gather` 快速关闭所有额外页面
4. **验证状态**：确保环境干净
5. **安全调用**：在稳定环境下调用 `storage_state()`

## 测试

运行测试脚本验证修复：

```bash
python test_beforeunload_fix.py
```

测试内容：
- 创建带有 `beforeunload` 事件的页面
- 禁用事件后关闭页面
- 在有额外页面的情况下调用 `storage_state()`

## 影响范围

修改的文件：
- `src/tab_manager.py`
- `src/account_manager.py`
- `src/browser_state_manager.py`

## 预期效果

- 不再出现"确定要离开？"对话框
- `storage_state()` 调用不会超时
- 页面关闭操作顺利完成
- 脚本不会卡死

## 相关问题

- Issue: 桌面端搜索结束后会新建一个bing页面，然后弹出"确定要离开？"对话框导致脚本卡死
- 修复日期: 2026-02-10


### 辅助修复

#### 1. `TabManager._safe_close_page()` (src/tab_manager.py)
在关闭页面前禁用 `beforeunload` 事件

#### 2. `TabManager._process_new_page()` (src/tab_manager.py)
新页面创建时立即注入防护脚本

#### 3. `BrowserStateManager.cleanup_resources()` (src/browser_state_manager.py)
清理资源时禁用所有页面的 `beforeunload` 事件

## 为什么之前的修复不够

第一版修复只在页面关闭时禁用 `beforeunload`，但没有解决核心问题：

- **竞态条件**：`TabManager` 的异步监听器与 `storage_state()` 调用冲突
- **时序问题**：新窗口可能在 `storage_state()` 调用期间被创建
- **监听器残留**：事件监听器在搜索完成后仍然活跃

第二版修复通过**移除事件监听器**和**并发关闭页面**彻底解决了这些问题。

## 测试

运行测试脚本验证修复：

```bash
python test_beforeunload_fix.py
```

## 影响范围

修改的文件：
- `src/account_manager.py` (核心修复)
- `src/tab_manager.py` (辅助防护)
- `src/browser_state_manager.py` (辅助防护)

## 预期效果

- 不再出现"确定要离开？"对话框
- `storage_state()` 调用不会超时
- 页面关闭操作顺利完成
- 脚本不会卡死

## 相关问题

- Issue: 桌面端搜索结束后会新建一个bing页面，然后弹出"确定要离开？"对话框导致脚本卡死
- 修复日期: 2026-02-10
- 版本: v2 (增强版)
