@echo off
setlocal enabledelayedexpansion

echo [MegaCell ERP] Stopping FastAPI (:8000) and Vite (:5173) ...

for %%P in (8000 5173) do (
  set "FOUND=0"
  for /f "tokens=5" %%A in ('netstat -ano ^| findstr /R /C:":%%P .*LISTENING"') do (
    set "PID=%%A"
    if not "!PID!"=="" (
      set "FOUND=1"
      echo   Stopping port %%P PID !PID!
      taskkill /F /PID !PID! >nul 2>&1
    )
  )
  if "!FOUND!"=="0" echo   Port %%P: not running
)

echo Done.
endlocal
