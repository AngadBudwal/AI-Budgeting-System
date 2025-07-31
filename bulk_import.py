"""Bulk import data via API endpoint."""

import pandas as pd
import requests
import json

def bulk_import_via_api():
    """Import expenses via FastAPI endpoint."""
    print("🚀 Starting bulk import via API...")
    
    # Load CSV data
    try:
        df = pd.read_csv('data/expenses.csv')
        print(f"📊 Loaded {len(df)} expense records from CSV")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return
    
    # Import via API
    api_url = "http://localhost:8000/expenses"
    imported_count = 0
    
    for _, row in df.iterrows():
        try:
            expense_data = {
                "date": row['date'],
                "amount": float(row['amount']),
                "vendor": row['vendor'],
                "description": row.get('description', ''),
                "department": row['department'],
                "category": row.get('category', 'Other')
            }
            
            response = requests.post(api_url, json=expense_data, timeout=10)
            
            if response.status_code == 200:
                imported_count += 1
                if imported_count % 100 == 0:
                    print(f"   Imported {imported_count} expenses...")
            else:
                print(f"⚠️  API Error for {row['vendor']}: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️  Error importing {row.get('vendor', 'Unknown')}: {e}")
            continue
    
    print(f"✅ Successfully imported {imported_count} expenses via API!")
    
    # Verify via API
    try:
        stats_response = requests.get("http://localhost:8000/dashboard/stats", timeout=10)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"📈 Verification: {stats['total_expenses']} expenses, ${stats['total_spent']:,.2f} total")
        else:
            print("⚠️  Could not verify import")
    except Exception as e:
        print(f"⚠️  Verification error: {e}")

if __name__ == "__main__":
    bulk_import_via_api() 