@echo off
chcp 65001 >nul
cd /d "%~dp0\..\.."
REM MS Rewards Automator - Windows Running Script

echo ========================================
echo MS Rewards Automator
echo ========================================
echo.

REM Activate conda environment if available
echo Activating conda environment: ms-rewards-bot
call conda activate ms-rewards-bot 2>nul
if errorlevel 1 (
    echo Note: Conda environment not activated, using system Python
    echo.
)

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found, please install Python 3.10+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check config file
if not exist config.yaml (
    echo [ERROR] Config file config.yaml not found
    pause
    exit /b 1
)

REM Check dependencies
echo [1/3] Checking dependencies...
echo.
python tools/check_environment.py
if errorlevel 1 (
    echo.
    echo ========================================
    echo Dependency check failed!
    echo ========================================
    echo.
    echo Would you like to install missing dependencies? (Y/N)
    set /p install_deps=
    if /i "%install_deps%"=="Y" (
        echo.
        echo Installing dependencies...
        pip install -r requirements.txt
        playwright install chromium
        echo.
        echo Dependencies installed. Please run the script again.
        pause
        exit /b 0
    ) else (
        echo.
        echo Installation cancelled. Please install dependencies manually.
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo Dependencies check passed!
echo ========================================

echo.
echo [2/3] Starting program...
echo.

REM Run main program
python main.py %*

echo.
echo [3/3] Program completed
echo.

REM Ask to view log
echo View log? (Y/N)
set /p view_log=
if /i "%view_log%"=="Y" (
    type logs\automator.log
)

pause
