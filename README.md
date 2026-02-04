# 🎯 MS Rewards Automator

自动化完成 Microsoft Rewards 任务，轻松赚取积分。

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.40+-green.svg)](https://playwright.dev/)
[![Maintained](https://img.shields.io/badge/Maintained-Yes-brightgreen.svg)](https://github.com/yourusername/ms-rewards-automator)
[![Open Source](https://img.shields.io/badge/Open%20Source-Yes-orange.svg)](LICENSE)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ⚠️ 免责声明

**本项目仅供学习和研究使用。使用自动化工具可能违反 Microsoft Rewards 服务条款，可能导致账号被限制或封禁。使用本工具造成的任何后果由使用者自行承担，作者不承担任何责任。**

## ✨ 功能特性

- 🔍 **自动搜索**: 自动完成桌面端（30次）和移动端（20次）搜索任务
- 🎭 **反检测**: 集成 playwright-stealth，模拟真实用户行为
- 🔐 **会话持久化**: 一次登录，长期使用
- 📊 **积分监控**: 实时监控积分变化，智能检测异常
- 🔔 **多渠道通知**: 支持 Telegram、Server酱、WhatsApp 推送
- ⏰ **智能调度**: 支持定时执行和随机时间调度
- 📈 **数据可视化**: 内置 Web Dashboard，支持展示 7 天积分增长曲线

## 🛠️ 工作原理

- **Session 持久化**: 仅需一次手动登录，保存加密后的 storage_state，后续任务通过 Cookie 直接进入
- **智能模拟**: 并非简单的协议请求，而是使用 Playwright 驱动真实浏览器内核，执行带有随机偏移的点击、缓动滚动和人类打字模拟
- **动态适应**: 针对 Microsoft Rewards 频繁变动的 UI，采用多重选择器降级算法，确保解析的高可用性
- **反检测优化**: 实现加权随机时间分布，避开高峰时段，降低被检测风险

## 🔒 隐私声明

本项目绝不存储您的 Microsoft 账号明文密码。所有登录凭证（Cookies）均以加密形式存储在您的本地 `storage_state.json` 中。项目不会向除 Microsoft 和您配置的通知渠道以外的任何第三方发送数据。

## 📋 目录

- [快速开始](#-快速开始)
- [详细文档](#-详细文档)
- [风险提示](#-风险提示)
- [项目结构](#-项目结构)
- [许可证](#-许可证)

## 🚀 快速开始

### 1. 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/ms-rewards-automator.git
cd ms-rewards-automator

# 创建 Conda 环境（推荐）
conda env create -f environment.yml
conda activate ms-rewards-bot

# 或使用 pip
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 安装浏览器
playwright install chromium
# 注意：如果您在 Linux 上运行，可能需要额外安装系统依赖库

# 验证安装
python tools/check_environment.py
```

### 2. 首次运行

```bash
# Windows 用户
quick_start.bat

# 或直接运行
python main.py
```

**智能模式**：程序会自动检测登录状态
- 首次运行时，浏览器会自动打开（有头模式），请手动登录 Microsoft 账号
- 登录成功后会自动保存会话，后续运行将自动切换到无头模式（后台运行）
- 如需重新登录，删除 `storage_state.json` 文件即可

### 3. 查看任务完成情况

```bash
# Windows 用户
scripts/windows/start_dashboard.bat

# 或直接运行
streamlit run dashboard.py
```

浏览器会打开 Dashboard，显示今天的任务完成情况（桌面搜索 X/30，移动搜索 X/20）和 7 天积分增长曲线。

### 4. 配置通知（可选）

编辑 `config.yaml` 配置 Telegram、Server酱或 WhatsApp 通知，详见 [通知配置指南](docs/guides/NOTIFICATION_GUIDE.md)。

## 📚 详细文档

**用户文档**：
- **[使用指南](docs/guides/USAGE_GUIDE.md)** - 完整的使用说明和命令参数
- **[通知配置](docs/guides/NOTIFICATION_GUIDE.md)** - Telegram、Server酱、WhatsApp 配置
- **[故障排除](docs/guides/TROUBLESHOOTING.md)** - 常见问题和解决方案

**开发者文档**：
- **[🚀 深度解析：本项目如何应对复杂的反爬虫检测？](docs/development/DEVELOPER_NOTES.md)** - 深入了解本项目在异步页面管理、动态 DOM 解析以及加权随机算法等方面的工程实现细节

## ⚠️ 风险提示

**重要**: 本工具仅供学习和研究使用。使用自动化工具可能违反 Microsoft Rewards 服务条款，可能导致账号被限制或封禁。

**建议**:
- ✅ 在本地运行，使用家庭网络
- ✅ 使用 `slow` 模式（`python main.py --mode slow`）
- ✅ 启用调度器在随机时间执行（`python main.py --schedule`）
- ❌ 不要在云服务器或 GitHub Actions 上运行
- ❌ 不要短时间内多次运行

使用本工具造成的任何后果由使用者自行承担。

## 📁 项目结构

```
ms-rewards-automator/
├── src/                    # 源代码目录
├── tools/                  # 辅助工具
│   ├── check_environment.py  # 环境检查
│   ├── run_tests.py          # 测试运行器
│   └── search_terms.txt      # 搜索词库
├── tests/                  # 单元测试
├── docs/                   # 文档目录
│   ├── guides/            # 使用指南
│   └── development/       # 开发文档
├── logs/                   # 日志文件
├── scripts/                # 启动脚本
│   ├── windows/           # Windows 脚本
│   └── unix/              # Unix/Linux 脚本
├── main.py                 # 主程序入口
├── dashboard.py            # 数据面板
├── config.yaml             # 配置文件
└── requirements.txt        # Python 依赖
```

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [Playwright](https://playwright.dev/) - 浏览器自动化框架
- [playwright-stealth](https://github.com/AtuboDad/playwright_stealth) - 反检测插件
- [Streamlit](https://streamlit.io/) - 数据可视化框架

---

**如果觉得有用，请给个 ⭐ Star！**

