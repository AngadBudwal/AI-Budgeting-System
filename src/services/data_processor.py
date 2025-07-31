"""Data processing service for CSV ingestion and validation."""

import csv
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import re
from sqlalchemy.orm import Session

try:
    from ..database import SessionLocal, ExpenseDB, BudgetDB
    from ..models import ExpenseRecord, BudgetRecord, UploadResponse, DepartmentEnum, CategoryEnum
    from ..config import settings
except ImportError:
    # For standalone execution
    from database import SessionLocal, ExpenseDB, BudgetDB
    from models import ExpenseRecord, BudgetRecord, UploadResponse, DepartmentEnum, CategoryEnum
    from config import settings

class DataProcessor:
    """Handles CSV data ingestion, validation, and database operations."""
    
    def __init__(self):
        self.db = SessionLocal()
        self.errors = []
        self.warnings = []
        
        # Expected CSV columns for expenses
        self.expense_columns = [
            'date', 'amount', 'currency', 'vendor', 'description', 
            'department', 'category'
        ]
        
        # Expected CSV columns for budgets
        self.budget_columns = [
            'department', 'category', 'period_start', 
            'period_end', 'allocated_amount', 'currency'
        ]
        
        # Vendor-to-category mappings for auto-categorization
        self.vendor_category_map = {
            # IT Infrastructure
            'aws': 'IT Infrastructure',
            'microsoft azure': 'IT Infrastructure',
            'google cloud': 'IT Infrastructure',
            'github': 'IT Infrastructure',
            'slack': 'IT Infrastructure',
            'zoom': 'IT Infrastructure',
            'docker': 'IT Infrastructure',
            'atlassian': 'IT Infrastructure',
            'jetbrains': 'IT Infrastructure',
            
            # Marketing
            'google ads': 'Marketing',
            'facebook ads': 'Marketing',
            'linkedin marketing': 'Marketing',
            'mailchimp': 'Marketing',
            'hubspot': 'Marketing',
            'salesforce': 'Marketing',
            'canva': 'Marketing',
            'adobe creative': 'Marketing',
            'hootsuite': 'Marketing',
            
            # Travel
            'delta': 'Travel',
            'united': 'Travel',
            'marriott': 'Travel',
            'hilton': 'Travel',
            'expedia': 'Travel',
            'uber': 'Travel',
            'lyft': 'Travel',
            'enterprise': 'Travel',
            'airbnb': 'Travel',
            
            # Office Supplies
            'staples': 'Office Supplies',
            'office depot': 'Office Supplies',
            'amazon business': 'Office Supplies',
            'costco': 'Office Supplies',
            'home depot': 'Office Supplies',
            'ikea': 'Office Supplies',
            
            # Personnel
            'adp': 'Personnel',
            'workday': 'Personnel',
            'bamboohr': 'Personnel',
            'gusto': 'Personnel',
            'paychex': 'Personnel',
            'linkedin recruiter': 'Personnel',
            
            # Utilities
            'pacific gas': 'Utilities',
            'verizon': 'Utilities',
            'at&t': 'Utilities',
            'comcast': 'Utilities',
            'waste management': 'Utilities',
            
            # Professional Services
            'deloitte': 'Professional Services',
            'pwc': 'Professional Services',
            'kpmg': 'Professional Services',
            'mckinsey': 'Professional Services',
            'legal': 'Professional Services',
            
            # Training
            'coursera': 'Training',
            'linkedin learning': 'Training',
            'udemy': 'Training',
            'pluralsight': 'Training',
            'conference': 'Training',
            
            # Equipment
            'dell': 'Equipment',
            'apple': 'Equipment',
            'hp': 'Equipment',
            'lenovo': 'Equipment',
            'canon': 'Equipment',
            'xerox': 'Equipment',
            'cisco': 'Equipment'
        }

    def auto_categorize_expense(self, vendor: str, description: str = "") -> str:
        """Automatically categorize expense based on vendor and description."""
        vendor_lower = vendor.lower()
        description_lower = description.lower()
        
        # Check vendor mappings
        for keyword, category in self.vendor_category_map.items():
            if keyword in vendor_lower:
                return category
        
        # Check description for keywords
        if any(word in description_lower for word in ['cloud', 'hosting', 'software', 'api']):
            return 'IT Infrastructure'
        elif any(word in description_lower for word in ['marketing', 'ad', 'campaign']):
            return 'Marketing'
        elif any(word in description_lower for word in ['travel', 'trip', 'hotel', 'flight']):
            return 'Travel'
        elif any(word in description_lower for word in ['office', 'supplies', 'desk']):
            return 'Office Supplies'
        elif any(word in description_lower for word in ['payroll', 'recruitment', 'hiring']):
            return 'Personnel'
        elif any(word in description_lower for word in ['utility', 'electric', 'internet', 'phone']):
            return 'Utilities'
        elif any(word in description_lower for word in ['legal', 'consulting', 'professional']):
            return 'Professional Services'
        elif any(word in description_lower for word in ['training', 'course', 'certification']):
            return 'Training'
        elif any(word in description_lower for word in ['computer', 'equipment', 'hardware']):
            return 'Equipment'
        
        return 'Other'

    def validate_date(self, date_str: str) -> Tuple[bool, Optional[date]]:
        """Validate and parse date string."""
        if not date_str or pd.isna(date_str):
            return False, None
        
        # Try different date formats
        date_formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y/%m/%d',
            '%m-%d-%Y',
            '%d-%m-%Y'
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(str(date_str), fmt).date()
                return True, parsed_date
            except ValueError:
                continue
        
        return False, None

    def validate_amount(self, amount_str: str) -> Tuple[bool, Optional[float]]:
        """Validate and parse amount string."""
        if not amount_str or pd.isna(amount_str):
            return False, None
        
        try:
            # Remove currency symbols and commas
            clean_amount = re.sub(r'[$,\s]', '', str(amount_str))
            amount = float(clean_amount)
            
            if amount <= 0:
                return False, None
            
            return True, round(amount, 2)
        except (ValueError, TypeError):
            return False, None

    def validate_department(self, department_str: str) -> Tuple[bool, Optional[str]]:
        """Validate department string."""
        if not department_str or pd.isna(department_str):
            return False, None
        
        department = str(department_str).strip()
        
        # Try exact match first
        for dept in DepartmentEnum:
            if dept.value.lower() == department.lower():
                return True, dept.value
        
        # Try partial matches
        department_mappings = {
            'eng': 'Engineering',
            'market': 'Marketing',
            'sale': 'Sales',
            'human': 'HR',
            'hr': 'HR',
            'finance': 'Finance',
            'fin': 'Finance',
            'ops': 'Operations',
            'operation': 'Operations',
            'exec': 'Executive',
            'executive': 'Executive'
        }
        
        for key, value in department_mappings.items():
            if key in department.lower():
                return True, value
        
        return False, None

    def validate_category(self, category_str: str) -> Tuple[bool, Optional[str]]:
        """Validate category string."""
        if not category_str or pd.isna(category_str):
            return False, None
        
        category = str(category_str).strip()
        
        # Try exact match first
        for cat in CategoryEnum:
            if cat.value.lower() == category.lower():
                return True, cat.value
        
        # Try partial matches
        category_mappings = {
            'it': 'IT Infrastructure',
            'tech': 'IT Infrastructure',
            'infrastructure': 'IT Infrastructure',
            'marketing': 'Marketing',
            'travel': 'Travel',
            'office': 'Office Supplies',
            'supplies': 'Office Supplies',
            'personnel': 'Personnel',
            'payroll': 'Personnel',
            'hr': 'Personnel',
            'utility': 'Utilities',
            'utilities': 'Utilities',
            'professional': 'Professional Services',
            'legal': 'Professional Services',
            'consulting': 'Professional Services',
            'training': 'Training',
            'education': 'Training',
            'equipment': 'Equipment',
            'hardware': 'Equipment'
        }
        
        for key, value in category_mappings.items():
            if key in category.lower():
                return True, value
        
        return False, None

    def validate_currency(self, currency_str: str) -> Tuple[bool, Optional[str]]:
        """Validate currency string."""
        if not currency_str or pd.isna(currency_str):
            return True, "USD"  # Default to USD if not provided
        
        currency = str(currency_str).strip().upper()
        
        # Check if it's one of our supported currencies
        valid_currencies = ['USD', 'INR', 'CAD', 'TRY']
        if currency in valid_currencies:
            return True, currency
        
        # Handle common variations
        currency_mappings = {
            'US': 'USD',
            'DOLLAR': 'USD',
            'DOLLARS': 'USD',
            'IN': 'INR',
            'RUPEE': 'INR',
            'RUPEES': 'INR',
            'CA': 'CAD',
            'CANADIAN': 'CAD',
            'TR': 'TRY',
            'TURKISH': 'TRY',
            'LIRA': 'TRY'
        }
        
        if currency in currency_mappings:
            return True, currency_mappings[currency]
        
        return False, None

    def process_expense_csv(self, file_path: Path) -> UploadResponse:
        """Process expense CSV file and return upload response."""
        self.errors = []
        self.warnings = []
        processed_records = 0
        
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Check required columns
            missing_cols = [col for col in self.expense_columns if col not in df.columns]
            if missing_cols:
                return UploadResponse(
                    success=False,
                    message=f"Missing required columns: {missing_cols}",
                    records_processed=0,
                    errors=[f"Missing columns: {', '.join(missing_cols)}"]
                )
            
            valid_expenses = []
            
            for index, row in df.iterrows():
                row_errors = []
                
                # Validate date
                date_valid, expense_date = self.validate_date(row['date'])
                if not date_valid:
                    row_errors.append(f"Invalid date: {row['date']}")
                
                # Validate amount
                amount_valid, amount = self.validate_amount(row['amount'])
                if not amount_valid:
                    row_errors.append(f"Invalid amount: {row['amount']}")
                
                # Validate vendor
                vendor = str(row['vendor']).strip() if not pd.isna(row['vendor']) else ""
                if not vendor:
                    row_errors.append("Vendor is required")
                
                # Validate department
                dept_valid, department = self.validate_department(row['department'])
                if not dept_valid:
                    row_errors.append(f"Invalid department: {row['department']}")
                
                # Validate currency
                currency_valid, currency = self.validate_currency(row.get('currency', 'USD'))
                if not currency_valid:
                    row_errors.append(f"Invalid currency: {row.get('currency', 'USD')}")
                
                # Handle category (auto-categorize if missing)
                category = None
                if 'category' in row and not pd.isna(row['category']):
                    cat_valid, category = self.validate_category(row['category'])
                    if not cat_valid:
                        self.warnings.append(f"Row {index + 2}: Invalid category '{row['category']}', will auto-categorize")
                        category = None
                
                if not category and vendor:
                    category = self.auto_categorize_expense(vendor, str(row.get('description', '')))
                    self.warnings.append(f"Row {index + 2}: Auto-categorized as '{category}'")
                
                # If we have errors, log them and skip this row
                if row_errors:
                    error_msg = f"Row {index + 2}: {'; '.join(row_errors)}"
                    self.errors.append(error_msg)
                    continue
                
                # Create expense record
                expense = ExpenseDB(
                    date=expense_date,
                    amount=amount,
                    currency=currency,
                    vendor=vendor,
                    description=str(row.get('description', '')).strip(),
                    department=department,
                    category=category,
                    is_recurring=False,  # Default to False, can be enhanced later
                    created_at=datetime.utcnow()
                )
                
                valid_expenses.append(expense)
                processed_records += 1
            
            # Bulk insert valid records
            if valid_expenses:
                self.db.bulk_save_objects(valid_expenses)
                self.db.commit()
            
            # Prepare response
            success = len(self.errors) == 0
            message = f"Successfully processed {processed_records} records"
            if self.errors:
                message += f" with {len(self.errors)} errors"
            if self.warnings:
                message += f" and {len(self.warnings)} warnings"
            
            return UploadResponse(
                success=success,
                message=message,
                records_processed=processed_records,
                errors=self.errors[:10]  # Limit to first 10 errors
            )
        
        except Exception as e:
            self.db.rollback()
            return UploadResponse(
                success=False,
                message=f"Error processing file: {str(e)}",
                records_processed=0,
                errors=[str(e)]
            )

    def process_budget_csv(self, file_path: Path) -> UploadResponse:
        """Process budget CSV file and return upload response."""
        self.errors = []
        self.warnings = []
        processed_records = 0
        
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Check required columns
            missing_cols = [col for col in self.budget_columns if col not in df.columns]
            if missing_cols:
                return UploadResponse(
                    success=False,
                    message=f"Missing required columns: {missing_cols}",
                    records_processed=0,
                    errors=[f"Missing columns: {', '.join(missing_cols)}"]
                )
            
            valid_budgets = []
            
            for index, row in df.iterrows():
                row_errors = []
                
                # Validate department
                dept_valid, department = self.validate_department(row['department'])
                if not dept_valid:
                    row_errors.append(f"Invalid department: {row['department']}")
                
                # Validate category
                cat_valid, category = self.validate_category(row['category'])
                if not cat_valid:
                    row_errors.append(f"Invalid category: {row['category']}")
                
                # Validate period start
                start_valid, period_start = self.validate_date(row['period_start'])
                if not start_valid:
                    row_errors.append(f"Invalid period_start: {row['period_start']}")
                
                # Validate period end
                end_valid, period_end = self.validate_date(row['period_end'])
                if not end_valid:
                    row_errors.append(f"Invalid period_end: {row['period_end']}")
                
                # Validate allocated amount
                amount_valid, allocated_amount = self.validate_amount(row['allocated_amount'])
                if not amount_valid:
                    row_errors.append(f"Invalid allocated_amount: {row['allocated_amount']}")
                
                # Validate currency
                currency_valid, currency = self.validate_currency(row.get('currency', 'USD'))
                if not currency_valid:
                    row_errors.append(f"Invalid currency: {row.get('currency', 'USD')}")
                
                # If we have errors, log them and skip this row
                if row_errors:
                    error_msg = f"Row {index + 2}: {'; '.join(row_errors)}"
                    self.errors.append(error_msg)
                    continue
                
                # Create budget record
                budget = BudgetDB(
                    department=department,
                    category=category,
                    period_start=period_start,
                    period_end=period_end,
                    allocated_amount=allocated_amount,
                    currency=currency,
                    spent_amount=0.0,  # Will be calculated later
                    created_at=datetime.utcnow()
                )
                
                valid_budgets.append(budget)
                processed_records += 1
            
            # Bulk insert valid records
            if valid_budgets:
                self.db.bulk_save_objects(valid_budgets)
                self.db.commit()
            
            # Prepare response
            success = len(self.errors) == 0
            message = f"Successfully processed {processed_records} records"
            if self.errors:
                message += f" with {len(self.errors)} errors"
            
            return UploadResponse(
                success=success,
                message=message,
                records_processed=processed_records,
                errors=self.errors[:10]  # Limit to first 10 errors
            )
        
        except Exception as e:
            self.db.rollback()
            return UploadResponse(
                success=False,
                message=f"Error processing file: {str(e)}",
                records_processed=0,
                errors=[str(e)]
            )

    def get_data_summary(self) -> Dict:
        """Get summary statistics of current data in database."""
        try:
            # Total expenses
            total_expenses = self.db.query(ExpenseDB).count()
            total_amount = self.db.query(ExpenseDB).with_entities(
                ExpenseDB.amount
            ).all()
            total_spent = sum(amount[0] for amount in total_amount) if total_amount else 0
            
            # Total budgets
            total_budgets = self.db.query(BudgetDB).count()
            budget_amount = self.db.query(BudgetDB).with_entities(
                BudgetDB.allocated_amount
            ).all()
            total_allocated = sum(amount[0] for amount in budget_amount) if budget_amount else 0
            
            # Recent expenses (last 10)
            recent_expenses = self.db.query(ExpenseDB).order_by(
                ExpenseDB.created_at.desc()
            ).limit(10).all()
            
            return {
                "total_expenses": total_expenses,
                "total_spent": round(total_spent, 2),
                "total_budgets": total_budgets,
                "total_allocated": round(total_allocated, 2),
                "recent_expenses": [
                    {
                        "date": exp.date.strftime("%Y-%m-%d"),
                        "amount": exp.amount,
                        "currency": getattr(exp, 'currency', 'USD'),
                        "vendor": exp.vendor,
                        "department": exp.department,
                        "category": exp.category
                    }
                    for exp in recent_expenses
                ]
            }
        
        except Exception as e:
            return {"error": str(e)}
    
    def get_expenses(self, limit: int = 100, offset: int = 0, filters: Dict = None) -> List[Dict]:
        """Get expenses with optional filtering."""
        try:
            query = self.db.query(ExpenseDB)
            
            if filters:
                if filters.get('department'):
                    query = query.filter(ExpenseDB.department == filters['department'])
                if filters.get('category'):
                    query = query.filter(ExpenseDB.category == filters['category'])
                if filters.get('currency'):
                    query = query.filter(ExpenseDB.currency == filters['currency'])
                if filters.get('start_date'):
                    query = query.filter(ExpenseDB.date >= filters['start_date'])
                if filters.get('end_date'):
                    query = query.filter(ExpenseDB.date <= filters['end_date'])
            
            expenses = query.order_by(ExpenseDB.date.desc()).offset(offset).limit(limit).all()
            
            return [
                {
                    'id': exp.id,
                    'date': exp.date.strftime('%Y-%m-%d'),
                    'amount': float(exp.amount),
                    'currency': getattr(exp, 'currency', 'USD'),
                    'vendor': exp.vendor,
                    'description': exp.description,
                    'department': exp.department,
                    'category': exp.category,
                    'created_at': exp.created_at.isoformat() if exp.created_at else None
                }
                for exp in expenses
            ]
            
        except Exception as e:
            return []
    
    def get_budgets(self, limit: int = 100, offset: int = 0, filters: Dict = None) -> List[Dict]:
        """Get budgets with optional filtering."""
        try:
            query = self.db.query(BudgetDB)
            
            if filters:
                if filters.get('department'):
                    query = query.filter(BudgetDB.department == filters['department'])
                if filters.get('category'):
                    query = query.filter(BudgetDB.category == filters['category'])
                if filters.get('currency'):
                    query = query.filter(BudgetDB.currency == filters['currency'])
                if filters.get('start_date'):
                    query = query.filter(BudgetDB.period_start >= filters['start_date'])
                if filters.get('end_date'):
                    query = query.filter(BudgetDB.period_end <= filters['end_date'])
            
            budgets = query.order_by(BudgetDB.created_at.desc()).offset(offset).limit(limit).all()
            
            return [
                {
                    'id': budget.id,
                    'department': budget.department,
                    'category': budget.category,
                    'period_start': budget.period_start.strftime('%Y-%m-%d'),
                    'period_end': budget.period_end.strftime('%Y-%m-%d'),
                    'allocated_amount': float(budget.allocated_amount),
                    'currency': getattr(budget, 'currency', 'USD'),
                    'spent_amount': float(getattr(budget, 'spent_amount', 0)),
                    'created_at': budget.created_at.isoformat() if budget.created_at else None
                }
                for budget in budgets
            ]
            
        except Exception as e:
            return []
    
    def add_expense(self, date: str, amount: float, vendor: str, description: str, 
                   department: str, category: str, currency: str = "USD") -> Dict:
        """Add a new expense record."""
        try:
            # Validate inputs
            date_valid, expense_date = self.validate_date(date)
            if not date_valid:
                return {'success': False, 'error': f'Invalid date: {date}'}
            
            dept_valid, validated_dept = self.validate_department(department)
            if not dept_valid:
                return {'success': False, 'error': f'Invalid department: {department}'}
            
            cat_valid, validated_cat = self.validate_category(category)
            if not cat_valid:
                # Auto-categorize if invalid
                validated_cat = self.auto_categorize_expense(vendor, description)
            
            currency_valid, validated_currency = self.validate_currency(currency)
            if not currency_valid:
                return {'success': False, 'error': f'Invalid currency: {currency}'}
            
            expense = ExpenseDB(
                date=expense_date,
                amount=amount,
                currency=validated_currency,
                vendor=vendor,
                description=description,
                department=validated_dept,
                category=validated_cat,
                is_recurring=False,
                created_at=datetime.utcnow()
            )
            
            self.db.add(expense)
            self.db.commit()
            
            return {'success': True, 'id': expense.id}
            
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def add_budget(self, department: str, category: str, period_start: str, 
                  period_end: str, allocated_amount: float, currency: str = "USD") -> Dict:
        """Add a new budget record."""
        try:
            # Validate inputs
            start_valid, start_date = self.validate_date(period_start)
            if not start_valid:
                return {'success': False, 'error': f'Invalid period_start: {period_start}'}
            
            end_valid, end_date = self.validate_date(period_end)
            if not end_valid:
                return {'success': False, 'error': f'Invalid period_end: {period_end}'}
            
            dept_valid, validated_dept = self.validate_department(department)
            if not dept_valid:
                return {'success': False, 'error': f'Invalid department: {department}'}
            
            cat_valid, validated_cat = self.validate_category(category)
            if not cat_valid:
                return {'success': False, 'error': f'Invalid category: {category}'}
            
            currency_valid, validated_currency = self.validate_currency(currency)
            if not currency_valid:
                return {'success': False, 'error': f'Invalid currency: {currency}'}
            
            budget = BudgetDB(
                department=validated_dept,
                category=validated_cat,
                period_start=start_date,
                period_end=end_date,
                allocated_amount=allocated_amount,
                currency=validated_currency,
                spent_amount=0.0,
                created_at=datetime.utcnow()
            )
            
            self.db.add(budget)
            self.db.commit()
            
            return {'success': True, 'id': budget.id}
            
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_spending_by_department(self, months: int = 12) -> List[Dict]:
        """Get spending breakdown by department."""
        try:
            from sqlalchemy import func
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.now() - timedelta(days=months * 30)
            
            results = self.db.query(
                ExpenseDB.department,
                func.sum(ExpenseDB.amount).label('total_amount'),
                func.count(ExpenseDB.id).label('transaction_count'),
                func.avg(ExpenseDB.amount).label('avg_amount')
            ).filter(
                ExpenseDB.date >= cutoff_date.date()
            ).group_by(
                ExpenseDB.department
            ).order_by(
                func.sum(ExpenseDB.amount).desc()
            ).all()
            
            return [
                {
                    'department': result.department,
                    'total_amount': float(result.total_amount),
                    'transaction_count': result.transaction_count,
                    'avg_amount': float(result.avg_amount)
                }
                for result in results
            ]
            
        except Exception as e:
            return []
    
    def get_spending_by_category(self, months: int = 12) -> List[Dict]:
        """Get spending breakdown by category."""
        try:
            from sqlalchemy import func
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.now() - timedelta(days=months * 30)
            
            results = self.db.query(
                ExpenseDB.category,
                func.sum(ExpenseDB.amount).label('total_amount'),
                func.count(ExpenseDB.id).label('transaction_count'),
                func.avg(ExpenseDB.amount).label('avg_amount')
            ).filter(
                ExpenseDB.date >= cutoff_date.date()
            ).group_by(
                ExpenseDB.category
            ).order_by(
                func.sum(ExpenseDB.amount).desc()
            ).all()
            
            return [
                {
                    'category': result.category,
                    'total_amount': float(result.total_amount),
                    'transaction_count': result.transaction_count,
                    'avg_amount': float(result.avg_amount)
                }
                for result in results
            ]
            
        except Exception as e:
            return []
    
    def get_monthly_trends(self, months: int = 12) -> List[Dict]:
        """Get monthly spending trends."""
        try:
            from sqlalchemy import func, extract
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.now() - timedelta(days=months * 30)
            
            results = self.db.query(
                func.strftime('%Y-%m', ExpenseDB.date).label('month'),
                func.sum(ExpenseDB.amount).label('total_amount'),
                func.count(ExpenseDB.id).label('transaction_count')
            ).filter(
                ExpenseDB.date >= cutoff_date.date()
            ).group_by(
                func.strftime('%Y-%m', ExpenseDB.date)
            ).order_by(
                'month'
            ).all()
            
            return [
                {
                    'month': result.month,
                    'total_amount': float(result.total_amount),
                    'transaction_count': result.transaction_count
                }
                for result in results
            ]
            
        except Exception as e:
            return []

    def __del__(self):
        """Clean up database connection."""
        if hasattr(self, 'db'):
            self.db.close() 