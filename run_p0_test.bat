@echo off
REM P0模块快速测试脚本（Windows）

echo ========================================
echo P0模块集成测试
echo ========================================
echo.

REM 1. 运行集成测试
echo [1/3] 运行集成测试...
python test_p0_integration.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 集成测试失败！请检查错误信息。
    pause
    exit /b 1
)

echo.
echo ========================================
echo 集成测试通过！
echo ========================================
echo.

REM 2. 询问是否运行主程序
echo 是否运行主程序进行实际测试？
echo.
echo 选项:
echo   1 - 快速测试（仅桌面搜索，1次）
echo   2 - 完整测试（桌面+移动+任务）
echo   3 - 跳过
echo.
set /p choice="请选择 (1/2/3): "

if "%choice%"=="1" (
    echo.
    echo [2/3] 运行快速测试...
    python main.py --mode fast --desktop-only
) else if "%choice%"=="2" (
    echo.
    echo [2/3] 运行完整测试...
    python main.py
) else (
    echo.
    echo 跳过主程序测试
)

echo.
echo ========================================
echo 测试完成！
echo ========================================
echo.
echo 提示:
echo - 查看日志: logs\automator.log
echo - 配置文件: config.yaml
echo - 集成指南: docs\P0_INTEGRATION_GUIDE.md
echo.

pause
