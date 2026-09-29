@echo off
REM ============================================================
REM  RecallOps - one-click demo launcher
REM  Starts FastAPI backend (8000) + Django frontend (8001)
REM ============================================================
title RecallOps Demo
cd /d "%~dp0"

echo [1/3] Checking .env...
if not exist ".env" (
    echo ERROR: .env not found. Copy .env.example to .env and add your keys.
    pause
    exit /b 1
)

set PYTHON_EXE=%~dp0venv\Scripts\python.exe
if not exist "%PYTHON_EXE%" (
    set PYTHON_EXE=python
)

echo [2/3] Starting FastAPI backend on port 8000...
start "RecallOps Backend" cmd /k "cd /d "%~dp0" && "%PYTHON_EXE%" -m uvicorn Backend.main:app --host 127.0.0.1 --port 8000"

echo [3/3] Starting Django frontend on port 8001...
start "RecallOps Frontend" cmd /k "cd /d "%~dp0app" && "%PYTHON_EXE%" manage.py runserver 127.0.0.1:8001"

timeout /t 5 /nobreak >nul
start http://127.0.0.1:8001

echo.
echo RecallOps is running:
echo   Frontend:  http://127.0.0.1:8001
echo   Backend:   http://127.0.0.1:8000/docs
echo.
echo Close the two server windows to stop.
pause

