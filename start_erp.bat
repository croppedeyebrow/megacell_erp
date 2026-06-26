@echo off
setlocal EnableExtensions

set "APP_DIR=%~dp0"
set "APP_DIR=%APP_DIR:~0,-1%"
set "PORT=8501"
set "URL=http://localhost:%PORT%"
set "LOG_DIR=%APP_DIR%\logs"
set "LOG_FILE=%LOG_DIR%\streamlit.log"
set "NO_PAUSE=0"
set "NO_BROWSER=0"

:parse_args
if "%~1"=="" goto args_done
if /I "%~1"=="--no-pause" set "NO_PAUSE=1"
if /I "%~1"=="--no-browser" set "NO_BROWSER=1"
shift
goto parse_args

:args_done

echo [MegaCell ERP] Start request
echo Project: %APP_DIR%
echo Port   : %PORT%
echo.

if not exist "%APP_DIR%\app.py" (
    echo [ERROR] app.py was not found in:
    echo %APP_DIR%
    if not "%NO_PAUSE%"=="1" pause
    exit /b 1
)

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$conn = Get-NetTCPConnection -LocalPort %PORT% -State Listen -ErrorAction SilentlyContinue; if ($conn) { exit 10 } else { exit 0 }"
if "%ERRORLEVEL%"=="10" (
    echo [MegaCell ERP] Server is already running on port %PORT%.
    if not "%NO_BROWSER%"=="1" start "" "%URL%"
    goto :show_urls
)

set "PY_EXE=%LOCALAPPDATA%\Python\bin\python.exe"
if exist "%PY_EXE%" (
    set "PY_LABEL=%PY_EXE%"
) else (
    echo [ERROR] Python was not found at:
    echo %PY_EXE%
    echo Install Python or update start_erp.bat with the correct Python path.
    if not "%NO_PAUSE%"=="1" pause
    exit /b 1
)

echo [MegaCell ERP] Starting Streamlit server...
echo [MegaCell ERP] Python  : %PY_LABEL%
echo [MegaCell ERP] Log file: %LOG_FILE%
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "$cmd = '\"' + $env:PY_EXE + '\" -m streamlit run app.py --server.address=0.0.0.0 --server.port=' + $env:PORT + ' --server.headless=true > \"' + $env:LOG_FILE + '\" 2>&1'; Start-Process -FilePath 'cmd.exe' -ArgumentList @('/c', $cmd) -WorkingDirectory $env:APP_DIR -WindowStyle Hidden"

timeout /t 5 /nobreak >nul

powershell -NoProfile -ExecutionPolicy Bypass -Command "$conn = Get-NetTCPConnection -LocalPort %PORT% -State Listen -ErrorAction SilentlyContinue; if ($conn) { exit 0 } else { exit 20 }"
if "%ERRORLEVEL%"=="20" (
    echo [ERROR] Server did not start on port %PORT%.
    echo Check the log file:
    echo %LOG_FILE%
    echo.
    if exist "%LOG_FILE%" type "%LOG_FILE%"
    if not "%NO_PAUSE%"=="1" pause
    exit /b 1
)

if not "%NO_BROWSER%"=="1" start "" "%URL%"

:show_urls
echo.
echo [MegaCell ERP] Local URL:
echo   %URL%
echo.
echo [MegaCell ERP] Internal network URLs on this PC:
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' -and $_.PrefixOrigin -ne 'WellKnown' } | ForEach-Object { '  http://' + $_.IPAddress + ':%PORT%' }"
echo.
echo If other employees cannot connect, run firewall_allow_8501_admin.bat as administrator.
echo Use stop_erp.bat to stop the server.
echo.
if not "%NO_PAUSE%"=="1" pause

endlocal
