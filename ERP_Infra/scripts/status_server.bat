@echo off
setlocal

set "PORT=8000"

netstat -ano | findstr /R /C:":%PORT% .*LISTENING" >nul
if errorlevel 1 (
    echo [MegaCell ERP] FastAPI is not listening on port %PORT%.
    exit /b 1
)

echo [MegaCell ERP] FastAPI is listening on port %PORT%.
exit /b 0
