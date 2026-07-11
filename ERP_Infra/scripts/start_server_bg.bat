@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "REPO_DIR=%SCRIPT_DIR%..\.."
set "APP_DIR=%REPO_DIR%\ERP_Backend"
set "PORT=8000"
set "LOG_DIR=%APP_DIR%\logs"
set "DEPLOY_LOG=%LOG_DIR%\deploy.log"
set "RUNNER=%SCRIPT_DIR%run_server_logged.bat"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

cd /d "%APP_DIR%"

echo [%date% %time%] Starting FastAPI in background on 0.0.0.0:%PORT% >> "%DEPLOY_LOG%"

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$runner=(Resolve-Path $env:RUNNER).Path; Start-Process -FilePath 'cmd.exe' -ArgumentList '/d','/c',('""' + $runner + '""') -WindowStyle Hidden"
powershell.exe -NoProfile -Command "Start-Sleep -Seconds 7"

call "%SCRIPT_DIR%status_server.bat"

endlocal
