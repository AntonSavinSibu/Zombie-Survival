@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo   ZOMBIE SURVIVAL - WINDOWS BUILD
echo   DLL-SAFE PYGAME BUILD
echo ==========================================
echo.

where py >nul 2>&1
if %errorlevel%==0 (set "PY=py") else (set "PY=python")

%PY% --version
if errorlevel 1 (
    echo Python was not found.
    pause
    exit /b 1
)

echo Installing pygame and PyInstaller...
%PY% -m pip install --upgrade pip
%PY% -m pip install --upgrade pygame pyinstaller
if errorlevel 1 (
    echo Package installation failed.
    pause
    exit /b 1
)

echo Cleaning old builds...
if exist build rmdir /s /q build
if exist "dist\Zombie Survival" rmdir /s /q "dist\Zombie Survival"

echo Building DLL-safe folder version...
%PY% -m PyInstaller --clean --noconfirm "Zombie Survival FIXED.spec"
if errorlevel 1 (
    echo.
    echo BUILD FAILED - send me a screenshot of this window.
    pause
    exit /b 1
)

echo.
echo BUILD COMPLETE!
echo Run:
echo dist\Zombie Survival\Zombie Survival.exe
echo.
echo Keep the entire "Zombie Survival" folder together.
pause
endlocal
