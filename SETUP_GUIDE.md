# 🚀 Nsight AI Budgeting System - Python Setup Guide

## Quick Setup (Recommended)

### Option 1: Automated Setup
```bash
# Run the automated setup script
setup_python.bat
```

### Option 2: Manual Setup

#### Step 1: Reinstall Python (if needed)
If you're getting "Could not find platform independent libraries" error:

1. **Download Python 3.11 or 3.12** from: https://www.python.org/downloads/
2. **During installation, check these boxes:**
   - ✅ "Add Python to PATH"
   - ✅ "Install pip"
   - ✅ "Install for all users" (optional)
3. **Restart your command prompt** after installation

#### Step 2: Install pip (if missing)
```bash
# Try this first
py -m ensurepip --upgrade

# If that fails, download pip manually
powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py'"
py get-pip.py
```

#### Step 3: Install Required Packages
```bash
# Essential ML packages
py -m pip install pandas scikit-learn numpy

# Full requirements (optional but recommended)
py -m pip install fastapi uvicorn streamlit sqlalchemy pydantic pydantic-settings prophet
```

#### Step 4: Test Installation
```bash
# Test basic functionality
py -c "import pandas, sklearn, numpy; print('✅ Success!')"

# Test ML core
py test_ml_core.py
```

## 🎯 Using the ML Core

Once setup is complete, you can use these commands:

### Train the ML Model
```bash
# Train using your synthetic data (1,605 expense records)
py -m src.cli train-ml data/expenses.csv --test
```

### Test Individual Predictions
```bash
# Predict expense categories
py -m src.cli predict "Microsoft Azure" "Cloud computing services"
py -m src.cli predict "Google Ads" "Marketing campaign"
py -m src.cli predict "Delta Airlines" "Business travel"
```

### View Model Performance
```bash
# See model accuracy and metrics
py -m src.cli ml-info
```

### Test the Full System
```bash
# Run comprehensive test
py test_ml_core.py
```

## 🔧 Troubleshooting

### Common Issues:

**1. "Could not find platform independent libraries"**
- Reinstall Python from python.org
- Make sure to check "Add Python to PATH"

**2. "No module named pip"**
- Run: `py -m ensurepip --upgrade`
- Or download get-pip.py manually

**3. "No module named pandas/sklearn"**
- Run: `py -m pip install pandas scikit-learn numpy`

**4. "Permission denied" errors**
- Run command prompt as Administrator
- Or add `--user` flag: `py -m pip install --user pandas`

### Alternative Installation Methods:

**Using Anaconda (Recommended for ML work):**
```bash
# Download Anaconda from: https://www.anaconda.com/download
# Then in Anaconda Prompt:
conda install pandas scikit-learn numpy fastapi streamlit
```

**Using Virtual Environment:**
```bash
py -m venv venv
venv\Scripts\activate
py -m pip install -r requirements.txt
```

## 📊 Expected Results

After successful setup:

### Training Output:
```
🤖 Starting ML model training...
📚 Loading training data from data/expenses.csv
✅ Data loaded: 1605 samples, 9 categories
🏋️ Training ML models...
✅ Training completed! Model performance:
  • random_forest: CV: 0.923 (±0.015), Test: 0.918
  • logistic_regression: CV: 0.887 (±0.021), Test: 0.891
  • naive_bayes: CV: 0.845 (±0.019), Test: 0.851
🏆 Best model: random_forest
🎯 Final accuracy: 0.918
```

### Prediction Examples:
```
🔍 Sample predictions:
   1. Microsoft Azure - Cloud computing services
      → Predicted: IT Infrastructure (confidence: 0.95)
   2. Google Ads - Online advertising campaign  
      → Predicted: Marketing (confidence: 0.92)
   3. Delta Airlines - Business trip to conference
      → Predicted: Travel (confidence: 0.89)
```

## 🎉 Next Steps

Once Python is working:
1. **Train your model**: `py -m src.cli train-ml data/expenses.csv --test`
2. **Ready for forecasting**: Budget prediction models
3. **Ready for dashboard**: Streamlit web interface

Your ML core is fully built and ready to go! 🚀 