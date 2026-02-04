#!/bin/bash
# 快速启动脚本 - 无头模式

# Change to project root directory
cd "$(dirname "$0")/../.."

# 尝试激活 conda 环境
if command -v conda &> /dev/null; then
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate ms-rewards-bot 2>/dev/null || echo "Note: Using system Python"
fi

echo "启动 MS Rewards Automator (无头模式)..."
python3 main.py --headless
