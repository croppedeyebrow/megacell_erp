@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "APP_DIR=%SCRIPT_DIR%..\.."
set "LOG_DIR=%APP_DIR%\logs"
set "DEPLOY_LOG=%LOG_DIR%\deploy.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

cd /d "%APP_DIR%"

echo [%date% %time%] Deploy started. >> "%DEPLOY_LOG%"
echo [MegaCell ERP] Pulling latest code from GitHub ...
git pull >> "%DEPLOY_LOG%" 2>&1
if errorlevel 1 (
    echo [MegaCell ERP] git pull failed. See logs\deploy.log.
    echo [%date% %time%] git pull failed. >> "%DEPLOY_LOG%"
    exit /b 1
)

call "%SCRIPT_DIR%stop_server.bat" >> "%DEPLOY_LOG%" 2>&1

echo [MegaCell ERP] Starting updated server in background ...
call "%SCRIPT_DIR%start_server_bg.bat"
if errorlevel 1 (
    echo [MegaCell ERP] Server start failed. See logs\server.log and logs\deploy.log.
    echo [%date% %time%] Server start failed. >> "%DEPLOY_LOG%"
    exit /b 1
)

echo [%date% %time%] Deploy finished. >> "%DEPLOY_LOG%"
echo [MegaCell ERP] Deploy finished.

endlocal
