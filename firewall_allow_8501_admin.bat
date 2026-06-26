@echo off
setlocal

set "PORT=8501"
set "RULE_NAME=MegaCell ERP Streamlit 8501"

echo [MegaCell ERP] This script must be run as Administrator.
echo It allows inbound TCP traffic on port %PORT% for internal ERP access.
echo.

net session >nul 2>&1
if not "%ERRORLEVEL%"=="0" (
    echo Administrator permission is required.
    echo Right-click this file and choose "Run as administrator".
    pause
    exit /b 1
)

netsh advfirewall firewall show rule name="%RULE_NAME%" >nul 2>&1
if "%ERRORLEVEL%"=="0" (
    echo Firewall rule already exists: %RULE_NAME%
) else (
    netsh advfirewall firewall add rule name="%RULE_NAME%" dir=in action=allow protocol=TCP localport=%PORT%
)

echo.
echo Done. Employees on the same network can try:
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '127.*' -and $_.PrefixOrigin -ne 'WellKnown' } | ForEach-Object { '  http://' + $_.IPAddress + ':%PORT%' }"
pause

endlocal
