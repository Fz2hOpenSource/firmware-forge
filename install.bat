@echo off
rem ==================================================================
rem  Embedded Workbench one-click installer (double-click friendly).
rem  Wraps install.ps1 - no command-line knowledge required.
rem  Keep this .bat next to install.ps1 in the repository root.
rem  Advanced: run "install.bat -Symlink" from a terminal for dev mode.
rem ==================================================================
setlocal

set "SCRIPT_DIR=%~dp0"
set "PS_SCRIPT=%SCRIPT_DIR%install.ps1"

if not exist "%PS_SCRIPT%" (
    echo [ERROR] install.ps1 was not found next to this file.
    echo Keep install.bat and install.ps1 together in the repository root.
    echo.
    pause
    exit /b 1
)

echo Installing the Embedded Workbench into DSH ...
echo Source: %SCRIPT_DIR%
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%" %*
set "RC=%errorlevel%"

echo.
if "%RC%"=="0" (
    echo [OK] Install finished.
    echo Next step: open DSH, create a new session, and pick the
    echo "Embedded Workbench" preset from the preset menu.
) else (
    echo [FAILED] Installer exited with code %RC%. Read the messages above.
)
echo.
pause
exit /b %RC%
