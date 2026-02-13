# 📖 使用指南

## 📋 目录

- [快速开始](#快速开始)
- [基本使用](#基本使用)
- [配置说明](#配置说明)
- [数据面板](#数据面板)
- [常见问题](#常见问题)

---

## 快速开始

### 🎯 智能模式切换

程序会自动检测登录状态：
- **首次运行**：自动使用有头模式（显示浏览器），方便你手动登录
- **后续运行**：自动使用无头模式（后台运行），不干扰你的工作

### Windows 用户

**首次运行**：
```cmd
quick_start.bat
```
浏览器会自动打开，按照提示完成手动登录，登录成功后会自动保存会话。

**日常使用**：
```cmd
quick_start.bat              # 自动后台运行（推荐）
```

如果需要重新登录或强制显示浏览器：
```cmd
python main.py --headless=false  # 强制显示浏览器
```

**启动调度器**（每天自动运行）：
```cmd
scripts/windows/start_scheduler.bat
```

**查看数据面板**：
```cmd
scripts/windows/start_dashboard.bat
```

### Linux/macOS 用户

**首次运行**：
```bash
./scripts/unix/quick_start.sh
```

**日常使用**：
```bash
./scripts/unix/quick_start.sh        # 后台运行
./scripts/unix/start_scheduler.sh    # 启动调度器
./scripts/unix/start_dashboard.sh    # 查看数据面板
```

## 基本使用

### 运行模式

```bash
# 立即执行一次
python main.py

# 后台运行（不显示浏览器）
python main.py --headless

# 慢速模式（更安全）
python main.py --mode slow

# 启动调度器（每天自动执行）
python main.py --schedule
```

### 任务选择

```bash
# 仅桌面搜索
python main.py --desktop-only

# 仅移动搜索
python main.py --mobile-only
```

## 配置说明

编辑 `config.yaml` 进行基本配置：

### 搜索设置

```yaml
search:
  desktop_count: 30    # 桌面搜索次数
  mobile_count: 20     # 移动搜索次数
  wait_interval:
    min: 8             # 最小等待时间（秒）
    max: 20            # 最大等待时间（秒）
```

### 调度设置

```yaml
scheduler:
  enabled: true              # 启用调度器
  mode: "random"             # 随机时间模式
  random_start_hour: 8       # 开始时间
  random_end_hour: 22        # 结束时间
```

### 通知设置

详见 [通知配置指南](NOTIFICATION_GUIDE.md)

## 数据面板

启动数据面板查看今天的任务完成情况：

```bash
# Windows
scripts/windows/start_dashboard.bat

# Linux/macOS  
./scripts/unix/start_dashboard.sh

# 或直接运行
streamlit run dashboard.py
```

浏览器会自动打开 `http://localhost:8501`，显示：
- 今天还需要完成的任务
- 积分获得情况
- 历史数据趋势

## 常见问题

### Q: 首次运行需要手动登录吗？

A: 是的。首次运行会打开浏览器，需要手动登录 Microsoft 账号。登录成功后会自动保存会话，后续无需再次登录。

### Q: 会话过期了怎么办？

A: 删除 `storage_state.json` 文件，重新运行程序完成登录。

**注意**：在删除此文件前，请确保已关闭所有正在运行的脚本窗口，以防文件占用无法删除。

### Q: 积分没有增加怎么办？

A: 可能已达到每日上限。检查数据面板确认今天的任务完成情况。

### Q: 如何更安全地使用？

A: 
- 使用慢速模式：`python main.py --mode slow`
- 启用调度器在随机时间运行：`python main.py --schedule`
- 不要频繁手动运行

### Q: 程序出错了怎么办？

A: 查看日志文件 `logs/automator.log` 了解具体错误信息。

---

**使用愉快！** 🎉
