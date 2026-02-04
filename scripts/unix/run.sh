#!/bin/bash
# MS Rewards Automator - Linux/macOS 运行脚本

# Change to project root directory
cd "$(dirname "$0")/../.."

echo "========================================"
echo "MS Rewards Automator"
echo "========================================"
echo ""

# 尝试激活 conda 环境
if command -v conda &> /dev/null; then
    echo "Activating conda environment: ms-rewards-bot"
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate ms-rewards-bot 2>/dev/null || echo "Note: Conda environment not activated, using system Python"
    echo ""
fi

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python，请先安装 Python 3.10+"
    echo "安装方法: https://www.python.org/downloads/"
    exit 1
fi

# 检查配置文件
if [ ! -f config.yaml ]; then
    echo "[错误] 未找到配置文件 config.yaml"
    echo "请先复制 config.yaml.example 并修改配置"
    exit 1
fi

# 检查依赖
echo "[1/3] 检查依赖..."
python3 tools/check_environment.py
if [ $? -ne 0 ]; then
    echo ""
    echo "[提示] 依赖检查失败，是否安装依赖？ (y/n)"
    read -r install_deps
    if [ "$install_deps" = "y" ] || [ "$install_deps" = "Y" ]; then
        echo "安装依赖..."
        pip3 install -r requirements.txt
        playwright install chromium
    else
        echo "已取消"
        exit 1
    fi
fi

echo ""
echo "[2/3] 启动程序..."
echo ""

# 运行主程序
python3 main.py "$@"

echo ""
echo "[3/3] 程序执行完成"
echo ""

# 询问是否查看日志
echo "是否查看日志？ (y/n)"
read -r view_log
if [ "$view_log" = "y" ] || [ "$view_log" = "Y" ]; then
    cat logs/automator.log
fi
