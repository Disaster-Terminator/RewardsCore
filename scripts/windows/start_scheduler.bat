@echo off
chcp 65001 >nul
cd /d "%~dp0\..\.."
REM Start Scheduler - Daily Auto Execution

echo ========================================
echo MS Rewards Automator - Scheduler Mode
echo ========================================
echo.

REM Activate conda environment
call conda activate ms-rewards-bot 2>nul
if errorlevel 1 (
    echo Note: Conda environment not activated, using system Python
    echo.
)

echo Scheduler will run in background and execute tasks daily
echo Press Ctrl+C to stop
echo.

python main.py --schedule --headless

pause
