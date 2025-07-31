@echo off
echo Starting Nsight AI Budgeting System Frontend...
echo.

REM Activate virtual environment
if exist "Scripts\activate.bat" (
    echo Activating virtual environment...
    call Scripts\activate.bat
) else (
    echo Virtual environment not found. Using system Python...
)

REM Wait a moment for backend to start
echo Waiting for backend to initialize...
timeout /t 3 /nobreak > nul

REM Start the Streamlit frontend
echo Starting Streamlit dashboard on http://localhost:8501
echo.
streamlit run dashboard/main.py --server.port 8501 --server.address localhost

pause 