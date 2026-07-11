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
  echo [MegaCell ERP] ERP_Front\node_modules 없음. npm install 실행 중...
  pushd "%FRONT_DIR%"
  call npm install
  if errorlevel 1 (
    echo [MegaCell ERP] npm install 실패.
    popd
    exit /b 1
  )
  popd
)

echo [MegaCell ERP] FastAPI + React 개발 서버를 시작합니다.
echo   API   http://localhost:8000/docs
echo   Front http://localhost:5173
echo.
echo 각 창을 닫거나 stop_dev.bat 으로 종료할 수 있습니다.

start "MegaCell API :8000" /D "%BACKEND_DIR%" cmd /k ""%PYTHON_EXE%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 2 /nobreak >nul
start "MegaCell Front :5173" /D "%FRONT_DIR%" cmd /k "npm run dev"

endlocal
