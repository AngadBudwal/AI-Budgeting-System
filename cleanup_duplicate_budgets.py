"""Clean up duplicate budget entries in the database."""

import requests
import json

def cleanup_duplicate_budgets():
    """Remove duplicate budget entries via API."""
    print("🧹 Starting budget cleanup process...")
    
    try:
        # Get all budgets from API
        response = requests.get("http://localhost:8000/budgets?limit=1000", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch budgets: {response.status_code}")
            return
        
        budgets_data = response.json()
        budgets = budgets_data.get('budgets', [])
        print(f"📊 Found {len(budgets)} total budget records")
        
        # Group budgets by unique combination of fields (excluding id and created_at)
        unique_budgets = {}
        duplicates_to_delete = []
        
        for budget in budgets:
            # Create unique key based on business fields
            key = (
                budget['department'],
                budget['category'], 
                budget['period_start'],
                budget['period_end'],
                float(budget['allocated_amount'])
            )
            
            if key in unique_budgets:
                # This is a duplicate - mark for deletion (keep the first one)
                duplicates_to_delete.append(budget['id'])
                print(f"   Duplicate found: {budget['department']} - {budget['category']} - ${budget['allocated_amount']}")
            else:
                # This is the first occurrence - keep it
                unique_budgets[key] = budget
        
        print(f"✅ Identified {len(unique_budgets)} unique budgets")
        print(f"🗑️  Found {len(duplicates_to_delete)} duplicates to remove")
        
        if duplicates_to_delete:
            print("⚠️  Note: Manual deletion via API endpoints not implemented")
            print("🔧 Recommendation: Use database tool to delete duplicates by ID")
            print("📋 Duplicate IDs to delete:")
            for dup_id in duplicates_to_delete:
                print(f"   - ID: {dup_id}")
        else:
            print("✅ No duplicates found!")
        
        print(f"📈 Final count should be: {len(unique_budgets)} budgets")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    cleanup_duplicate_budgets() 