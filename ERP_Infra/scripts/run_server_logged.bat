@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "REPO_DIR=%SCRIPT_DIR%..\.."
set "APP_DIR=%REPO_DIR%\ERP_Backend"
set "PYTHON_EXE=C:\Users\megaPC\AppData\Local\Python\bin\python.exe"
set "PORT=8000"
set "LOG_DIR=%APP_DIR%\logs"
set "SERVER_LOG=%LOG_DIR%\server.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

cd /d "%APP_DIR%"

if exist "%APP_DIR%\.venv\Scripts\python.exe" (
  set "PYTHON_EXE=%APP_DIR%\.venv\Scripts\python.exe"
)

echo.>> "%SERVER_LOG%"
echo [%date% %time%] Starting FastAPI on 0.0.0.0:%PORT% >> "%SERVER_LOG%"
"%PYTHON_EXE%" -m uvicorn app.main:app --host 0.0.0.0 --port %PORT% >> "%SERVER_LOG%" 2>&1
echo [%date% %time%] FastAPI process stopped. >> "%SERVER_LOG%"

endlocal
