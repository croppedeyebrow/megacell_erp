@echo off
setlocal EnableExtensions

set "APP_DIR=%~dp0"
set "APP_DIR=%APP_DIR:~0,-1%"
set "PORT=8501"
set "URL=http://localhost:%PORT%"
set "LOG_FILE=%APP_DIR%\logs\streamlit.log"
set "NO_PAUSE=0"

if /I "%~1"=="--no-pause" set "NO_PAUSE=1"

echo [MegaCell ERP] Server status
echo Project: %APP_DIR%
echo Port   : %PORT%
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "$conns = Get-NetTCPConnection -LocalPort %PORT% -State Listen -ErrorAction SilentlyContinue; if (-not $conns) { Write-Output 'Status : STOPPED'; exit 0 }; Write-Output 'Status : RUNNING'; foreach ($conn in $conns) { $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue; if ($proc) { Write-Output ('PID    : ' + $conn.OwningProcess + ' (' + $proc.ProcessName + ')') } }"

echo.
echo Local URL:
echo   %URL%
echo.
echo Internal network URLs on this PC:
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' -and $_.PrefixOrigin -ne 'WellKnown' } | ForEach-Object { '  http://' + $_.IPAddress + ':%PORT%' }"

echo.
echo Log file:
echo   %LOG_FILE%
if exist "%LOG_FILE%" (
    echo.
    echo Last log lines:
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-Content -LiteralPath '%LOG_FILE%' -Tail 20 -ErrorAction SilentlyContinue"
)

echo.
if not "%NO_PAUSE%"=="1" pause

endlocal
