@echo off
echo ========================================
echo   Nsight AI Budgeting System Setup
echo ========================================
echo.

echo Step 1: Checking Python installation...
py --version
if errorlevel 1 (
    echo ❌ Python launcher not found!
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found!
echo.

echo Step 2: Installing pip...
py -m ensurepip --upgrade
if errorlevel 1 (
    echo ⚠️  ensurepip failed, trying alternative method...
    echo Downloading pip installer...
    powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py'"
    py get-pip.py
    del get-pip.py
)

echo.
echo Step 3: Upgrading pip...
py -m pip install --upgrade pip

echo.
echo Step 4: Installing required packages for Nsight AI...
echo Installing: pandas, scikit-learn, numpy, fastapi, streamlit...

py -m pip install pandas
py -m pip install scikit-learn
py -m pip install numpy
py -m pip install fastapi
py -m pip install uvicorn
py -m pip install streamlit
py -m pip install sqlalchemy
py -m pip install pydantic
py -m pip install pydantic-settings
py -m pip install prophet

echo.
echo ========================================
echo   Setup Complete! 🎉
echo ========================================
echo.
echo Testing the installation...
py -c "import pandas, sklearn, numpy; print('✅ All packages installed successfully!')"

echo.
echo Next steps:
echo 1. Run: py -m src.cli train-ml data/expenses.csv --test
echo 2. Run: py -m src.cli predict "Microsoft Azure" "Cloud services"
echo 3. Run: py -m src.cli ml-info
echo.
pause 