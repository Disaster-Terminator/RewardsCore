@echo off
chcp 65001 >nul
cd /d "%~dp0\..\.."
REM Verify Installation Script

echo ========================================
echo MS Rewards Automator - Installation Verification
echo ========================================
echo.

REM Activate conda environment
echo Activating conda environment: ms-rewards-bot
call conda activate ms-rewards-bot 2>nul
if errorlevel 1 (
    echo Note: Conda environment not activated, using system Python
    echo.
)

echo [1/5] Checking Python...
python --version
if errorlevel 1 (
    echo   X Python not found
    goto :error
) else (
    echo   OK Python installed
)

echo.
echo [2/5] Checking core dependencies...
python -c "import playwright; print('  OK playwright')" 2>nul || echo   X playwright missing
python -c "import yaml; print('  OK pyyaml')" 2>nul || echo   X pyyaml missing
python -c "import aiohttp; print('  OK aiohttp')" 2>nul || echo   X aiohttp missing

echo.
echo [3/5] Checking visualization dependencies...
python -c "import streamlit; print('  OK streamlit')" 2>nul || echo   X streamlit missing
python -c "import plotly; print('  OK plotly')" 2>nul || echo   X plotly missing
python -c "import pandas; print('  OK pandas')" 2>nul || echo   X pandas missing

echo.
echo [4/5] Checking configuration...
if exist config.yaml (
    echo   OK config.yaml found
) else (
    echo   X config.yaml not found
)

if exist tools/search_terms.txt (
    echo   OK search_terms.txt found
) else (
    echo   X search_terms.txt not found
)

echo.
echo [5/5] Checking scripts...
if exist main.py (
    echo   OK main.py found
) else (
    echo   X main.py not found
)

if exist dashboard.py (
    echo   OK dashboard.py found
) else (
    echo   X dashboard.py not found
)

echo.
echo ========================================
echo Verification Complete
echo ========================================
echo.
echo All checks passed! You can now use:
echo   - quick_start.bat (auto headless mode)
echo   - scripts\windows\start_scheduler.bat (scheduler)
echo   - scripts\windows\start_dashboard.bat (data dashboard)
echo.
goto :end

:error
echo.
echo ========================================
echo Verification Failed
echo ========================================
echo.
echo Please install missing dependencies:
echo   pip install -r requirements.txt
echo   playwright install chromium
echo.

:end
pause
