@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "REPO_DIR=%SCRIPT_DIR%..\.."
set "APP_DIR=%REPO_DIR%\ERP_Backend"
set "PYTHON_EXE=C:\Users\megaPC\AppData\Local\Python\bin\python.exe"
set "PORT=8000"

cd /d "%APP_DIR%"

if exist "%APP_DIR%\.venv\Scripts\python.exe" (
  set "PYTHON_EXE=%APP_DIR%\.venv\Scripts\python.exe"
)

echo [MegaCell ERP] Starting FastAPI on 0.0.0.0:%PORT% ...
"%PYTHON_EXE%" -m uvicorn app.main:app --host 0.0.0.0 --port %PORT% --reload

endlocal
