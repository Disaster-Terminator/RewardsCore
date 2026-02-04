#!/bin/bash
# 启动数据可视化面板

# Change to project root directory
cd "$(dirname "$0")/../.."

# 尝试激活 conda 环境
if command -v conda &> /dev/null; then
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate ms-rewards-bot 2>/dev/null || echo "Note: Using system Python"
fi

echo "========================================"
echo "MS Rewards Automator - 数据面板"
echo "========================================"
echo ""
echo "正在启动数据面板..."
echo "浏览器将自动打开 http://localhost:8501"
echo ""

streamlit run dashboard.py
