@echo off
cd /d "%~dp0"

REM Activate conda environment
call conda activate ms-rewards-bot 2>nul

call scripts\windows\run.bat %*
