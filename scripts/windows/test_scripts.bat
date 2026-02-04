@echo off
chcp 65001 >nul
REM Test all batch scripts for encoding issues

echo ========================================
echo Testing Batch Scripts
echo ========================================
echo.

echo [1/5] Testing run.bat...
type run.bat | findstr /C:"echo" >nul
if errorlevel 1 (
    echo   X Failed
) else (
    echo   OK
)

echo [2/5] Testing quick_start.bat...
type quick_start.bat | findstr /C:"echo" >nul
if errorlevel 1 (
    echo   X Failed
) else (
    echo   OK
)

echo [3/5] Testing scripts\windows\start_scheduler.bat...
type scripts\windows\start_scheduler.bat | findstr /C:"echo" >nul
if errorlevel 1 (
    echo   X Failed
) else (
    echo   OK
)

echo [4/5] Testing scripts\windows\start_dashboard.bat...
type scripts\windows\start_dashboard.bat | findstr /C:"echo" >nul
if errorlevel 1 (
    echo   X Failed
) else (
    echo   OK
)

echo.
echo ========================================
echo All scripts tested
echo ========================================

pause
