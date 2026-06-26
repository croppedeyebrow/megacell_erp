@echo off
setlocal EnableExtensions

set "PORT=8501"
set "NO_PAUSE=0"

if /I "%~1"=="--no-pause" set "NO_PAUSE=1"

echo [MegaCell ERP] Stop request
echo Port: %PORT%
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "$conns = Get-NetTCPConnection -LocalPort %PORT% -State Listen -ErrorAction SilentlyContinue; if (-not $conns) { Write-Output '[MegaCell ERP] Server is not running.'; exit 0 }; $procIds = $conns | Select-Object -ExpandProperty OwningProcess -Unique; foreach ($procId in $procIds) { $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue; if ($proc) { Write-Output ('[MegaCell ERP] Stopping PID=' + $procId + ' Process=' + $proc.ProcessName); Stop-Process -Id $procId -Force } }; Write-Output '[MegaCell ERP] Stop command completed.'"

echo.
if not "%NO_PAUSE%"=="1" pause

endlocal
