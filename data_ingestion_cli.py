#!/usr/bin/env python3
"""Standalone CLI for Nsight AI Budgeting System data ingestion."""

import sys
import os
import argparse
import csv
from pathlib import Path
from datetime import datetime, date
import re

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("⚠️  Warning: pandas not available. Using basic CSV processing.")

class SimpleDataProcessor:
    """Simple data processor using only built-in libraries."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        
        # Vendor-to-category mappings for auto-categorization
        self.vendor_category_map = {
            'aws': 'IT Infrastructure',
            'microsoft': 'IT Infrastructure',
            'google cloud': 'IT Infrastructure',
            'github': 'IT Infrastructure',
            'slack': 'IT Infrastructure',
            'zoom': 'IT Infrastructure',
            'google ads': 'Marketing',
            'facebook': 'Marketing',
            'linkedin': 'Marketing',
            'hubspot': 'Marketing',
            'salesforce': 'Marketing',
            'delta': 'Travel',
            'united': 'Travel',
            'marriott': 'Travel',
            'hilton': 'Travel',
            'uber': 'Travel',
            'lyft': 'Travel',
            'staples': 'Office Supplies',
            'office depot': 'Office Supplies',
            'amazon': 'Office Supplies',
            'adp': 'Personnel',
            'workday': 'Personnel',
            'paychex': 'Personnel',
            'deloitte': 'Professional Services',
            'pwc': 'Professional Services',
            'kpmg': 'Professional Services',
            'coursera': 'Training',
            'udemy': 'Training',
            'dell': 'Equipment',
            'apple': 'Equipment',
            'hp': 'Equipment'
        }
        
        self.departments = ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations', 'Executive']
        self.categories = [
            'IT Infrastructure', 'Marketing', 'Travel', 'Office Supplies', 
            'Personnel', 'Utilities', 'Professional Services', 'Training', 
            'Equipment', 'Other'
        ]

    def auto_categorize_expense(self, vendor, description=""):
        """Auto-categorize expense based on vendor and description."""
        vendor_lower = vendor.lower()
        description_lower = description.lower()
        
        # Check vendor mappings
        for keyword, category in self.vendor_category_map.items():
            if keyword in vendor_lower:
                return category
        
        # Check description keywords
        if any(word in description_lower for word in ['cloud', 'software', 'api']):
            return 'IT Infrastructure'
        elif any(word in description_lower for word in ['marketing', 'ad', 'campaign']):
            return 'Marketing'
        elif any(word in description_lower for word in ['travel', 'trip', 'hotel']):
            return 'Travel'
        elif any(word in description_lower for word in ['office', 'supplies']):
            return 'Office Supplies'
        elif any(word in description_lower for word in ['payroll', 'recruitment']):
            return 'Personnel'
        elif any(word in description_lower for word in ['utility', 'electric', 'internet']):
            return 'Utilities'
        elif any(word in description_lower for word in ['legal', 'consulting']):
            return 'Professional Services'
        elif any(word in description_lower for word in ['training', 'course']):
            return 'Training'
        elif any(word in description_lower for word in ['computer', 'equipment']):
            return 'Equipment'
        
        return 'Other'

    def validate_date(self, date_str):
        """Validate and parse date string."""
        if not date_str:
            return False, None
        
        date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(str(date_str), fmt).date()
                return True, parsed_date
            except ValueError:
                continue
        
        return False, None

    def validate_amount(self, amount_str):
        """Validate and parse amount string."""
        if not amount_str:
            return False, None
        
        try:
            clean_amount = re.sub(r'[$,\s]', '', str(amount_str))
            amount = float(clean_amount)
            return amount > 0, round(amount, 2) if amount > 0 else None
        except (ValueError, TypeError):
            return False, None

    def validate_department(self, dept_str):
        """Validate department string."""
        if not dept_str:
            return False, None
        
        dept = str(dept_str).strip()
        
        # Exact matches
        for department in self.departments:
            if department.lower() == dept.lower():
                return True, department
        
        # Partial matches
        mappings = {
            'eng': 'Engineering', 'market': 'Marketing', 'sale': 'Sales',
            'hr': 'HR', 'human': 'HR', 'finance': 'Finance', 'fin': 'Finance',
            'ops': 'Operations', 'operation': 'Operations', 'exec': 'Executive'
        }
        
        for key, value in mappings.items():
            if key in dept.lower():
                return True, value
        
        return False, None

    def validate_category(self, cat_str):
        """Validate category string."""
        if not cat_str:
            return False, None
        
        category = str(cat_str).strip()
        
        # Exact matches
        for cat in self.categories:
            if cat.lower() == category.lower():
                return True, cat
        
        # Partial matches
        mappings = {
            'it': 'IT Infrastructure', 'tech': 'IT Infrastructure',
            'marketing': 'Marketing', 'travel': 'Travel',
            'office': 'Office Supplies', 'supplies': 'Office Supplies',
            'personnel': 'Personnel', 'payroll': 'Personnel',
            'utility': 'Utilities', 'professional': 'Professional Services',
            'legal': 'Professional Services', 'training': 'Training',
            'equipment': 'Equipment', 'hardware': 'Equipment'
        }
        
        for key, value in mappings.items():
            if key in category.lower():
                return True, value
        
        return False, None

    def process_expenses_csv(self, file_path):
        """Process expenses CSV file."""
        self.errors = []
        self.warnings = []
        valid_records = []
        
        required_columns = ['date', 'amount', 'vendor', 'department']
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Check required columns
                missing_cols = [col for col in required_columns if col not in reader.fieldnames]
                if missing_cols:
                    return {
                        'success': False,
                        'message': f"Missing required columns: {missing_cols}",
                        'records_processed': 0,
                        'errors': [f"Missing columns: {', '.join(missing_cols)}"]
                    }
                
                for row_num, row in enumerate(reader, start=2):
                    row_errors = []
                    
                    # Validate required fields
                    date_valid, expense_date = self.validate_date(row['date'])
                    if not date_valid:
                        row_errors.append(f"Invalid date: {row['date']}")
                    
                    amount_valid, amount = self.validate_amount(row['amount'])
                    if not amount_valid:
                        row_errors.append(f"Invalid amount: {row['amount']}")
                    
                    vendor = row['vendor'].strip() if row['vendor'] else ""
                    if not vendor:
                        row_errors.append("Vendor is required")
                    
                    dept_valid, department = self.validate_department(row['department'])
                    if not dept_valid:
                        row_errors.append(f"Invalid department: {row['department']}")
                    
                    # Handle category (auto-categorize if missing/invalid)
                    category = None
                    if 'category' in row and row['category']:
                        cat_valid, category = self.validate_category(row['category'])
                        if not cat_valid:
                            self.warnings.append(f"Row {row_num}: Invalid category '{row['category']}', will auto-categorize")
                            category = None
                    
                    if not category and vendor:
                        category = self.auto_categorize_expense(vendor, row.get('description', ''))
                        self.warnings.append(f"Row {row_num}: Auto-categorized as '{category}'")
                    
                    if row_errors:
                        self.errors.append(f"Row {row_num}: {'; '.join(row_errors)}")
                        continue
                    
                    # Create valid record
                    record = {
                        'date': expense_date.strftime('%Y-%m-%d'),
                        'amount': amount,
                        'vendor': vendor,
                        'description': row.get('description', '').strip(),
                        'department': department,
                        'category': category,
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    valid_records.append(record)
            
            # Save processed records to a new CSV file
            if valid_records:
                output_file = Path(file_path).parent / f"processed_{Path(file_path).name}"
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    fieldnames = ['date', 'amount', 'vendor', 'description', 'department', 'category', 'created_at']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(valid_records)
                
                print(f"✅ Processed data saved to: {output_file}")
            
            success = len(self.errors) == 0
            message = f"Successfully processed {len(valid_records)} records"
            if self.errors:
                message += f" with {len(self.errors)} errors"
            if self.warnings:
                message += f" and {len(self.warnings)} warnings"
            
            return {
                'success': success,
                'message': message,
                'records_processed': len(valid_records),
                'errors': self.errors[:10],
                'warnings': self.warnings[:10]
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"Error processing file: {str(e)}",
                'records_processed': 0,
                'errors': [str(e)]
            }

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Nsight AI Budgeting System - Data Ingestion CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Upload expenses command
    upload_parser = subparsers.add_parser('upload-expenses', help='Upload expenses from CSV')
    upload_parser.add_argument('file_path', help='Path to CSV file')
    
    # Templates command
    subparsers.add_parser('templates', help='Show CSV template formats')
    
    # Create samples command  
    subparsers.add_parser('create-samples', help='Create sample CSV files')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    processor = SimpleDataProcessor()
    
    if args.command == 'upload-expenses':
        file_path = Path(args.file_path)
        
        if not file_path.exists():
            print(f"❌ Error: File '{args.file_path}' not found.")
            return
        
        print(f"📁 Processing expense file: {args.file_path}")
        print("=" * 50)
        
        result = processor.process_expenses_csv(file_path)
        
        if result['success']:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ {result['message']}")
        
        print(f"📊 Records processed: {result['records_processed']}")
        
        if result['errors']:
            print(f"\n🚨 Errors ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"  • {error}")
        
        if 'warnings' in result and result['warnings']:
            print(f"\n⚠️  Warnings ({len(result['warnings'])}):")
            for warning in result['warnings']:
                print(f"  • {warning}")
    
    elif args.command == 'templates':
        print("📋 CSV Template Formats")
        print("=" * 50)
        print("\n💰 Expenses CSV Template:")
        print("Required columns: date, amount, vendor, department")
        print("Optional columns: description, category")
        print("Example:")
        print("date,amount,vendor,description,department,category")
        print("2024-01-15,1250.00,AWS,Cloud hosting costs,Engineering,IT Infrastructure")
        print("2024-01-16,750.50,Google Ads,Marketing campaign,Marketing,Marketing")
        print("\n📝 Notes:")
        print("• Date formats: YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY")
        print("• Amount can include $ and commas")
        print("• Category will be auto-assigned if missing")
        print("• Department abbreviations supported (Eng → Engineering)")
    
    elif args.command == 'create-samples':
        print("📁 Creating sample CSV file...")
        
        sample_data = [
            ["date", "amount", "vendor", "description", "department", "category"],
            ["2024-01-15", "1250.00", "AWS", "Cloud hosting costs", "Engineering", "IT Infrastructure"],
            ["2024-01-16", "750.50", "Google Ads", "Marketing campaign", "Marketing", "Marketing"],
            ["2024-01-17", "2500.00", "Dell Business", "Laptop purchase", "Engineering", "Equipment"],
            ["2024-01-18", "450.00", "Uber", "Business travel", "Sales", "Travel"],
            ["2024-01-19", "15000.00", "ADP Payroll", "Monthly payroll", "HR", "Personnel"]
        ]
        
        sample_file = Path("sample_expenses.csv")
        with open(sample_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(sample_data)
        
        print(f"✅ Created sample file: {sample_file}")
        print(f"\nTest it with:")
        print(f"  python data_ingestion_cli.py upload-expenses {sample_file}")

if __name__ == "__main__":
    main() 