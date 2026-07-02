@echo off
setlocal

set "PORT=8501"

netstat -ano | findstr /R /C:":%PORT% .*LISTENING" >nul
if errorlevel 1 (
    echo [MegaCell ERP] Server is not listening on port %PORT%.
    exit /b 1
)

echo [MegaCell ERP] Server is listening on port %PORT%.
exit /b 0
