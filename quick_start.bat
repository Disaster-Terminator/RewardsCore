@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM Activate conda environment
call conda activate ms-rewards-bot 2>nul

call scripts\windows\quick_start.bat %*
