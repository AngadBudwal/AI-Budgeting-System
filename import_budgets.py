"""Import budget data from CSV to database."""

import sys
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, 'src')

from services.data_processor import DataProcessor
from database import init_db

def import_budgets():
    """Import budgets from CSV to database."""
    print("💰 Starting budget import...")
    
    # Initialize database
    init_db()
    print("✅ Database initialized")
    
    # Check if budget file exists
    budget_file = Path('data/budgets.csv')
    if not budget_file.exists():
        print(f"❌ Budget file not found: {budget_file}")
        return
    
    print(f"📊 Found budget file: {budget_file}")
    
    # Initialize data processor
    processor = DataProcessor()
    
    # Process budget CSV
    print("🔄 Processing budget data...")
    result = processor.process_budget_csv(budget_file)
    
    # Display results
    if result.success:
        print(f"✅ {result.message}")
        print(f"📊 Successfully imported {result.records_processed} budget records!")
    else:
        print(f"❌ Import failed: {result.message}")
        if result.errors:
            print("🚨 Errors:")
            for error in result.errors[:5]:  # Show first 5 errors
                print(f"  • {error}")
    
    # Verify import with summary
    print("\n📈 Verifying import...")
    summary = processor.get_data_summary()
    
    if 'error' not in summary:
        print(f"✅ Database now contains:")
        print(f"  💰 Expenses: {summary['total_expenses']:,} records (${summary['total_spent']:,.2f})")
        print(f"  🎯 Budgets: {summary['total_budgets']:,} records (${summary['total_allocated']:,.2f})")
        
        if summary['total_budgets'] > 0:
            utilization = (summary['total_spent'] / summary['total_allocated'] * 100) if summary['total_allocated'] > 0 else 0
            print(f"  📊 Budget Utilization: {utilization:.1f}%")
    else:
        print(f"⚠️  Could not verify: {summary['error']}")

if __name__ == "__main__":
    import_budgets() 