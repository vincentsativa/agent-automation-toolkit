@echo off
setlocal enabledelayedexpansion
cd /d "%LOCALAPPDATA%\hermes"
echo Repairing Hermes python environment...

set "VENV="
for /f "usebackq delims=" %%P in (`powershell -NoProfile -Command "(Get-ChildItem $env:LOCALAPPDATA\hermes\installs\*\facts.json -ErrorAction SilentlyContinue | Sort-Object LastWriteTime | Select-Object -Last 1 | ForEach-Object { (Get-Content $_ -Raw | ConvertFrom-Json).packages.venv.environment })"`) do set "VENV=%%P"

if not defined VENV (
    echo FAILED - could not locate the managed environment under %LOCALAPPDATA%\hermes\installs
    pause
    exit /b 1
)
echo Environment: %VENV%

"%LOCALAPPDATA%\hermes\bin\uv.exe" pip install -e "%LOCALAPPDATA%\hermes\hermes-agent" --python "%VENV%\Scripts\python.exe"
if errorlevel 1 (
    echo FAILED - dependency repair did not complete
    pause
    exit /b 1
)

echo Done. Try 'hermes --version' now.
pause
exit /b 0
