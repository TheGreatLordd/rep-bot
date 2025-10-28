@echo off
title RepBot - Starting...
cd /d %~dp0
echo.


if not exist ".venv\Scripts\python.exe" (
    echo [!] Virtual environment not found. Creating...
    python -m venv .venv
    echo [+] Virtual environment created successfully!
    echo.
)

echo [*] Activating virtual environment...
call ".venv\Scripts\activate.bat"
if %ERRORLEVEL% neq 0 (
    echo [!] Failed to activate virtual environment
    echo [*] Installing dependencies with system Python instead...
)
echo [*] Checking dependencies...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt
echo [+] Dependencies ready!
echo.

if not exist ".env" (
    echo [!] WARNING: .env file not found!
    echo [!] Please create a .env file with your bot token.
    echo.
    pause
    exit /b 1
)

echo [*] Starting RepBot...
echo.
title RepBot - Running
python main.py


echo.
if %ERRORLEVEL% neq 0 (
    echo [!] Bot crashed with error code: %ERRORLEVEL%
    title RepBot - Error
) else (
    echo [+] Bot stopped gracefully
    title RepBot - Stopped
)

echo.
pause