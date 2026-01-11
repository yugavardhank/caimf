@echo off
REM CAIMF Quick Deployment Script for Windows
REM Supports: Docker, Local

setlocal enabledelayedexpansion

cls
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║           CAIMF Quick Deployment Script ^(Windows^)                  ║
echo ║           Child Aadhaar Inclusion Monitoring Framework             ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

:menu
echo Choose deployment method:
echo.
echo   1. Docker Compose ^(Recommended^)
echo   2. Local Development
echo   3. View Deployment Guide
echo   4. Exit
echo.

set /p choice="Enter choice [1-4]: "

if "%choice%"=="1" goto docker_deploy
if "%choice%"=="2" goto local_deploy
if "%choice%"=="3" goto view_guide
if "%choice%"=="4" goto exit_script
echo Invalid choice. Please try again.
goto menu

:docker_deploy
cls
echo.
echo Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ✗ Docker is not installed or not in PATH
    echo   Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    echo.
    pause
    goto menu
)

echo ✓ Docker found
echo.

echo [1/4] Building Docker images...
docker-compose build
if %errorlevel% neq 0 goto error

echo.
echo [2/4] Starting services...
docker-compose up -d
if %errorlevel% neq 0 goto error

echo.
echo [3/4] Waiting for services to start...
timeout /t 5 /nobreak

echo.
echo [4/4] Verifying deployment...
docker-compose ps

echo.
echo ✅ Deployment complete!
echo.
echo Access your services:
echo   📊 Dashboard: http://localhost:8501
echo   📡 API: http://localhost:8000
echo   📖 API Docs: http://localhost:8000/docs
echo.
echo View logs:
echo   docker-compose logs -f caimf-api
echo   docker-compose logs -f caimf-dashboard
echo.
echo Stop services:
echo   docker-compose down
echo.
pause
goto menu

:local_deploy
cls
echo.
echo [1/3] Checking virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [2/3] Installing dependencies...
pip install -q -r requirements.txt

echo.
echo [3/3] Setup complete!
echo.
echo Terminal 1 - API Server:
echo   python -m uvicorn caimf.api:app --reload --host 0.0.0.0 --port 8000
echo.
echo Terminal 2 - Dashboard ^(separate terminal^):
echo   python -m streamlit run caimf/dashboard.py
echo.
echo Or run the full pipeline:
echo   python auto_load.py
echo.
pause
goto menu

:view_guide
cls
echo Deployment guide not implemented in batch script
echo Please view DEPLOYMENT.md in your editor
echo.
pause
goto menu

:error
echo.
echo ✗ Error occurred during deployment
echo.
pause
goto menu

:exit_script
echo Exiting...
endlocal
exit /b 0
