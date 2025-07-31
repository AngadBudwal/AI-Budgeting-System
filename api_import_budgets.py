"""Import budget data via API endpoint."""

import requests
import csv
import json

def import_budgets_via_api():
    """Import budgets via FastAPI endpoint with duplicate detection."""
    print("💰 Starting budget import via API...")
    
    # Check existing budgets first
    try:
        existing_response = requests.get("http://localhost:8000/budgets?limit=1000", timeout=10)
        if existing_response.status_code == 200:
            existing_data = existing_response.json()
            existing_budgets = existing_data.get('budgets', [])
            
            # Create set of existing budget keys for duplicate checking
            existing_keys = set()
            for budget in existing_budgets:
                key = (
                    budget['department'],
                    budget['category'],
                    budget['period_start'],
                    budget['period_end'],
                    float(budget['allocated_amount'])
                )
                existing_keys.add(key)
            
            print(f"📋 Found {len(existing_budgets)} existing budgets in database")
        else:
            existing_keys = set()
            print("⚠️ Could not fetch existing budgets, proceeding anyway")
    except Exception as e:
        print(f"⚠️ Error checking existing budgets: {e}")
        existing_keys = set()
    
    # Load CSV data
    try:
        budgets = []
        with open('data/budgets.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                budgets.append(row)
        print(f"📊 Loaded {len(budgets)} budget records from CSV")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return
    
    # Import via API with duplicate checking
    api_url = "http://localhost:8000/budgets"
    imported_count = 0
    skipped_count = 0
    errors = 0
    
    for budget in budgets:
        try:
            budget_data = {
                "department": budget['department'],
                "category": budget['category'],
                "period_start": budget['period_start'],
                "period_end": budget['period_end'],
                "allocated_amount": float(budget['allocated_amount'])
            }
            
            # Check if this budget already exists
            budget_key = (
                budget['department'],
                budget['category'],
                budget['period_start'],
                budget['period_end'],
                float(budget['allocated_amount'])
            )
            
            if budget_key in existing_keys:
                skipped_count += 1
                continue  # Skip this duplicate
            
            response = requests.post(api_url, json=budget_data, timeout=10)
            
            if response.status_code == 200:
                imported_count += 1
                existing_keys.add(budget_key)  # Add to existing set to prevent duplicates within this import
                if imported_count % 50 == 0:
                    print(f"   Imported {imported_count} budgets...")
            else:
                errors += 1
                if errors <= 5:  # Show first 5 errors
                    print(f"⚠️  API Error for {budget['department']}-{budget['category']}: {response.status_code}")
                
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"⚠️  Error importing {budget.get('department', 'Unknown')}: {e}")
            continue
    
    print(f"✅ Successfully imported {imported_count} new budgets via API!")
    if skipped_count > 0:
        print(f"⏭️  Skipped {skipped_count} duplicate budgets")
    if errors > 0:
        print(f"⚠️  {errors} errors occurred during import")
    
    # Verify via API
    try:
        stats_response = requests.get("http://localhost:8000/dashboard/stats", timeout=10)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"📈 Verification: {stats['total_budgets']} budgets, ${stats['total_allocated']:,.2f} allocated")
            print(f"📊 Budget Utilization: {(stats['total_spent']/stats['total_allocated']*100):.1f}%" if stats['total_allocated'] > 0 else "📊 Budget Utilization: 0.0%")
        else:
            print("⚠️  Could not verify import")
    except Exception as e:
        print(f"⚠️  Verification error: {e}")

if __name__ == "__main__":
    import_budgets_via_api() 