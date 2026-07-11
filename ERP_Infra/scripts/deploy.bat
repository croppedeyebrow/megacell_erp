@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "REPO_DIR=%SCRIPT_DIR%..\.."

cd /d "%REPO_DIR%"

echo [MegaCell ERP] Pulling latest code from GitHub ...
git pull
if errorlevel 1 (
    echo [MegaCell ERP] git pull failed. Deployment stopped.
    pause
    exit /b 1
)

call "%SCRIPT_DIR%stop_server.bat"

echo [MegaCell ERP] Starting FastAPI ...
call "%SCRIPT_DIR%run_server.bat"

endlocal
