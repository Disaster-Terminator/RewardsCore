@echo off
chcp 65001 >nul
cd /d "%~dp0\..\.."
REM Quick Start Script - With Browser Window

echo ========================================
echo MS Rewards Automator - Quick Start
echo ========================================
echo.

REM Activate conda environment
echo Activating conda environment: ms-rewards-bot
call conda activate ms-rewards-bot
if errorlevel 1 (
    echo Warning: Failed to activate conda environment
    echo Trying to run with current Python environment...
    echo.
)

echo Starting MS Rewards Automator...
python main.py
pause
