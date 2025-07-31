# 🚀 Nsight AI Budgeting System - Setup Guide

This guide will help you set up and run the Nsight AI Budgeting System on your local machine or server.

## 📋 Prerequisites

- **Python 3.8+** (tested with Python 3.13)
- **Git** for version control
- **4GB+ RAM** recommended for ML operations
- **Windows, macOS, or Linux**

## 🛠️ Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/nsight-ai-budgeting-system.git
cd nsight-ai-budgeting-system
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database
```bash
# Create database tables
python -m src.database

# Run migration for existing databases (if upgrading)
python migrate_currency.py
```

### 5. Generate Sample Data (Optional)
```bash
# Generate synthetic data for testing
python -m src.cli generate-data --years 2023 2024
```

## 🏃‍♂️ Running the Application

### Method 1: Run Both Services
```bash
# Terminal 1: Start FastAPI Backend
python -m uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2: Start Streamlit Dashboard  
python -m streamlit run dashboard/main.py --server.port 8501 --server.address 127.0.0.1
```

### Method 2: Use the Test Script
```bash
# Check if services are running
python test_services.py
```

## 🌐 Access Points

Once both services are running:

- **📊 Dashboard**: http://localhost:8501
- **📖 API Documentation**: http://localhost:8000/docs
- **🔌 API Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
nsight-ai-budgeting-system/
├── src/                    # Core application code
│   ├── api/               # FastAPI backend
│   ├── ml/                # Machine learning modules
│   ├── services/          # Business logic
│   ├── models.py          # Data models
│   ├── database.py        # Database setup
│   └── config.py          # Configuration
├── dashboard/             # Streamlit frontend
├── data/                  # Sample data files
├── models/                # Trained ML models
├── reports/               # Generated reports
├── uploads/               # Temporary file storage
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
└── SETUP.md              # This setup guide
```

## 🌍 Multi-Currency Features

The system supports **4 currencies** for global operations:
- **USD** - US Dollar (United States)
- **INR** - Indian Rupee (India)
- **CAD** - Canadian Dollar (Canada)
- **TRY** - Turkish Lira (Turkey)

### Sample Data Import

Try importing the provided sample data:
```bash
# Import sample expenses (42 records across all currencies)
# Use the dashboard: Data Management → Import Expenses → expense_import_sample.csv

# Import sample budgets
# Use: Data Management → Import Budgets → data/sample_budgets.csv
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
# Database
DATABASE_URL=sqlite:///./budgeting_system.db

# Debug mode
DEBUG=True

# ML Model settings
ML_MODEL_PATH=./models/
FORECAST_HORIZON_DAYS=90
ANOMALY_THRESHOLD=0.3
```

### Database Configuration
By default, the system uses **SQLite** for simplicity. For production, consider:
- **PostgreSQL** for better performance
- **MySQL** for enterprise environments

## 🤖 ML Features Setup

### 1. Train Expense Classifier
```bash
python -m src.cli train-ml
```

### 2. Generate Forecasts
The system automatically generates forecasts when you:
- Access the **Forecasting** page in the dashboard
- Call the `/forecast/spending` API endpoint

### 3. Anomaly Detection
Anomaly detection runs automatically and flags unusual spending patterns.

## 🚨 Troubleshooting

### Common Issues

**1. "python-multipart" Error**
```bash
pip install python-multipart
```

**2. Port Already in Use**
```bash
# Change ports in the run commands
uvicorn src.api.main:app --port 8001
streamlit run dashboard/main.py --server.port 8502
```

**3. Database Permission Issues**
```bash
# Ensure write permissions in the project directory
chmod 755 ./
```

**4. ML Model Not Found**
```bash
# Train the ML model first
python -m src.cli train-ml
```

### Performance Tips

1. **For Large Datasets**: Consider upgrading to PostgreSQL
2. **Memory Issues**: Increase system RAM or reduce data processing batch sizes
3. **Slow Dashboard**: Use data filtering and pagination for better performance

## 🔒 Security Considerations

**For Production Deployment:**

1. **Change Default Ports**: Use reverse proxy (nginx/Apache)
2. **Add Authentication**: Implement user login system
3. **Use HTTPS**: Enable SSL/TLS encryption
4. **Environment Variables**: Never commit sensitive data to Git
5. **Database Security**: Use proper database credentials and encryption

## 📞 Support

If you encounter any issues:

1. Check the **API logs** in the terminal running uvicorn
2. Check the **Dashboard logs** in the terminal running streamlit
3. Verify all dependencies are installed: `pip list`
4. Ensure ports 8000 and 8501 are available

## 🎯 Next Steps

After successful setup:

1. **Import Your Data**: Use the CSV import features
2. **Explore Analytics**: Check the dashboard's analytics features
3. **Set Up Budgets**: Create budget allocations for your departments
4. **Train ML Models**: Generate forecasts and anomaly detection
5. **Customize**: Modify categories and departments for your organization

---

**Happy Budgeting! 💰** 