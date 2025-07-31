"""Data models for Nsight AI Budgeting System."""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

class CategoryEnum(str, Enum):
    """Expense categories."""
    IT_INFRASTRUCTURE = "IT Infrastructure"
    MARKETING = "Marketing"
    TRAVEL = "Travel"
    OFFICE_SUPPLIES = "Office Supplies"
    PERSONNEL = "Personnel"
    UTILITIES = "Utilities"
    PROFESSIONAL_SERVICES = "Professional Services"
    TRAINING = "Training"
    EQUIPMENT = "Equipment"
    OTHER = "Other"

class DepartmentEnum(str, Enum):
    """Company departments."""
    ENGINEERING = "Engineering"
    MARKETING = "Marketing"
    SALES = "Sales"
    HR = "HR"
    FINANCE = "Finance"
    OPERATIONS = "Operations"
    EXECUTIVE = "Executive"

class CurrencyEnum(str, Enum):
    """Currencies for Nsight operations in different regions."""
    USD = "USD"  # United States Dollar
    INR = "INR"  # Indian Rupee
    CAD = "CAD"  # Canadian Dollar
    TRY = "TRY"  # Turkish Lira

class ExpenseRecord(BaseModel):
    """Model for expense transactions."""
    id: Optional[int] = None
    date: date
    amount: float = Field(gt=0, description="Amount must be positive")
    currency: CurrencyEnum = CurrencyEnum.USD  # Default to USD
    vendor: str
    description: Optional[str] = None
    department: DepartmentEnum
    category: Optional[CategoryEnum] = None
    is_recurring: bool = False
    created_at: Optional[datetime] = None

class BudgetRecord(BaseModel):
    """Model for budget allocations."""
    id: Optional[int] = None
    department: DepartmentEnum
    category: CategoryEnum
    period_start: date
    period_end: date
    allocated_amount: float = Field(gt=0)
    currency: CurrencyEnum = CurrencyEnum.USD  # Default to USD
    spent_amount: Optional[float] = 0.0
    created_at: Optional[datetime] = None

class ForecastResult(BaseModel):
    """Model for budget forecast results."""
    department: DepartmentEnum
    category: CategoryEnum
    forecast_period: str
    predicted_amount: float
    currency: CurrencyEnum
    confidence_interval_lower: float
    confidence_interval_upper: float
    historical_average: float
    trend: str  # "increasing", "decreasing", "stable"

class AnomalyAlert(BaseModel):
    """Model for anomaly detection alerts."""
    id: Optional[int] = None
    date: date
    department: DepartmentEnum
    category: CategoryEnum
    actual_amount: float
    expected_amount: float
    currency: CurrencyEnum
    deviation_percentage: float
    severity: str  # "low", "medium", "high"
    description: str
    is_resolved: bool = False
    created_at: Optional[datetime] = None

class DashboardSummary(BaseModel):
    """Model for dashboard summary data."""
    total_budget: float
    total_spent: float
    currency: CurrencyEnum
    budget_utilization: float
    departments_over_budget: List[str]
    top_categories: List[dict]
    recent_anomalies: List[AnomalyAlert]
    monthly_trend: List[dict]

class UploadResponse(BaseModel):
    """Response model for file uploads."""
    success: bool
    message: str
    records_processed: int
    errors: List[str] = []

# Additional models for budget CSV import
class BudgetCreate(BaseModel):
    """Model for creating new budget records via API."""
    department: DepartmentEnum
    category: CategoryEnum
    period_start: date
    period_end: date
    allocated_amount: float = Field(gt=0)
    currency: CurrencyEnum = CurrencyEnum.USD

class BudgetCSVImportRequest(BaseModel):
    """Model for budget CSV import requests."""
    default_currency: CurrencyEnum = CurrencyEnum.USD
    validate_only: bool = False
    
class ExpenseCreate(BaseModel):
    """Model for creating new expense records via API."""
    date: date
    amount: float = Field(gt=0)
    currency: CurrencyEnum = CurrencyEnum.USD
    vendor: str
    description: Optional[str] = None
    department: DepartmentEnum
    category: Optional[CategoryEnum] = None
    is_recurring: bool = False 