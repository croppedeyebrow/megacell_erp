@echo off
setlocal

set "PORT=8501"
set "PID="

for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do set "PID=%%P"

if "%PID%"=="" (
    echo [MegaCell ERP] Server is not running on port %PORT%.
    pause
    exit /b 0
)

echo [MegaCell ERP] Stopping server on port %PORT%. PID=%PID%
taskkill /PID %PID% /F
echo [MegaCell ERP] Stopped.
pause

endlocal
