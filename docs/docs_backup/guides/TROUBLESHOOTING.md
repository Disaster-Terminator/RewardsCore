# 🔧 故障排除指南

## 目录
- [常见问题](#常见问题)
- [错误解决](#错误解决)
- [使用建议](#使用建议)

---

## 常见问题

### 无头模式看不到浏览器

**设计行为**：程序会自动检测登录状态，首次运行会显示浏览器，后续运行会自动切换到无头模式（后台运行）。

如果想强制显示浏览器：
```cmd
python main.py --headless=false
```

### 会话过期需要重新登录

**解决方法**：
1. 删除 `storage_state.json` 文件
2. 运行 `quick_start.bat`
3. 手动完成登录

### 积分没有增加

**可能原因**：
- 已达到每日搜索上限（桌面30次，移动20次）
- 积分延迟更新
- 网络问题

**解决方法**：
- 查看数据面板确认今天的任务完成情况
- 等待几分钟后再检查
- 使用慢速模式：`python main.py --mode slow`

## 错误解决

### Python 未找到

```
'python' is not recognized as an internal or external command
```

**解决**：确认 Python 已安装并添加到 PATH，或尝试使用 `py` 命令。

### 模块未找到

```
ModuleNotFoundError: No module named 'xxx'
```

**解决**：
```cmd
pip install -r requirements.txt
```

### 浏览器启动失败

```
Executable doesn't exist at xxx
```

**解决**：
```cmd
playwright install chromium
```

### 端口被占用（数据面板）

```
Address already in use
```

**解决**：关闭其他占用 8501 端口的程序，或重启电脑。

## 使用建议

### 安全使用

- ✅ 使用慢速模式：`python main.py --mode slow`
- ✅ 启用调度器随机时间运行
- ✅ 不要频繁手动运行
- ❌ 不要在短时间内多次运行

### 查看日志

出现问题时，查看日志文件：
```cmd
notepad logs\automator.log
```

### 获取帮助

如果问题仍未解决，查看日志文件并提交 GitHub Issue。

---

**现在可以正常使用了！** 🎉