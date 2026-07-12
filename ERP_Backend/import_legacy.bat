@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "REPO_DIR=%SCRIPT_DIR%.."
set "APP_DIR=%REPO_DIR%"
set "PYTHON_EXE=%APP_DIR%\.venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
  echo [MegaCell ERP] .venv 가 없습니다. 먼저 python -m venv .venv ^& pip install -r requirements.txt
  exit /b 1
)

cd /d "%APP_DIR%"
set PYTHONPATH=.

if "%~1"=="" (
  echo [MegaCell ERP] Importing legacy SQLite erp_orders ...
  "%PYTHON_EXE%" -m app.workers.import_legacy_sqlite
) else (
  echo [MegaCell ERP] Importing from %~1 ...
  "%PYTHON_EXE%" -m app.workers.import_legacy_sqlite --source "%~1"
)

endlocal
