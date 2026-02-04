#!/bin/bash
# 启动调度器 - 每天自动执行

# Change to project root directory
cd "$(dirname "$0")/../.."

# 尝试激活 conda 环境
if command -v conda &> /dev/null; then
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate ms-rewards-bot 2>/dev/null || echo "Note: Using system Python"
fi

echo "========================================"
echo "MS Rewards Automator - 调度模式"
echo "========================================"
echo ""
echo "调度器将在后台运行，每天自动执行任务"
echo "按 Ctrl+C 停止"
echo ""

python3 main.py --schedule --headless
