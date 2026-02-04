@echo off
chcp 65001 >nul
cd /d "%~dp0\..\.."
REM Start Data Visualization Dashboard

echo ========================================
echo MS Rewards Automator - Dashboard
echo ========================================
echo.

REM Activate conda environment
call conda activate ms-rewards-bot 2>nul
if errorlevel 1 (
    echo Note: Conda environment not activated, using system Python
    echo.
)

echo Starting dashboard...
echo Browser will open at http://localhost:8501
echo.

streamlit run dashboard.py

pause
