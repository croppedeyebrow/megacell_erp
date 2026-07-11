@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "REPO_DIR=%SCRIPT_DIR%..\.."
set "APP_DIR=%REPO_DIR%\ERP_Backend"
set "LOG_DIR=%APP_DIR%\logs"
set "DEPLOY_LOG=%LOG_DIR%\deploy.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

cd /d "%REPO_DIR%"

echo [%date% %time%] Deploy started. >> "%DEPLOY_LOG%"
echo [MegaCell ERP] Pulling latest code from GitHub ...
git pull >> "%DEPLOY_LOG%" 2>&1
if errorlevel 1 (
    echo [MegaCell ERP] git pull failed. See ERP_Backend\logs\deploy.log.
    echo [%date% %time%] git pull failed. >> "%DEPLOY_LOG%"
    exit /b 1
)

call "%SCRIPT_DIR%stop_server.bat" >> "%DEPLOY_LOG%" 2>&1

echo [MegaCell ERP] Starting FastAPI in background ...
call "%SCRIPT_DIR%start_server_bg.bat"
if errorlevel 1 (
    echo [MegaCell ERP] Server start failed. See ERP_Backend\logs\server.log and deploy.log.
    echo [%date% %time%] Server start failed. >> "%DEPLOY_LOG%"
    exit /b 1
)

echo [%date% %time%] Deploy finished. >> "%DEPLOY_LOG%"
echo [MegaCell ERP] Deploy finished.

endlocal
