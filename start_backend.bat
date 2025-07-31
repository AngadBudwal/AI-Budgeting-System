@echo off
echo Starting Nsight AI Budgeting System Backend...
echo.

REM Activate virtual environment
if exist "Scripts\activate.bat" (
    echo Activating virtual environment...
    call Scripts\activate.bat
) else (
    echo Virtual environment not found. Using system Python...
)

REM Start the FastAPI backend
echo Starting FastAPI server on http://localhost:8000
echo.
python src/api/main.py

pause 