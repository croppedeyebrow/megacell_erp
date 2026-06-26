@echo off
setlocal

set "APP_DIR=C:\Users\megaPC\Desktop\megacell_erp"
set "PORT=8501"
set "URL=http://localhost:%PORT%"

echo [MegaCell ERP] Checking server on port %PORT%...

powershell -NoProfile -ExecutionPolicy Bypass -Command "$conn = Get-NetTCPConnection -LocalPort %PORT% -State Listen -ErrorAction SilentlyContinue; if ($conn) { exit 10 } else { exit 0 }"
if "%ERRORLEVEL%"=="10" (
    echo [MegaCell ERP] Server is already running.
    start "" "%URL%"
    goto :show_network
)

if not exist "%APP_DIR%\app.py" (
    echo [MegaCell ERP] app.py was not found.
    echo %APP_DIR%
    pause
    exit /b 1
)

echo [MegaCell ERP] Starting Streamlit server...
start "MegaCell ERP Server" /D "%APP_DIR%" cmd /k "python -m streamlit run app.py --server.address=0.0.0.0 --server.port=%PORT%"

timeout /t 7 /nobreak >nul
start "" "%URL%"

:show_network
echo.
echo [MegaCell ERP] Local URL:
echo   %URL%
echo.
echo [MegaCell ERP] Internal network URLs on this PC:
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '127.*' -and $_.PrefixOrigin -ne 'WellKnown' } | ForEach-Object { '  http://' + $_.IPAddress + ':%PORT%' }"
echo.
echo Other employees can open the internal network URL if Windows Firewall allows port %PORT%.
echo Keep the server window open while using ERP.
echo.
pause

endlocal
