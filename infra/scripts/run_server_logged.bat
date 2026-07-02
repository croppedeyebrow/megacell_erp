@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "APP_DIR=%SCRIPT_DIR%..\.."
set "PYTHON_EXE=C:\Users\megaPC\AppData\Local\Python\bin\python.exe"
set "PORT=8501"
set "LOG_DIR=%APP_DIR%\logs"
set "SERVER_LOG=%LOG_DIR%\server.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

cd /d "%APP_DIR%"

echo.>> "%SERVER_LOG%"
echo [%date% %time%] Starting Streamlit on 0.0.0.0:%PORT% >> "%SERVER_LOG%"
"%PYTHON_EXE%" -m streamlit run app.py --server.address 0.0.0.0 --server.port %PORT% >> "%SERVER_LOG%" 2>&1
echo [%date% %time%] Streamlit process stopped. >> "%SERVER_LOG%"

endlocal
