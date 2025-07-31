"""Configuration settings for Nsight AI Budgeting System."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "sqlite:///./budgeting_system.db"
    
    # API Settings
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    debug: bool = True
    
    # Data Paths
    data_dir: Path = Path("data")
    uploads_dir: Path = Path("uploads")
    models_dir: Path = Path("models")
    
    # ML Model Settings
    forecast_horizon_days: int = 90  # 3 months
    anomaly_threshold: float = 0.3  # 30% above normal
    min_training_samples: int = 30
    
    # Categories for expense classification
    default_categories: list = [
        "IT Infrastructure",
        "Marketing",
        "Travel",
        "Office Supplies", 
        "Personnel",
        "Utilities",
        "Professional Services",
        "Training",
        "Equipment",
        "Other"
    ]
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()

# Ensure directories exist
settings.data_dir.mkdir(exist_ok=True)
settings.uploads_dir.mkdir(exist_ok=True)
settings.models_dir.mkdir(exist_ok=True) 