#!/usr/bin/env python3
"""Simple CSV viewer for Nsight AI Budgeting System data."""

import csv
import argparse
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

class CSVViewer:
    """Simple CSV data viewer and analyzer."""
    
    def __init__(self):
        pass
    
    def analyze_expenses(self, file_path):
        """Analyze expense CSV data and show summary."""
        if not Path(file_path).exists():
            print(f"❌ Error: File '{file_path}' not found.")
            return
        
        print(f"📊 Analyzing expense data: {file_path}")
        print("=" * 60)
        
        total_records = 0
        total_amount = 0
        dept_summary = defaultdict(lambda: {'count': 0, 'total': 0})
        category_summary = defaultdict(lambda: {'count': 0, 'total': 0})
        vendor_summary = defaultdict(lambda: {'count': 0, 'total': 0})
        monthly_summary = defaultdict(lambda: {'count': 0, 'total': 0})
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        amount = float(row['amount'])
                        department = row['department']
                        category = row.get('category', 'Unknown')
                        vendor = row['vendor']
                        date_str = row['date']
                        
                        # Extract month from date
                        try:
                            if '-' in date_str:
                                month = date_str[:7]  # YYYY-MM
                            else:
                                # Handle other date formats
                                month = "Unknown"
                        except:
                            month = "Unknown"
                        
                        total_records += 1
                        total_amount += amount
                        
                        # Department summary
                        dept_summary[department]['count'] += 1
                        dept_summary[department]['total'] += amount
                        
                        # Category summary
                        category_summary[category]['count'] += 1
                        category_summary[category]['total'] += amount
                        
                        # Vendor summary
                        vendor_summary[vendor]['count'] += 1
                        vendor_summary[vendor]['total'] += amount
                        
                        # Monthly summary
                        monthly_summary[month]['count'] += 1
                        monthly_summary[month]['total'] += amount
                        
                    except (ValueError, KeyError) as e:
                        continue  # Skip invalid rows
            
            # Display summary
            print(f"💰 Total Records: {total_records:,}")
            print(f"💵 Total Amount: ${total_amount:,.2f}")
            print(f"📈 Average per Transaction: ${total_amount/total_records:.2f}" if total_records > 0 else "")
            
            # Department breakdown
            print(f"\n📊 Department Breakdown:")
            sorted_depts = sorted(dept_summary.items(), key=lambda x: x[1]['total'], reverse=True)
            for dept, data in sorted_depts:
                percentage = (data['total'] / total_amount * 100) if total_amount > 0 else 0
                print(f"  {dept:15} {data['count']:4} transactions  ${data['total']:10,.2f}  ({percentage:5.1f}%)")
            
            # Category breakdown
            print(f"\n📈 Category Breakdown:")
            sorted_cats = sorted(category_summary.items(), key=lambda x: x[1]['total'], reverse=True)
            for category, data in sorted_cats:
                percentage = (data['total'] / total_amount * 100) if total_amount > 0 else 0
                print(f"  {category:20} {data['count']:4} transactions  ${data['total']:10,.2f}  ({percentage:5.1f}%)")
            
            # Top vendors
            print(f"\n🏢 Top 15 Vendors by Spending:")
            sorted_vendors = sorted(vendor_summary.items(), key=lambda x: x[1]['total'], reverse=True)
            for i, (vendor, data) in enumerate(sorted_vendors[:15], 1):
                print(f"  {i:2}. {vendor:25} {data['count']:3} transactions  ${data['total']:10,.2f}")
            
            # Monthly trends (if we have date data)
            if monthly_summary and len(monthly_summary) > 1:
                print(f"\n📅 Monthly Spending Trends:")
                sorted_months = sorted(monthly_summary.items())
                for month, data in sorted_months:
                    if month != "Unknown":
                        print(f"  {month}  {data['count']:4} transactions  ${data['total']:10,.2f}")
        
        except Exception as e:
            print(f"❌ Error analyzing file: {e}")
    
    def compare_files(self, file1, file2):
        """Compare two expense CSV files."""
        print(f"🔄 Comparing expense files:")
        print(f"  File 1: {file1}")
        print(f"  File 2: {file2}")
        print("=" * 60)
        
        def get_file_stats(file_path):
            total = 0
            count = 0
            depts = set()
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            total += float(row['amount'])
                            count += 1
                            depts.add(row['department'])
                        except:
                            continue
            except:
                return 0, 0, set()
            
            return total, count, depts
        
        total1, count1, depts1 = get_file_stats(file1)
        total2, count2, depts2 = get_file_stats(file2)
        
        print(f"📊 File 1: {count1:,} records, ${total1:,.2f} total")
        print(f"📊 File 2: {count2:,} records, ${total2:,.2f} total")
        print(f"📈 Difference: {count2-count1:+,} records, ${total2-total1:+,.2f}")
        
        if depts1 and depts2:
            print(f"🏢 Departments File 1: {', '.join(sorted(depts1))}")
            print(f"🏢 Departments File 2: {', '.join(sorted(depts2))}")
            new_depts = depts2 - depts1
            if new_depts:
                print(f"✨ New departments in File 2: {', '.join(sorted(new_depts))}")
    
    def show_sample_records(self, file_path, count=10):
        """Show sample records from the CSV file."""
        if not Path(file_path).exists():
            print(f"❌ Error: File '{file_path}' not found.")
            return
        
        print(f"📋 Sample records from: {file_path}")
        print("=" * 60)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for i, row in enumerate(reader):
                    if i >= count:
                        break
                    
                    print(f"Record {i+1}:")
                    for key, value in row.items():
                        print(f"  {key:12}: {value}")
                    print()
        
        except Exception as e:
            print(f"❌ Error reading file: {e}")

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="CSV Viewer for Nsight AI Budgeting System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze expense CSV file')
    analyze_parser.add_argument('file_path', help='Path to CSV file')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare two CSV files')
    compare_parser.add_argument('file1', help='First CSV file')
    compare_parser.add_argument('file2', help='Second CSV file')
    
    # Sample command
    sample_parser = subparsers.add_parser('sample', help='Show sample records')
    sample_parser.add_argument('file_path', help='Path to CSV file')
    sample_parser.add_argument('--count', type=int, default=5, help='Number of records to show')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    viewer = CSVViewer()
    
    try:
        if args.command == 'analyze':
            viewer.analyze_expenses(args.file_path)
        elif args.command == 'compare':
            viewer.compare_files(args.file1, args.file2)
        elif args.command == 'sample':
            viewer.show_sample_records(args.file_path, args.count)
    
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 