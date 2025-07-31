"""Synthetic data generator for Nsight AI Budgeting System."""

import random
import pandas as pd
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from faker import Faker

try:
    from .database import SessionLocal, ExpenseDB, BudgetDB, init_db
    from .models import DepartmentEnum, CategoryEnum
except ImportError:
    # For standalone execution
    from database import SessionLocal, ExpenseDB, BudgetDB, init_db
    from models import DepartmentEnum, CategoryEnum

# Initialize Faker for realistic data
fake = Faker()

class SyntheticDataGenerator:
    """Generate realistic synthetic data for Nsight budgeting system."""
    
    def __init__(self):
        self.db = SessionLocal()
        
        # Realistic vendor mappings by category
        self.vendors_by_category = {
            CategoryEnum.IT_INFRASTRUCTURE: [
                "AWS", "Microsoft Azure", "Google Cloud", "DigitalOcean", "Heroku",
                "GitHub", "Slack", "Zoom", "Atlassian", "JetBrains", "Docker"
            ],
            CategoryEnum.MARKETING: [
                "Google Ads", "Facebook Ads", "LinkedIn Marketing", "Mailchimp",
                "HubSpot", "Salesforce", "Canva", "Adobe Creative", "Hootsuite"
            ],
            CategoryEnum.TRAVEL: [
                "Delta Airlines", "United Airlines", "Marriott Hotels", "Hilton",
                "Expedia", "Uber", "Lyft", "Enterprise Rent-A-Car", "Airbnb"
            ],
            CategoryEnum.OFFICE_SUPPLIES: [
                "Staples", "Office Depot", "Amazon Business", "Costco Business",
                "Best Buy Business", "Home Depot", "IKEA Business"
            ],
            CategoryEnum.PERSONNEL: [
                "ADP Payroll", "Workday", "BambooHR", "Gusto", "Paychex",
                "Indeed Hiring", "LinkedIn Recruiter", "Glassdoor"
            ],
            CategoryEnum.UTILITIES: [
                "Pacific Gas & Electric", "ConEd", "Verizon Business", 
                "AT&T Business", "Comcast Business", "Waste Management"
            ],
            CategoryEnum.PROFESSIONAL_SERVICES: [
                "Deloitte Consulting", "PwC", "KPMG", "EY", "McKinsey",
                "Legal Services Inc", "Smith & Associates", "Wilson Law Firm"
            ],
            CategoryEnum.TRAINING: [
                "Coursera Business", "LinkedIn Learning", "Udemy Business",
                "Pluralsight", "O'Reilly Media", "AWS Training", "Conference Registration"
            ],
            CategoryEnum.EQUIPMENT: [
                "Dell Business", "Apple Business", "HP Enterprise", "Lenovo",
                "Canon Business", "Xerox", "Cisco Systems", "NetGear"
            ]
        }
        
        # Department budget allocations (monthly)
        self.department_budgets = {
            DepartmentEnum.ENGINEERING: {
                CategoryEnum.IT_INFRASTRUCTURE: 15000,
                CategoryEnum.EQUIPMENT: 8000,
                CategoryEnum.TRAINING: 5000,
                CategoryEnum.PERSONNEL: 45000,
                CategoryEnum.OTHER: 2000
            },
            DepartmentEnum.MARKETING: {
                CategoryEnum.MARKETING: 25000,
                CategoryEnum.TRAVEL: 8000,
                CategoryEnum.EQUIPMENT: 3000,
                CategoryEnum.TRAINING: 3000,
                CategoryEnum.OTHER: 1000
            },
            DepartmentEnum.SALES: {
                CategoryEnum.TRAVEL: 12000,
                CategoryEnum.MARKETING: 5000,
                CategoryEnum.EQUIPMENT: 4000,
                CategoryEnum.TRAINING: 4000,
                CategoryEnum.PERSONNEL: 35000,
                CategoryEnum.OTHER: 2000
            },
            DepartmentEnum.HR: {
                CategoryEnum.PERSONNEL: 20000,
                CategoryEnum.TRAINING: 6000,
                CategoryEnum.PROFESSIONAL_SERVICES: 4000,
                CategoryEnum.OFFICE_SUPPLIES: 2000,
                CategoryEnum.OTHER: 1000
            },
            DepartmentEnum.FINANCE: {
                CategoryEnum.PROFESSIONAL_SERVICES: 8000,
                CategoryEnum.IT_INFRASTRUCTURE: 3000,
                CategoryEnum.EQUIPMENT: 2000,
                CategoryEnum.TRAINING: 2000,
                CategoryEnum.PERSONNEL: 25000
            },
            DepartmentEnum.OPERATIONS: {
                CategoryEnum.UTILITIES: 5000,
                CategoryEnum.OFFICE_SUPPLIES: 4000,
                CategoryEnum.EQUIPMENT: 6000,
                CategoryEnum.PROFESSIONAL_SERVICES: 3000,
                CategoryEnum.PERSONNEL: 20000,
                CategoryEnum.OTHER: 2000
            },
            DepartmentEnum.EXECUTIVE: {
                CategoryEnum.TRAVEL: 8000,
                CategoryEnum.PROFESSIONAL_SERVICES: 10000,
                CategoryEnum.EQUIPMENT: 3000,
                CategoryEnum.OTHER: 5000
            }
        }

    def generate_expense_amount(self, category: CategoryEnum, is_anomaly: bool = False) -> float:
        """Generate realistic expense amounts based on category."""
        base_amounts = {
            CategoryEnum.IT_INFRASTRUCTURE: (200, 3000),
            CategoryEnum.MARKETING: (500, 5000),
            CategoryEnum.TRAVEL: (300, 2500),
            CategoryEnum.OFFICE_SUPPLIES: (50, 800),
            CategoryEnum.PERSONNEL: (3000, 15000),
            CategoryEnum.UTILITIES: (200, 1500),
            CategoryEnum.PROFESSIONAL_SERVICES: (1000, 8000),
            CategoryEnum.TRAINING: (100, 2000),
            CategoryEnum.EQUIPMENT: (500, 5000),
            CategoryEnum.OTHER: (100, 1000)
        }
        
        min_amt, max_amt = base_amounts.get(category, (100, 1000))
        
        if is_anomaly:
            # Create anomalies that are 2-5x normal amounts
            multiplier = random.uniform(2.0, 5.0)
            return round(random.uniform(min_amt, max_amt) * multiplier, 2)
        
        return round(random.uniform(min_amt, max_amt), 2)

    def generate_expenses(self, start_date: date, end_date: date, num_records: int = 1000):
        """Generate synthetic expense records using SQL."""
        print(f"Generating {num_records} expense records from {start_date} to {end_date}...")
        
        expenses = []
        
        for _ in range(num_records):
            # Random date within range
            random_date = start_date + timedelta(
                days=random.randint(0, (end_date - start_date).days)
            )
            
            # Random department and category
            department = random.choice(list(DepartmentEnum))
            category = random.choice(list(CategoryEnum))
            
            # 5% chance of anomaly
            is_anomaly = random.random() < 0.05
            
            # Generate realistic vendor and amount
            vendor = random.choice(self.vendors_by_category.get(category, ["Generic Vendor"]))
            amount = self.generate_expense_amount(category, is_anomaly)
            
            # Generate description
            descriptions = {
                CategoryEnum.IT_INFRASTRUCTURE: ["Cloud hosting costs", "Software licenses", "API usage fees"],
                CategoryEnum.MARKETING: ["Ad campaign", "Marketing tools subscription", "Content creation"],
                CategoryEnum.TRAVEL: ["Business trip", "Conference travel", "Client meeting travel"],
                CategoryEnum.OFFICE_SUPPLIES: ["Office materials", "Desk supplies", "Meeting room supplies"],
                CategoryEnum.PERSONNEL: ["Contractor payment", "Recruitment fees", "Employee benefits"],
                CategoryEnum.UTILITIES: ["Monthly utilities", "Internet service", "Phone service"],
                CategoryEnum.PROFESSIONAL_SERVICES: ["Legal consultation", "Accounting services", "Business consulting"],
                CategoryEnum.TRAINING: ["Online course", "Professional certification", "Conference registration"],
                CategoryEnum.EQUIPMENT: ["Computer equipment", "Office furniture", "Software/hardware"],
                CategoryEnum.OTHER: ["Miscellaneous expense", "General business cost"]
            }
            
            description = random.choice(descriptions.get(category, ["Business expense"]))
            
            # Determine if recurring (monthly subscriptions, etc.)
            recurring_categories = [CategoryEnum.IT_INFRASTRUCTURE, CategoryEnum.UTILITIES, CategoryEnum.PERSONNEL]
            is_recurring = category in recurring_categories and random.random() < 0.3
            
            expense = ExpenseDB(
                date=random_date,
                amount=amount,
                vendor=vendor,
                description=description,
                department=department.value,
                category=category.value,
                is_recurring=is_recurring,
                created_at=datetime.utcnow()
            )
            
            expenses.append(expense)
        
        # Bulk insert using SQL
        self.db.bulk_save_objects(expenses)
        self.db.commit()
        print(f"✅ Generated {len(expenses)} expense records")

    def generate_budgets(self, year: int = 2024):
        """Generate budget allocations for each department using SQL."""
        print(f"Generating budget allocations for {year}...")
        
        budgets = []
        
        for month in range(1, 13):  # 12 months
            period_start = date(year, month, 1)
            
            # Calculate last day of month
            if month == 12:
                period_end = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                period_end = date(year, month + 1, 1) - timedelta(days=1)
            
            for department, categories in self.department_budgets.items():
                for category, monthly_amount in categories.items():
                    # Add some variation to budgets (±10%)
                    variation = random.uniform(0.9, 1.1)
                    allocated_amount = round(monthly_amount * variation, 2)
                    
                    budget = BudgetDB(
                        department=department.value,
                        category=category.value,
                        period_start=period_start,
                        period_end=period_end,
                        allocated_amount=allocated_amount,
                        spent_amount=0.0,  # Will be calculated later
                        created_at=datetime.utcnow()
                    )
                    
                    budgets.append(budget)
        
        # Bulk insert budgets
        self.db.bulk_save_objects(budgets)
        self.db.commit()
        print(f"✅ Generated {len(budgets)} budget records")

    def update_budget_spent_amounts(self):
        """Update spent amounts in budgets based on actual expenses using SQL."""
        print("Calculating spent amounts for budgets...")
        
        # SQL query to calculate spent amounts
        query = """
        UPDATE budgets 
        SET spent_amount = (
            SELECT COALESCE(SUM(expenses.amount), 0)
            FROM expenses 
            WHERE expenses.department = budgets.department
            AND expenses.category = budgets.category
            AND expenses.date >= budgets.period_start
            AND expenses.date <= budgets.period_end
        )
        """
        
        self.db.execute(query)
        self.db.commit()
        print("✅ Updated budget spent amounts")

    def generate_seasonal_patterns(self):
        """Add seasonal spending patterns for more realistic data."""
        print("Adding seasonal spending patterns...")
        
        # Q4 increased marketing spend
        q4_marketing = []
        for month in [10, 11, 12]:
            for _ in range(20):  # Extra marketing expenses
                expense_date = date(2024, month, random.randint(1, 28))
                amount = self.generate_expense_amount(CategoryEnum.MARKETING) * 1.5
                
                expense = ExpenseDB(
                    date=expense_date,
                    amount=round(amount, 2),
                    vendor=random.choice(self.vendors_by_category[CategoryEnum.MARKETING]),
                    description="Holiday campaign spending",
                    department=DepartmentEnum.MARKETING.value,
                    category=CategoryEnum.MARKETING.value,
                    is_recurring=False,
                    created_at=datetime.utcnow()
                )
                q4_marketing.append(expense)
        
        # Summer conference travel
        summer_travel = []
        for month in [6, 7, 8]:
            for _ in range(15):
                expense_date = date(2024, month, random.randint(1, 28))
                amount = self.generate_expense_amount(CategoryEnum.TRAVEL) * 1.3
                
                expense = ExpenseDB(
                    date=expense_date,
                    amount=round(amount, 2),
                    vendor=random.choice(self.vendors_by_category[CategoryEnum.TRAVEL]),
                    description="Summer conference travel",
                    department=random.choice([DepartmentEnum.ENGINEERING, DepartmentEnum.SALES]).value,
                    category=CategoryEnum.TRAVEL.value,
                    is_recurring=False,
                    created_at=datetime.utcnow()
                )
                summer_travel.append(expense)
        
        self.db.bulk_save_objects(q4_marketing + summer_travel)
        self.db.commit()
        print(f"✅ Added {len(q4_marketing + summer_travel)} seasonal expenses")

    def print_data_summary(self):
        """Print summary of generated data using SQL queries."""
        print("\n" + "="*50)
        print("📊 SYNTHETIC DATA SUMMARY")
        print("="*50)
        
        # Total expenses
        total_expenses = self.db.query(ExpenseDB).count()
        total_amount = self.db.query(ExpenseDB).with_entities(
            ExpenseDB.amount
        ).all()
        total_spent = sum(amount[0] for amount in total_amount)
        
        print(f"💰 Total Expenses: {total_expenses:,} records")
        print(f"💵 Total Amount: ${total_spent:,.2f}")
        
        # Expenses by department
        print("\n📈 Expenses by Department:")
        dept_query = """
        SELECT department, COUNT(*) as count, SUM(amount) as total
        FROM expenses 
        GROUP BY department 
        ORDER BY total DESC
        """
        dept_results = self.db.execute(dept_query).fetchall()
        for dept, count, total in dept_results:
            print(f"  {dept}: {count} expenses, ${total:,.2f}")
        
        # Expenses by category
        print("\n📊 Expenses by Category:")
        cat_query = """
        SELECT category, COUNT(*) as count, SUM(amount) as total
        FROM expenses 
        GROUP BY category 
        ORDER BY total DESC
        """
        cat_results = self.db.execute(cat_query).fetchall()
        for category, count, total in cat_results:
            print(f"  {category}: {count} expenses, ${total:,.2f}")
        
        # Budget summary
        total_budgets = self.db.query(BudgetDB).count()
        budget_amount = self.db.query(BudgetDB).with_entities(
            BudgetDB.allocated_amount
        ).all()
        total_allocated = sum(amount[0] for amount in budget_amount)
        
        print(f"\n🎯 Total Budgets: {total_budgets} records")
        print(f"💰 Total Allocated: ${total_allocated:,.2f}")
        
        # Top vendors
        print("\n🏢 Top Vendors by Spend:")
        vendor_query = """
        SELECT vendor, COUNT(*) as transactions, SUM(amount) as total
        FROM expenses 
        GROUP BY vendor 
        ORDER BY total DESC 
        LIMIT 10
        """
        vendor_results = self.db.execute(vendor_query).fetchall()
        for vendor, transactions, total in vendor_results:
            print(f"  {vendor}: {transactions} transactions, ${total:,.2f}")

    def generate_all_data(self, months_back: int = 12):
        """Generate complete synthetic dataset."""
        print("🚀 Starting synthetic data generation for Nsight...")
        
        # Date range for the last N months
        end_date = date.today()
        start_date = end_date - timedelta(days=months_back * 30)
        
        try:
            # Generate core data
            self.generate_expenses(start_date, end_date, num_records=1500)
            self.generate_budgets(year=2024)
            self.generate_seasonal_patterns()
            self.update_budget_spent_amounts()
            
            # Print summary
            self.print_data_summary()
            
            print(f"\n🎉 Synthetic data generation complete!")
            print(f"✅ Database ready for Nsight AI Budgeting System")
            
        except Exception as e:
            print(f"❌ Error generating data: {e}")
            self.db.rollback()
        finally:
            self.db.close()

def main():
    """Main function to run data generation."""
    # Initialize database
    init_db()
    
    # Generate synthetic data
    generator = SyntheticDataGenerator()
    generator.generate_all_data(months_back=12)

if __name__ == "__main__":
    main() 