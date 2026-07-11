@echo off
setlocal enabledelayedexpansion

set "PORT=8000"
set "FOUND=0"

echo [MegaCell ERP] Searching for a process listening on port %PORT% ...

for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do (
    set "PID=%%P"
    if not "!PID!"=="" (
        set "FOUND=1"
        echo [MegaCell ERP] Stopping PID !PID! ...
        taskkill /F /PID !PID!
    )
)

if "!FOUND!"=="0" (
    echo [MegaCell ERP] No running FastAPI server found on port %PORT%.
)

endlocal
