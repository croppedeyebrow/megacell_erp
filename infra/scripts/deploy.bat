@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "APP_DIR=%SCRIPT_DIR%..\.."

cd /d "%APP_DIR%"

echo [MegaCell ERP] Pulling latest code from GitHub ...
git pull
if errorlevel 1 (
    echo [MegaCell ERP] git pull failed. Deployment stopped.
    pause
    exit /b 1
)

call "%SCRIPT_DIR%stop_server.bat"

echo [MegaCell ERP] Starting updated server ...
call "%SCRIPT_DIR%run_server.bat"

endlocal
