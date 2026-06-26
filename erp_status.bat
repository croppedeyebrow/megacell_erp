@echo off
setlocal

set "PORT=8501"

echo [MegaCell ERP] Server status
echo.
netstat -ano | findstr ":%PORT%" | findstr "LISTENING"
if errorlevel 1 (
    echo Server is NOT running on port %PORT%.
) else (
    echo Server is running on port %PORT%.
)

echo.
echo Internal network URLs on this PC:
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '127.*' -and $_.PrefixOrigin -ne 'WellKnown' } | ForEach-Object { '  http://' + $_.IPAddress + ':%PORT%' }"

echo.
echo If employees cannot connect, run firewall_allow_8501_admin.bat as administrator.
pause

endlocal
