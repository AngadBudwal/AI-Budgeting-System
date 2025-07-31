# Nsight AI Budgeting System

An intelligent budgeting and expense management system powered by AI/ML for predictive analytics, anomaly detection, and automated categorization with **multi-currency support** for global operations.

## Features

### Core Features (MVP)
- **Multi-Currency Support**: Handle USD, INR, CAD, TRY for global Nsight operations
- **Budget Forecasting**: Predict future spending using machine learning
- **Expense Tracking & Auto-Categorization**: Automatically categorize expenses by vendor and description
- **Anomaly Detection**: Flag unusual spending patterns and potential budget overruns
- **Interactive Dashboard**: Real-time insights with charts and alerts
- **CSV Import/Export**: Easy data import and reporting capabilities with currency support

### Global Operations Support
- **USD**: United States operations
- **INR**: India operations  
- **CAD**: Canada operations
- **TRY**: Turkey operations
- **Currency-aware reporting**: Separate tracking and analysis by currency
- **Flexible CSV imports**: Support currency columns or default currency assignment

### AI/ML Capabilities
- **Predictive Analytics**: Linear Regression and Prophet for time series forecasting
- **Anomaly Detection**: Isolation Forest for outlier detection
- **Smart Categorization**: Text classification for automatic expense categorization
- **Trend Analysis**: Historical pattern recognition and future projections

## Architecture

```
[ Data Ingestion (CSV/API) ]
        ↓
[ Preprocessing & Storage (Pandas + SQLite) ]
        ↓
[ ML Modules ]
   - Forecasting
   - Anomaly Detection
   - Categorization
        ↓
[ Dashboard (Streamlit/FastAPI) ]
   - Graphs & Visualizations
   - Alerts & Notifications
   - Budget vs Actual Reports
```

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: scikit-learn, Prophet
- **Frontend**: Streamlit
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Development**: Python 3.8+, Pydantic, pytest

## Quick Start

### 1. Installation
```bash
# Clone the repository
git clone <repository-url>
cd budgeting-system

# Install dependencies
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
# Create database tables
python -m src.database

# For existing databases, run migration to add currency support
python migrate_currency.py
```

### 3. Run the Application
```bash
# Start FastAPI backend
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

# Start Streamlit dashboard (in another terminal)
streamlit run dashboard/main.py
```

### 4. Access the System
- **API Documentation**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8501

## Data Structure

### Expense Records
```json
{
  "date": "2024-01-15",
  "amount": 1250.00,
  "currency": "USD",
  "vendor": "AWS",
  "description": "Cloud infrastructure costs",
  "department": "Engineering",
  "category": "IT Infrastructure"
}
```

### Budget Allocations
```json
{
  "department": "Marketing",
  "category": "Marketing",
  "period_start": "2024-01-01",
  "period_end": "2024-01-31",
  "allocated_amount": 25000.00,
  "currency": "USD"
}
```

### CSV Import Formats

#### Expenses CSV
```csv
date,amount,currency,vendor,description,department,category
2024-01-15,150.00,USD,Microsoft Azure,Cloud hosting,Engineering,IT Infrastructure
2024-01-16,25000.00,INR,Google Ads,Marketing campaign India,Marketing,Marketing
2024-01-17,2500.00,CAD,Air Canada,Business travel,Executive,Travel
```

#### Budgets CSV
```csv
department,category,period_start,period_end,allocated_amount,currency
Engineering,IT Infrastructure,2024-02-01,2024-02-29,50000.00,USD
Marketing,Marketing,2024-02-01,2024-02-29,1800000.00,INR
Sales,Travel,2024-02-01,2024-02-29,8000.00,CAD
```

## Dashboard Features

### Budget Overview
- Total budget vs actual spending with currency display
- Department-wise breakdown by currency
- Category distribution across regions
- Monthly trends and patterns

### Alerts & Anomalies
- Real-time spending alerts
- Budget overrun warnings
- Unusual transaction detection
- Severity-based notifications

### Forecasting
- Next month/quarter predictions
- Confidence intervals
- Historical trend analysis
- Department-specific forecasts

### Data Management
- **Add Expenses**: Manual entry with currency selection
- **Add Budgets**: Budget allocation with multi-currency support
- **CSV Import**: Bulk upload expenses and budgets
- **Currency Support**: Automatic validation and conversion handling

### CSV Import Features
- **Drag & Drop**: Easy file upload interface
- **Currency Detection**: Automatic currency column recognition
- **Default Currency**: Set fallback currency for records without currency specified
- **Error Reporting**: Detailed validation errors with line numbers
- **Sample Files**: Download template CSV files for proper formatting
- **Bulk Processing**: Handle thousands of records efficiently

## Development Timeline

### Week 1: Foundation
- [x] Project structure and configuration
- [x] Database models and setup
- [x] Core data models
- [ ] CSV upload functionality
- [ ] Synthetic data generation

### Week 2: ML Core
- [ ] Expense categorization model
- [ ] Budget forecasting implementation
- [ ] Anomaly detection system
- [ ] Model training pipeline

### Week 3: Dashboard
- [ ] FastAPI backend endpoints
- [ ] Streamlit frontend
- [ ] Data visualization components
- [ ] Real-time alerts system

### Week 4: Demo & Polish
- [ ] Demo preparation
- [ ] Performance optimization
- [ ] User documentation
- [ ] Stakeholder presentation

## Configuration

Key settings in `src/config.py`:
- Database connection
- ML model parameters
- Forecast horizon (default: 90 days)
- Anomaly threshold (default: 30%)
- Expense categories

## Project Structure

```
Budgeting System/
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   ├── models.py          # Pydantic data models
│   ├── database.py        # SQLAlchemy setup
│   ├── main.py           # FastAPI application
│   ├── ml/               # ML modules
│   ├── services/         # Business logic
│   └── utils/            # Utility functions
├── dashboard/            # Streamlit dashboard
├── data/                # Data storage
├── models/              # Trained ML models
├── uploads/             # File uploads
├── tests/               # Test suite
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## Value Proposition for Nsight

1. **Predictive Cash Flow**: Accurate budget forecasting for better financial planning
2. **Early Warning System**: Detect overspending before it impacts operations
3. **Automation**: Reduce manual effort in expense categorization
4. **Executive Insights**: Clear dashboards for leadership decision-making
5. **Cost Savings**: Identify spending patterns and optimization opportunities

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

---

**Built for intelligent budget management** 