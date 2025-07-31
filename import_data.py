"""Script to import CSV data into the database."""

import pandas as pd
import sys
sys.path.append('src')

from services.data_processor import DataProcessor
from database import init_db

def import_expenses():
    """Import expenses from CSV to database."""
    print("🚀 Starting data import...")
    
    # Initialize database
    init_db()
    print("✅ Database initialized")
    
    # Load CSV data
    try:
        df = pd.read_csv('data/expenses.csv')
        print(f"📊 Loaded {len(df)} expense records from CSV")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return
    
    # Initialize data processor
    processor = DataProcessor()
    
    # Import each expense
    imported_count = 0
    for _, row in df.iterrows():
        try:
            # Pass arguments individually as required by the method signature
            result = processor.add_expense(
                date=row['date'],
                amount=float(row['amount']),
                vendor=row['vendor'],
                description=row.get('description', ''),
                department=row['department'],
                category=row.get('category', 'Other')
            )
            
            if 'error' not in result:
                imported_count += 1
            
            if imported_count % 100 == 0:
                print(f"   Imported {imported_count} expenses...")
                
        except Exception as e:
            print(f"⚠️  Error importing expense {row.get('vendor', 'Unknown')}: {e}")
            continue
    
    print(f"✅ Successfully imported {imported_count} expenses!")
    
    # Verify import
    summary = processor.get_data_summary()
    print(f"📈 Database now contains: {summary['total_expenses']} expenses, ${summary['total_spent']:,.2f} total")

if __name__ == "__main__":
    import_expenses() 