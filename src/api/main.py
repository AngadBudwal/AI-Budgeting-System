"""FastAPI backend for Nsight AI Budgeting System dashboard."""

from fastapi import FastAPI, HTTPException, Query, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
from typing import List, Dict, Optional, Union
from datetime import datetime, date
from pathlib import Path
import json
import logging
import tempfile
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from ..services.data_processor import DataProcessor
    from ..database import init_db
    from ..ml.expense_classifier import ExpenseClassifier
    from ..ml.budget_forecaster import BudgetForecaster
    from ..ml.anomaly_detector import AnomalyDetector
except ImportError:
    # For standalone execution
    import sys
    sys.path.append('.')
    from src.services.data_processor import DataProcessor
    from src.database import init_db
    from src.ml.expense_classifier import ExpenseClassifier
    from src.ml.budget_forecaster import BudgetForecaster
    from src.ml.anomaly_detector import AnomalyDetector

# Pydantic models for API requests/responses
class ExpenseCreate(BaseModel):
    date: str
    amount: float
    currency: str = "USD"
    vendor: str
    description: str = ""
    department: str
    category: Optional[str] = None

class BudgetCreate(BaseModel):
    department: str
    category: str
    period_start: str
    period_end: str
    allocated_amount: float
    currency: str = "USD"

class PredictionRequest(BaseModel):
    vendor: str
    description: str = ""

class ForecastRequest(BaseModel):
    months: int = 6
    confidence_level: float = 0.95

class AnomalyRequest(BaseModel):
    threshold: float = 0.6
    save_report: bool = False

class ExpenseResponse(BaseModel):
    id: int
    date: str
    amount: float
    vendor: str
    description: str
    department: str
    category: str
    created_at: str

class BudgetResponse(BaseModel):
    id: int
    department: str
    category: str
    period_start: str
    period_end: str
    allocated_amount: float
    created_at: str

class DashboardStats(BaseModel):
    total_expenses: int
    total_spent: float
    total_budgets: int
    total_allocated: float
    anomaly_rate: float
    recent_expenses: List[Dict]

# FastAPI app initialization
app = FastAPI(
    title="Nsight AI Budgeting System API",
    description="RESTful API for AI-powered budgeting, forecasting, and anomaly detection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global dependencies
def get_data_processor():
    """Get data processor instance."""
    try:
        return DataProcessor()
    except Exception as e:
        logger.error(f"Failed to initialize data processor: {e}")
        raise HTTPException(status_code=500, detail="Data processor initialization failed")

def get_expense_classifier():
    """Get ML expense classifier instance."""
    try:
        classifier = ExpenseClassifier()
        classifier.load_model()  # Load pre-trained model
        return classifier
    except Exception as e:
        logger.error(f"Failed to initialize ML classifier: {e}")
        # Return None if model not available, endpoints will handle gracefully
        return None

def get_budget_forecaster():
    """Get budget forecaster instance."""
    try:
        return BudgetForecaster()
    except Exception as e:
        logger.error(f"Failed to initialize budget forecaster: {e}")
        raise HTTPException(status_code=500, detail="Budget forecaster initialization failed")

def get_anomaly_detector():
    """Get anomaly detector instance."""
    try:
        return AnomalyDetector()
    except Exception as e:
        logger.error(f"Failed to initialize anomaly detector: {e}")
        raise HTTPException(status_code=500, detail="Anomaly detector initialization failed")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Nsight AI Budgeting System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Dashboard statistics endpoint
@app.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(processor: DataProcessor = Depends(get_data_processor)):
    """Get dashboard statistics and overview data."""
    try:
        summary = processor.get_data_summary()
        
        if "error" in summary:
            raise HTTPException(status_code=500, detail=summary["error"])
        
        # Get recent anomaly rate
        anomaly_rate = 0.0
        try:
            detector = get_anomaly_detector()
            if detector.load_historical_data("data/expenses.csv"):
                detector.train_anomaly_models()
                results = detector.detect_anomalies()
                anomaly_rate = results.get('anomaly_rate', 0.0)
        except Exception:
            logger.warning("Could not calculate anomaly rate for dashboard")
        
        return DashboardStats(
            total_expenses=summary['total_expenses'],
            total_spent=summary['total_spent'],
            total_budgets=summary['total_budgets'],
            total_allocated=summary['total_allocated'],
            anomaly_rate=anomaly_rate,
            recent_expenses=summary.get('recent_expenses', [])
        )
    
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Expense endpoints
@app.get("/expenses")
async def get_expenses(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    department: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    processor: DataProcessor = Depends(get_data_processor)
):
    """Get expenses with optional filtering."""
    try:
        # Build filters
        filters = {}
        if department:
            filters['department'] = department
        if category:
            filters['category'] = category
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date
        
        expenses = processor.get_expenses(limit=limit, offset=offset, filters=filters)
        return {"expenses": expenses, "total": len(expenses)}
    
    except Exception as e:
        logger.error(f"Get expenses error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/expenses")
async def create_expense(
    expense: ExpenseCreate,
    processor: DataProcessor = Depends(get_data_processor)
):
    """Create a new expense record."""
    try:
        # Auto-categorize if no category provided
        if not expense.category:
            classifier = get_expense_classifier()
            if classifier:
                predicted_category, confidence = classifier.predict_category(expense.vendor, expense.description)
                expense.category = predicted_category
        
        # Create expense
        result = processor.add_expense(
            date=expense.date,
            amount=expense.amount,
            vendor=expense.vendor,
            description=expense.description,
            department=expense.department,
            category=expense.category or 'Other',
            currency=expense.currency
        )
        
        if result.get('success'):
            return {"message": "Expense created successfully", "id": result.get('id')}
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to create expense'))
    
    except Exception as e:
        logger.error(f"Create expense error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Budget endpoints
@app.get("/budgets")
async def get_budgets(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    department: Optional[str] = None,
    category: Optional[str] = None,
    processor: DataProcessor = Depends(get_data_processor)
):
    """Get budgets with optional filtering."""
    try:
        filters = {}
        if department:
            filters['department'] = department
        if category:
            filters['category'] = category
        
        budgets = processor.get_budgets(limit=limit, offset=offset, filters=filters)
        return {"budgets": budgets, "total": len(budgets)}
    
    except Exception as e:
        logger.error(f"Get budgets error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/budgets")
async def create_budget(
    budget: BudgetCreate,
    processor: DataProcessor = Depends(get_data_processor)
):
    """Create a new budget record."""
    try:
        result = processor.add_budget(
            department=budget.department,
            category=budget.category,
            period_start=budget.period_start,
            period_end=budget.period_end,
            allocated_amount=budget.allocated_amount,
            currency=budget.currency
        )
        
        if result.get('success'):
            return {"message": "Budget created successfully", "id": result.get('id')}
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to create budget'))
    
    except Exception as e:
        logger.error(f"Create budget error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# CSV Import endpoints
@app.post("/budgets/import")
async def import_budgets_csv(
    file: UploadFile = File(...),
    default_currency: str = "USD",
    processor: DataProcessor = Depends(get_data_processor)
):
    """Import budgets from CSV file."""
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process the CSV file
            result = processor.process_budget_csv(Path(temp_file_path))
            
            return {
                "success": result.success,
                "message": result.message,
                "records_processed": result.records_processed,
                "errors": result.errors[:10] if result.errors else []  # Limit errors shown
            }
        
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    except Exception as e:
        logger.error(f"Budget CSV import error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/expenses/import")
async def import_expenses_csv(
    file: UploadFile = File(...),
    default_currency: str = "USD",
    processor: DataProcessor = Depends(get_data_processor)
):
    """Import expenses from CSV file."""
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process the CSV file
            result = processor.process_expense_csv(Path(temp_file_path))
            
            return {
                "success": result.success,
                "message": result.message,
                "records_processed": result.records_processed,
                "errors": result.errors[:10] if result.errors else []  # Limit errors shown
            }
        
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    except Exception as e:
        logger.error(f"Expense CSV import error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ML Classification endpoints
@app.post("/ml/predict")
async def predict_expense_category(request: PredictionRequest):
    """Predict expense category using ML classifier."""
    try:
        classifier = get_expense_classifier()
        if not classifier:
            raise HTTPException(status_code=503, detail="ML classifier not available")
        
        # predict_category returns a tuple (category, confidence)
        predicted_category, confidence = classifier.predict_category(request.vendor, request.description)
        return {
            "vendor": request.vendor,
            "description": request.description,
            "predicted_category": predicted_category,
            "confidence": confidence,
            "model_info": getattr(classifier, 'best_model_name', 'rule_based') if hasattr(classifier, 'best_model_name') else 'rule_based'
        }
    
    except Exception as e:
        logger.error(f"ML prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ml/info")
async def get_ml_model_info():
    """Get ML model information and performance metrics."""
    try:
        classifier = get_expense_classifier()
        if not classifier:
            return {"status": "ML classifier not available"}
        
        info = classifier.get_model_info()
        
        # Add additional formatting for the dashboard
        if info.get('status') == 'trained' and 'model_metrics' in info:
            metrics = info.get('model_metrics', {})
            info.update({
                'accuracy': metrics.get('test_accuracy', 0),
                'training_samples': metrics.get('training_samples', 0),
                'categories_count': len(info.get('categories', []))
            })
        elif info.get('status') == 'not_trained':
            info.update({
                'accuracy': 0,
                'training_samples': 0,
                'categories_count': 0
            })
        
        return info
    
    except Exception as e:
        logger.error(f"ML info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Budget Forecasting endpoints
@app.post("/forecast/spending")
async def forecast_spending(
    request: ForecastRequest,
    data_file: str = Query("data/expenses.csv"),
    forecaster: BudgetForecaster = Depends(get_budget_forecaster)
):
    """Generate spending forecasts for future months."""
    try:
        if not Path(data_file).exists():
            raise HTTPException(status_code=404, detail=f"Data file not found: {data_file}")
        
        # Load data and generate forecast
        if not forecaster.load_historical_data(data_file):
            raise HTTPException(status_code=400, detail="Failed to load historical data")
        
        # Analyze patterns first if not trained
        if not forecaster.is_trained:
            forecaster.analyze_spending_patterns()
        
        forecast = forecaster.forecast_spending(months_ahead=request.months)
        
        if 'error' in forecast:
            raise HTTPException(status_code=400, detail=forecast['error'])
        
        return forecast
    
    except Exception as e:
        logger.error(f"Forecast error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/forecast/trends")
async def analyze_spending_trends(
    data_file: str = Query("data/expenses.csv"),
    forecaster: BudgetForecaster = Depends(get_budget_forecaster)
):
    """Analyze historical spending trends."""
    try:
        if not Path(data_file).exists():
            raise HTTPException(status_code=404, detail=f"Data file not found: {data_file}")
        
        # Load data and analyze trends
        if not forecaster.load_historical_data(data_file):
            raise HTTPException(status_code=400, detail="Failed to load historical data")
        
        trends = forecaster.analyze_spending_trends()
        
        if 'error' in trends:
            raise HTTPException(status_code=400, detail=trends['error'])
        
        return trends
    
    except Exception as e:
        logger.error(f"Trends analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/forecast/variance")
async def budget_variance_analysis(
    expenses_file: str = Query("data/expenses.csv"),
    budgets_file: str = Query("data/budgets.csv"),
    forecaster: BudgetForecaster = Depends(get_budget_forecaster)
):
    """Analyze budget vs actual spending variance."""
    try:
        if not Path(expenses_file).exists():
            raise HTTPException(status_code=404, detail=f"Expenses file not found: {expenses_file}")
        
        # Load data and analyze variance
        if not forecaster.load_historical_data(expenses_file):
            raise HTTPException(status_code=400, detail="Failed to load expenses data")
        
        variance = forecaster.analyze_budget_variance(budgets_file)
        
        if 'error' in variance:
            raise HTTPException(status_code=400, detail=variance['error'])
        
        return variance
    
    except Exception as e:
        logger.error(f"Variance analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Anomaly Detection endpoints
@app.post("/anomalies/detect")
async def detect_anomalies(
    request: AnomalyRequest,
    data_file: str = Query("data/expenses.csv"),
    detector: AnomalyDetector = Depends(get_anomaly_detector)
):
    """Detect anomalies in expense data."""
    try:
        if not Path(data_file).exists():
            raise HTTPException(status_code=404, detail=f"Data file not found: {data_file}")
        
        # Set custom threshold
        detector.anomaly_threshold = request.threshold
        
        # Load data and train models
        if not detector.load_historical_data(data_file):
            raise HTTPException(status_code=400, detail="Failed to load historical data")
        
        training_results = detector.train_anomaly_models()
        if 'error' in training_results:
            raise HTTPException(status_code=400, detail=training_results['error'])
        
        # Detect anomalies
        anomaly_results = detector.detect_anomalies()
        if 'error' in anomaly_results:
            raise HTTPException(status_code=400, detail=anomaly_results['error'])
        
        # Save report if requested
        if request.save_report:
            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)
            report_file = f"reports/api_anomaly_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            detector.export_anomaly_report(anomaly_results, report_file)
            anomaly_results['report_file'] = report_file
        
        return anomaly_results
    
    except Exception as e:
        logger.error(f"Anomaly detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/anomalies/summary")
async def get_anomaly_summary(
    data_file: str = Query("data/expenses.csv"),
    threshold: float = Query(0.6, ge=0.1, le=1.0),
    detector: AnomalyDetector = Depends(get_anomaly_detector)
):
    """Get anomaly detection summary and insights."""
    try:
        if not Path(data_file).exists():
            raise HTTPException(status_code=404, detail=f"Data file not found: {data_file}")
        
        detector.anomaly_threshold = threshold
        
        # Quick training and detection
        if not detector.load_historical_data(data_file):
            raise HTTPException(status_code=400, detail="Failed to load data")
        
        detector.train_anomaly_models()
        results = detector.detect_anomalies()
        summary = detector.get_anomaly_summary(results)
        
        if 'error' in summary:
            raise HTTPException(status_code=400, detail=summary['error'])
        
        return summary
    
    except Exception as e:
        logger.error(f"Anomaly summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Dashboard-specific endpoints for charts and visualizations
@app.get("/dashboard/spending-by-department")
async def get_spending_by_department(
    months: int = Query(12, ge=1, le=24),
    processor: DataProcessor = Depends(get_data_processor)
):
    """Get spending breakdown by department for dashboard charts."""
    try:
        data = processor.get_spending_by_department(months=months)
        return {"data": data, "months": months}
    
    except Exception as e:
        logger.error(f"Department spending error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/spending-by-category")
async def get_spending_by_category(
    months: int = Query(12, ge=1, le=24),
    processor: DataProcessor = Depends(get_data_processor)
):
    """Get spending breakdown by category for dashboard charts."""
    try:
        data = processor.get_spending_by_category(months=months)
        return {"data": data, "months": months}
    
    except Exception as e:
        logger.error(f"Category spending error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/monthly-trends")
async def get_monthly_spending_trends(
    months: int = Query(12, ge=1, le=24),
    processor: DataProcessor = Depends(get_data_processor)
):
    """Get monthly spending trends for dashboard time series charts."""
    try:
        data = processor.get_monthly_trends(months=months)
        return {"data": data, "months": months}
    
    except Exception as e:
        logger.error(f"Monthly trends error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/recent-alerts")
async def get_recent_alerts(
    limit: int = Query(10, ge=1, le=50),
    detector: AnomalyDetector = Depends(get_anomaly_detector)
):
    """Get recent anomaly alerts for dashboard notifications."""
    try:
        # Quick anomaly check
        if detector.load_historical_data("data/expenses.csv"):
            detector.train_anomaly_models()
            results = detector.detect_anomalies()
            
            anomalies = results.get('anomalies', [])
            recent_alerts = anomalies[:limit]
            
            return {
                "alerts": recent_alerts,
                "total_anomalies": len(anomalies),
                "anomaly_rate": results.get('anomaly_rate', 0)
            }
        else:
            return {"alerts": [], "total_anomalies": 0, "anomaly_rate": 0}
    
    except Exception as e:
        logger.error(f"Recent alerts error: {e}")
        return {"alerts": [], "total_anomalies": 0, "anomaly_rate": 0}

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup."""
    try:
        init_db()
        logger.info("Database initialized successfully")
        logger.info("Nsight AI Budgeting API started successfully")
    except Exception as e:
        logger.error(f"Startup error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 