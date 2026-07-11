@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "REPO_DIR=%SCRIPT_DIR%..\.."
set "APP_DIR=%REPO_DIR%\ERP_Backend\legacy\streamlit"
set "PYTHON_EXE=C:\Users\megaPC\AppData\Local\Python\bin\python.exe"
set "PORT=8501"

cd /d "%APP_DIR%"

echo [MegaCell ERP] Starting LEGACY Streamlit on 0.0.0.0:%PORT% ...
echo [MegaCell ERP] Primary backend is FastAPI on port 8000. Use run_server.bat for production path.
"%PYTHON_EXE%" -m streamlit run app.py --server.address 0.0.0.0 --server.port %PORT%

endlocal
