@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "REPO_DIR=%SCRIPT_DIR%..\.."
set "BACKEND_DIR=%REPO_DIR%\ERP_Backend"
set "FRONT_DIR=%REPO_DIR%\ERP_Front"
set "PYTHON_EXE=C:\Users\megaPC\AppData\Local\Python\bin\python.exe"

if exist "%BACKEND_DIR%\.venv\Scripts\python.exe" (
  set "PYTHON_EXE=%BACKEND_DIR%\.venv\Scripts\python.exe"
)

if not exist "%FRONT_DIR%\node_modules\" (
  echo [MegaCell ERP] ERP_Front\node_modules not found. Running yarn install --frozen-lockfile...
  pushd "%FRONT_DIR%"
  call yarn install --frozen-lockfile
  if errorlevel 1 (
    echo [MegaCell ERP] yarn install --frozen-lockfile failed.
    popd
    exit /b 1
  )
  popd
)

echo [MegaCell ERP] Starting FastAPI and React development servers...
echo   API   http://localhost:8000/docs
echo   Front http://localhost:5173
echo.
echo Close each server window or run stop_dev.bat to stop them.

start "MegaCell API :8000" /D "%BACKEND_DIR%" cmd /k ""%PYTHON_EXE%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 2 /nobreak >nul
start "MegaCell Front :5173" /D "%FRONT_DIR%" cmd /k "yarn dev"

endlocal
