@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "APP_DIR=%SCRIPT_DIR%..\.."
set "PYTHON_EXE=C:\Users\megaPC\AppData\Local\Python\bin\python.exe"
set "PORT=8501"

cd /d "%APP_DIR%"

echo [MegaCell ERP] Starting Streamlit on 0.0.0.0:%PORT% ...
"%PYTHON_EXE%" -m streamlit run app.py --server.address 0.0.0.0 --server.port %PORT%

endlocal
