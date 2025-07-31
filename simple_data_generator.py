#!/usr/bin/env python3
"""Simplified synthetic data generator for Nsight AI Budgeting System using only built-in libraries."""

import random
import csv
import json
from datetime import datetime, date, timedelta
import os

class SimpleSyntheticDataGenerator:
    """Generate realistic synthetic data using only built-in Python libraries."""
    
    def __init__(self):
        # Create data directories
        os.makedirs("data", exist_ok=True)
        os.makedirs("uploads", exist_ok=True)
        os.makedirs("models", exist_ok=True)
        
        # Realistic vendor mappings by category
        self.vendors_by_category = {
            "IT Infrastructure": [
                "AWS", "Microsoft Azure", "Google Cloud", "DigitalOcean", "Heroku",
                "GitHub", "Slack", "Zoom", "Atlassian", "JetBrains", "Docker"
            ],
            "Marketing": [
                "Google Ads", "Facebook Ads", "LinkedIn Marketing", "Mailchimp",
                "HubSpot", "Salesforce", "Canva", "Adobe Creative", "Hootsuite"
            ],
            "Travel": [
                "Delta Airlines", "United Airlines", "Marriott Hotels", "Hilton",
                "Expedia", "Uber", "Lyft", "Enterprise Rent-A-Car", "Airbnb"
            ],
            "Office Supplies": [
                "Staples", "Office Depot", "Amazon Business", "Costco Business",
                "Best Buy Business", "Home Depot", "IKEA Business"
            ],
            "Personnel": [
                "ADP Payroll", "Workday", "BambooHR", "Gusto", "Paychex",
                "Indeed Hiring", "LinkedIn Recruiter", "Glassdoor"
            ],
            "Utilities": [
                "Pacific Gas & Electric", "ConEd", "Verizon Business", 
                "AT&T Business", "Comcast Business", "Waste Management"
            ],
            "Professional Services": [
                "Deloitte Consulting", "PwC", "KPMG", "EY", "McKinsey",
                "Legal Services Inc", "Smith & Associates", "Wilson Law Firm"
            ],
            "Training": [
                "Coursera Business", "LinkedIn Learning", "Udemy Business",
                "Pluralsight", "O'Reilly Media", "AWS Training", "Conference Registration"
            ],
            "Equipment": [
                "Dell Business", "Apple Business", "HP Enterprise", "Lenovo",
                "Canon Business", "Xerox", "Cisco Systems", "NetGear"
            ],
            "Other": [
                "Miscellaneous Vendor", "General Supplies Co", "Business Services Inc"
            ]
        }
        
        # Department list
        self.departments = [
            "Engineering", "Marketing", "Sales", "HR", 
            "Finance", "Operations", "Executive"
        ]
        
        # Categories
        self.categories = list(self.vendors_by_category.keys())
        
        # Department budget allocations (monthly)
        self.department_budgets = {
            "Engineering": {
                "IT Infrastructure": 15000,
                "Equipment": 8000,
                "Training": 5000,
                "Personnel": 45000,
                "Other": 2000
            },
            "Marketing": {
                "Marketing": 25000,
                "Travel": 8000,
                "Equipment": 3000,
                "Training": 3000,
                "Other": 1000
            },
            "Sales": {
                "Travel": 12000,
                "Marketing": 5000,
                "Equipment": 4000,
                "Training": 4000,
                "Personnel": 35000,
                "Other": 2000
            },
            "HR": {
                "Personnel": 20000,
                "Training": 6000,
                "Professional Services": 4000,
                "Office Supplies": 2000,
                "Other": 1000
            },
            "Finance": {
                "Professional Services": 8000,
                "IT Infrastructure": 3000,
                "Equipment": 2000,
                "Training": 2000,
                "Personnel": 25000
            },
            "Operations": {
                "Utilities": 5000,
                "Office Supplies": 4000,
                "Equipment": 6000,
                "Professional Services": 3000,
                "Personnel": 20000,
                "Other": 2000
            },
            "Executive": {
                "Travel": 8000,
                "Professional Services": 10000,
                "Equipment": 3000,
                "Other": 5000
            }
        }

    def generate_expense_amount(self, category, is_anomaly=False):
        """Generate realistic expense amounts based on category."""
        base_amounts = {
            "IT Infrastructure": (200, 3000),
            "Marketing": (500, 5000),
            "Travel": (300, 2500),
            "Office Supplies": (50, 800),
            "Personnel": (3000, 15000),
            "Utilities": (200, 1500),
            "Professional Services": (1000, 8000),
            "Training": (100, 2000),
            "Equipment": (500, 5000),
            "Other": (100, 1000)
        }
        
        min_amt, max_amt = base_amounts.get(category, (100, 1000))
        
        if is_anomaly:
            # Create anomalies that are 2-5x normal amounts
            multiplier = random.uniform(2.0, 5.0)
            return round(random.uniform(min_amt, max_amt) * multiplier, 2)
        
        return round(random.uniform(min_amt, max_amt), 2)

    def generate_expenses_csv(self, start_date, end_date, num_records=1500):
        """Generate synthetic expense records and save to CSV."""
        print(f"Generating {num_records} expense records from {start_date} to {end_date}...")
        
        expenses = []
        
        for i in range(num_records):
            # Random date within range
            days_between = (end_date - start_date).days
            random_days = random.randint(0, days_between)
            expense_date = start_date + timedelta(days=random_days)
            
            # Random department and category
            department = random.choice(self.departments)
            category = random.choice(self.categories)
            
            # 5% chance of anomaly
            is_anomaly = random.random() < 0.05
            
            # Generate realistic vendor and amount
            vendor = random.choice(self.vendors_by_category.get(category, ["Generic Vendor"]))
            amount = self.generate_expense_amount(category, is_anomaly)
            
            # Generate description
            descriptions = {
                "IT Infrastructure": ["Cloud hosting costs", "Software licenses", "API usage fees"],
                "Marketing": ["Ad campaign", "Marketing tools subscription", "Content creation"],
                "Travel": ["Business trip", "Conference travel", "Client meeting travel"],
                "Office Supplies": ["Office materials", "Desk supplies", "Meeting room supplies"],
                "Personnel": ["Contractor payment", "Recruitment fees", "Employee benefits"],
                "Utilities": ["Monthly utilities", "Internet service", "Phone service"],
                "Professional Services": ["Legal consultation", "Accounting services", "Business consulting"],
                "Training": ["Online course", "Professional certification", "Conference registration"],
                "Equipment": ["Computer equipment", "Office furniture", "Software/hardware"],
                "Other": ["Miscellaneous expense", "General business cost"]
            }
            
            description = random.choice(descriptions.get(category, ["Business expense"]))
            
            # Determine if recurring
            recurring_categories = ["IT Infrastructure", "Utilities", "Personnel"]
            is_recurring = category in recurring_categories and random.random() < 0.3
            
            expense = {
                "id": i + 1,
                "date": expense_date.strftime("%Y-%m-%d"),
                "amount": amount,
                "vendor": vendor,
                "description": description,
                "department": department,
                "category": category,
                "is_recurring": is_recurring,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            expenses.append(expense)
        
        # Save to CSV
        csv_file = "data/expenses.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ["id", "date", "amount", "vendor", "description", "department", "category", "is_recurring", "created_at"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(expenses)
        
        print(f"✅ Generated {len(expenses)} expense records saved to {csv_file}")
        return expenses

    def generate_budgets_csv(self, year=2024):
        """Generate budget allocations and save to CSV."""
        print(f"Generating budget allocations for {year}...")
        
        budgets = []
        budget_id = 1
        
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
                    
                    budget = {
                        "id": budget_id,
                        "department": department,
                        "category": category,
                        "period_start": period_start.strftime("%Y-%m-%d"),
                        "period_end": period_end.strftime("%Y-%m-%d"),
                        "allocated_amount": allocated_amount,
                        "spent_amount": 0.0,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    budgets.append(budget)
                    budget_id += 1
        
        # Save to CSV
        csv_file = "data/budgets.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ["id", "department", "category", "period_start", "period_end", "allocated_amount", "spent_amount", "created_at"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(budgets)
        
        print(f"✅ Generated {len(budgets)} budget records saved to {csv_file}")
        return budgets

    def add_seasonal_patterns(self, expenses):
        """Add seasonal spending patterns."""
        print("Adding seasonal spending patterns...")
        
        seasonal_expenses = []
        expense_id = len(expenses) + 1
        
        # Q4 increased marketing spend
        for month in [10, 11, 12]:
            for _ in range(20):  # Extra marketing expenses
                expense_date = date(2024, month, random.randint(1, 28))
                amount = self.generate_expense_amount("Marketing") * 1.5
                
                expense = {
                    "id": expense_id,
                    "date": expense_date.strftime("%Y-%m-%d"),
                    "amount": round(amount, 2),
                    "vendor": random.choice(self.vendors_by_category["Marketing"]),
                    "description": "Holiday campaign spending",
                    "department": "Marketing",
                    "category": "Marketing",
                    "is_recurring": False,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                seasonal_expenses.append(expense)
                expense_id += 1
        
        # Summer conference travel
        for month in [6, 7, 8]:
            for _ in range(15):
                expense_date = date(2024, month, random.randint(1, 28))
                amount = self.generate_expense_amount("Travel") * 1.3
                department = random.choice(["Engineering", "Sales"])
                
                expense = {
                    "id": expense_id,
                    "date": expense_date.strftime("%Y-%m-%d"),
                    "amount": round(amount, 2),
                    "vendor": random.choice(self.vendors_by_category["Travel"]),
                    "description": "Summer conference travel",
                    "department": department,
                    "category": "Travel",
                    "is_recurring": False,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                seasonal_expenses.append(expense)
                expense_id += 1
        
        # Append to existing CSV
        csv_file = "data/expenses.csv"
        with open(csv_file, 'a', newline='', encoding='utf-8') as file:
            fieldnames = ["id", "date", "amount", "vendor", "description", "department", "category", "is_recurring", "created_at"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writerows(seasonal_expenses)
        
        print(f"✅ Added {len(seasonal_expenses)} seasonal expenses")
        return seasonal_expenses

    def generate_summary_json(self):
        """Generate summary statistics and save to JSON."""
        print("Generating data summary...")
        
        # Read expenses CSV
        expenses = []
        with open("data/expenses.csv", 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            expenses = list(reader)
        
        # Read budgets CSV
        budgets = []
        with open("data/budgets.csv", 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            budgets = list(reader)
        
        # Calculate summaries
        total_expenses = len(expenses)
        total_amount = sum(float(exp['amount']) for exp in expenses)
        
        # Department summary
        dept_summary = {}
        for exp in expenses:
            dept = exp['department']
            if dept not in dept_summary:
                dept_summary[dept] = {"count": 0, "total": 0}
            dept_summary[dept]["count"] += 1
            dept_summary[dept]["total"] += float(exp['amount'])
        
        # Category summary
        cat_summary = {}
        for exp in expenses:
            cat = exp['category']
            if cat not in cat_summary:
                cat_summary[cat] = {"count": 0, "total": 0}
            cat_summary[cat]["count"] += 1
            cat_summary[cat]["total"] += float(exp['amount'])
        
        # Budget summary
        total_budgets = len(budgets)
        total_allocated = sum(float(budget['allocated_amount']) for budget in budgets)
        
        # Top vendors
        vendor_summary = {}
        for exp in expenses:
            vendor = exp['vendor']
            if vendor not in vendor_summary:
                vendor_summary[vendor] = {"transactions": 0, "total": 0}
            vendor_summary[vendor]["transactions"] += 1
            vendor_summary[vendor]["total"] += float(exp['amount'])
        
        # Sort top vendors
        top_vendors = sorted(vendor_summary.items(), key=lambda x: x[1]['total'], reverse=True)[:10]
        
        summary = {
            "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_expenses": total_expenses,
            "total_amount": round(total_amount, 2),
            "total_budgets": total_budgets,
            "total_allocated": round(total_allocated, 2),
            "departments": {k: {"count": v["count"], "total": round(v["total"], 2)} for k, v in dept_summary.items()},
            "categories": {k: {"count": v["count"], "total": round(v["total"], 2)} for k, v in cat_summary.items()},
            "top_vendors": [{"vendor": vendor, "transactions": data["transactions"], "total": round(data["total"], 2)} for vendor, data in top_vendors]
        }
        
        # Save summary
        with open("data/summary.json", 'w', encoding='utf-8') as file:
            json.dump(summary, file, indent=2, ensure_ascii=False)
        
        return summary

    def print_summary(self, summary):
        """Print formatted summary."""
        print("\n" + "="*60)
        print("📊 NSIGHT SYNTHETIC DATA SUMMARY")
        print("="*60)
        
        print(f"💰 Total Expenses: {summary['total_expenses']:,} records")
        print(f"💵 Total Amount: ${summary['total_amount']:,.2f}")
        print(f"🎯 Total Budgets: {summary['total_budgets']} records")
        print(f"💰 Total Allocated: ${summary['total_allocated']:,.2f}")
        
        print(f"\n📈 Expenses by Department:")
        for dept, data in summary['departments'].items():
            print(f"  {dept}: {data['count']} expenses, ${data['total']:,.2f}")
        
        print(f"\n📊 Expenses by Category:")
        for cat, data in summary['categories'].items():
            print(f"  {cat}: {data['count']} expenses, ${data['total']:,.2f}")
        
        print(f"\n🏢 Top 10 Vendors by Spend:")
        for vendor_data in summary['top_vendors'][:10]:
            print(f"  {vendor_data['vendor']}: {vendor_data['transactions']} transactions, ${vendor_data['total']:,.2f}")

    def generate_all_data(self, months_back=12):
        """Generate complete synthetic dataset."""
        print("🚀 Starting synthetic data generation for Nsight...")
        print("="*60)
        
        # Date range for the last N months
        end_date = date.today()
        start_date = end_date - timedelta(days=months_back * 30)
        
        try:
            # Generate core data
            expenses = self.generate_expenses_csv(start_date, end_date, num_records=1500)
            budgets = self.generate_budgets_csv(year=2024)
            seasonal = self.add_seasonal_patterns(expenses)
            
            # Generate summary
            summary = self.generate_summary_json()
            self.print_summary(summary)
            
            print(f"\n🎉 Synthetic data generation complete!")
            print(f"✅ Files created in 'data/' directory:")
            print(f"  📄 expenses.csv ({len(expenses) + len(seasonal)} records)")
            print(f"  📄 budgets.csv ({len(budgets)} records)")
            print(f"  📄 summary.json (statistics)")
            print(f"\n📂 Ready for Nsight AI Budgeting System demo!")
            
        except Exception as e:
            print(f"❌ Error generating data: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main function to run data generation."""
    generator = SimpleSyntheticDataGenerator()
    generator.generate_all_data(months_back=12)

if __name__ == "__main__":
    main() 