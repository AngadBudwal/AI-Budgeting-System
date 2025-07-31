@echo off
echo ========================================
echo   Nsight AI Budgeting System Launcher
echo ========================================
echo.

REM Check if virtual environment exists
if exist "Scripts\activate.bat" (
    echo ✓ Virtual environment found
) else (
    echo ⚠ Warning: Virtual environment not found at Scripts\activate.bat
    echo   Make sure Python and dependencies are installed
    echo.
)

echo Starting backend and frontend services...
echo.

REM Start backend in new window
echo ► Starting Backend (FastAPI)...
start "Nsight AI Backend" cmd /k start_backend.bat

REM Wait a moment before starting frontend
timeout /t 2 /nobreak > nul

REM Start frontend in new window  
echo ► Starting Frontend (Streamlit)...
start "Nsight AI Frontend" cmd /k start_frontend.bat

echo.
echo ========================================
echo Services are starting in separate windows:
echo   • Backend:  http://localhost:8000
echo   • Frontend: http://localhost:8501
echo ========================================
echo.
echo Press any key to exit this launcher...
pause > nul 