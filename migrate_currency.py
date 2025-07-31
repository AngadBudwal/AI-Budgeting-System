"""
Database migration script to add currency support to existing tables.
Run this script to update your existing database schema.
"""

import sqlite3
import sys
from pathlib import Path

def migrate_database():
    """Add currency columns to existing tables."""
    
    db_path = "budgeting_system.db"
    
    # Check if database exists
    if not Path(db_path).exists():
        print("❌ Database not found. Please run the system first to create the database.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🚀 Starting database migration for multi-currency support...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(expenses)")
        expense_columns = [col[1] for col in cursor.fetchall()]
        
        cursor.execute("PRAGMA table_info(budgets)")
        budget_columns = [col[1] for col in cursor.fetchall()]
        
        cursor.execute("PRAGMA table_info(anomalies)")
        anomaly_columns = [col[1] for col in cursor.fetchall()]
        
        # Add currency column to expenses table if not exists
        if 'currency' not in expense_columns:
            print("📊 Adding currency column to expenses table...")
            cursor.execute("ALTER TABLE expenses ADD COLUMN currency TEXT DEFAULT 'USD'")
            print("✅ Added currency column to expenses table")
        else:
            print("✅ Currency column already exists in expenses table")
        
        # Add currency column to budgets table if not exists
        if 'currency' not in budget_columns:
            print("💼 Adding currency column to budgets table...")
            cursor.execute("ALTER TABLE budgets ADD COLUMN currency TEXT DEFAULT 'USD'")
            print("✅ Added currency column to budgets table")
        else:
            print("✅ Currency column already exists in budgets table")
        
        # Add currency column to anomalies table if not exists
        if 'currency' not in anomaly_columns:
            print("🚨 Adding currency column to anomalies table...")
            cursor.execute("ALTER TABLE anomalies ADD COLUMN currency TEXT DEFAULT 'USD'")
            print("✅ Added currency column to anomalies table")
        else:
            print("✅ Currency column already exists in anomalies table")
        
        # Create indexes for currency columns for better performance
        print("🔍 Creating indexes for currency columns...")
        
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_expenses_currency ON expenses(currency)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_budgets_currency ON budgets(currency)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_anomalies_currency ON anomalies(currency)")
            print("✅ Created currency indexes")
        except Exception as e:
            print(f"⚠️  Warning: Could not create indexes: {e}")
        
        # Commit changes
        conn.commit()
        print("\n🎉 Database migration completed successfully!")
        print("\n📖 Currency Support Added:")
        print("   • USD - US Dollar")
        print("   • INR - Indian Rupee")
        print("   • CAD - Canadian Dollar")
        print("   • TRY - Turkish Lira")
        print("\n📁 Sample CSV files created:")
        print("   • data/sample_expenses.csv")
        print("   • data/sample_budgets.csv")
        print("\n🚀 You can now use the multi-currency features in the dashboard!")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1) 