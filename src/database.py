"""Database setup and models for Nsight AI Budgeting System."""

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

try:
    from .config import settings
except ImportError:
    # For standalone execution
    from config import settings

# Database setup
engine = create_engine(settings.database_url, echo=settings.debug)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class ExpenseDB(Base):
    """SQLAlchemy model for expenses."""
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="USD", index=True)  # ISO currency code
    vendor = Column(String(255), nullable=False)
    description = Column(Text)
    department = Column(String(50), nullable=False, index=True)
    category = Column(String(50), index=True)
    is_recurring = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class BudgetDB(Base):
    """SQLAlchemy model for budgets."""
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    department = Column(String(50), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    allocated_amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="USD", index=True)  # ISO currency code
    spent_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class AnomalyDB(Base):
    """SQLAlchemy model for anomaly alerts."""
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    department = Column(String(50), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    actual_amount = Column(Float, nullable=False)
    expected_amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="USD", index=True)  # ISO currency code
    deviation_percentage = Column(Float, nullable=False)
    severity = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database with tables."""
    create_tables()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db() 