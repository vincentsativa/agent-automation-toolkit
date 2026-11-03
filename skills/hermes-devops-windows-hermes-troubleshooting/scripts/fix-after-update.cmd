@echo off
setlocal enabledelayedexpansion
title Hermes Post-Update Repair
echo ============================================
echo  Hermes Post-Update Repair
echo  Fixes venv + desktop build after an update
echo ============================================
echo.

set "HERMES=%LOCALAPPDATA%\hermes"
set "UV=%HERMES%\bin\uv.exe"
set "DESKTOP_EXE=%HERMES%\hermes-agent\apps\desktop\release\win-unpacked\Hermes.exe"

rem --- Resolve the LIVE python environment (PM-managed; hash changes on rebuild) ---
set "VENV="
for /f "usebackq delims=" %%P in (`powershell -NoProfile -Command "(Get-ChildItem $env:LOCALAPPDATA\hermes\installs\*\facts.json -ErrorAction SilentlyContinue | Sort-Object LastWriteTime | Select-Object -Last 1 | ForEach-Object { (Get-Content $_ -Raw | ConvertFrom-Json).packages.venv.environment })"`) do set "VENV=%%P"
set "VENV_PY=%VENV%\Scripts\python.exe"

echo [0/3] Resolving live python environment...
if not defined VENV (
    echo   FAILED - no installs\*\facts.json found under %HERMES%
    echo   Cannot locate the managed environment. Aborting.
    pause
    exit /b 1
)
echo   Found: %VENV%
echo.

echo [1/3] Checking Python dependencies...
if not exist "%VENV_PY%" (
    echo   FAILED - interpreter missing at %VENV_PY%
    echo   The recorded environment is gone. Re-run the installer or 'hermes doctor'.
    pause
    exit /b 1
)
"%VENV_PY%" -c "import fastapi,uvicorn,pydantic,openai,yaml,dotenv,rich" >nul 2>&1
if %errorlevel%==0 (
    echo   OK - dependencies healthy
) else (
    echo   BROKEN - reinstalling dependencies...
    "%UV%" pip install -e "%HERMES%\hermes-agent" --python "%VENV_PY%"
    "%VENV_PY%" -c "import fastapi,uvicorn,pydantic,openai,yaml,dotenv,rich" >nul 2>&1
    if !errorlevel!==0 (
        echo   OK - dependencies repaired
    ) else (
        echo   FAILED - could not repair dependencies
        set "FAILED=1"
    )
)
echo.

echo [2/3] Checking desktop app build...
if exist "%DESKTOP_EXE%" (
    echo   OK - desktop app present
) else (
    echo   MISSING - rebuilding desktop app...
    cd /d "%HERMES%"
    set "REBUILT="
    for /l %%A in (1,1,3) do (
        if not defined REBUILT (
            echo   attempt %%A - running build
            "%VENV_PY%" -m hermes_cli.main desktop --build-only
            if exist "%DESKTOP_EXE%" (
                set "REBUILT=1"
            ) else (
                echo   attempt %%A - build failed, repairing venv and retrying
                "%UV%" pip install -e "%HERMES%\hermes-agent" --python "%VENV_PY%"
            )
        )
    )
    if defined REBUILT (
        echo   OK - desktop app rebuilt
    ) else (
        echo   FAILED - could not rebuild desktop app
        set "FAILED=1"
    )
)
echo.

echo [3/3] Verifying CLI...
"%VENV_PY%" -c "import dotenv" >nul 2>&1
if %errorlevel%==0 (
    echo   OK - CLI imports healthy
) else (
    echo   FAILED - CLI still broken
    set "FAILED=1"
)
echo.
echo ============================================
if defined FAILED (
    echo  One or more checks FAILED. Re-run this
    echo  after closing all Hermes windows/gateways.
    echo ============================================
    pause
    exit /b 1
)
echo  Done.
echo ============================================
pause
exit /b 0
