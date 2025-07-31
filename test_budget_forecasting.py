#!/usr/bin/env python3
"""Test script for budget forecasting functionality - zero dependencies! 📈"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from src.ml.budget_forecaster import BudgetForecaster
    print("✅ Budget forecaster imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_spending_analysis():
    """Test spending pattern analysis."""
    print("\n📊 Testing Spending Pattern Analysis...")
    
    data_file = "data/expenses.csv"
    if not Path(data_file).exists():
        print(f"❌ Test data not found: {data_file}")
        print("Run data generation first!")
        return False
    
    try:
        forecaster = BudgetForecaster()
        
        # Load and analyze data
        print(f"📚 Loading data from: {data_file}")
        if not forecaster.load_historical_data(data_file):
            print("❌ Failed to load data")
            return False
        
        # Analyze patterns
        print("🔍 Analyzing spending patterns...")
        analysis = forecaster.analyze_spending_patterns()
        
        if 'error' in analysis:
            print(f"❌ Analysis failed: {analysis['error']}")
            return False
        
        # Display results
        print("✅ Analysis Results:")
        print(f"  📅 Months analyzed: {analysis['total_months']}")
        print(f"  💰 Total spending: ${analysis['total_spending']:,.0f}")
        print(f"  📊 Average monthly: ${analysis['average_monthly']:,.0f}")
        print(f"  📈 Recent average: ${analysis['recent_average']:,.0f}")
        print(f"  📈 Growth rate: {analysis['growth_rate']:+.1f}%")
        print(f"  🏷️  Categories: {analysis['categories_analyzed']}")
        print(f"  🏢 Departments: {analysis['departments_analyzed']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False

def test_spending_forecast():
    """Test spending forecasting."""
    print("\n🔮 Testing Spending Forecasting...")
    
    data_file = "data/expenses.csv"
    if not Path(data_file).exists():
        print(f"❌ Test data not found: {data_file}")
        return False
    
    try:
        forecaster = BudgetForecaster()
        
        # Load and analyze data
        if not forecaster.load_historical_data(data_file):
            print("❌ Failed to load data")
            return False
        
        forecaster.analyze_spending_patterns()
        
        # Generate 6-month forecast
        print("🔮 Generating 6-month forecast...")
        forecast = forecaster.forecast_spending(6)
        
        if 'error' in forecast:
            print(f"❌ Forecast failed: {forecast['error']}")
            return False
        
        # Display forecast results
        print("✅ Forecast Results:")
        print(f"  📅 Forecast period: {forecast['forecast_period']} months")
        print(f"  💰 Total forecasted: ${forecast['total_forecasted']:,.0f}")
        
        print("\n📅 Monthly Forecasts:")
        for monthly in forecast['monthly_forecasts'][:3]:  # Show first 3 months
            month = monthly['month']
            predicted = monthly['predicted_amount']
            lower = monthly['confidence_lower']
            upper = monthly['confidence_upper']
            print(f"  • {month}: ${predicted:,.0f} (${lower:,.0f} - ${upper:,.0f})")
        
        if len(forecast['monthly_forecasts']) > 3:
            print(f"  ... and {len(forecast['monthly_forecasts']) - 3} more months")
        
        # Show top categories
        if forecast.get('category_forecasts'):
            print("\n📊 Top Category Forecasts:")
            cat_sorted = sorted(forecast['category_forecasts'].items(), 
                              key=lambda x: x[1]['total_forecast'], reverse=True)[:3]
            
            for category, cat_data in cat_sorted:
                trend_icon = "📈" if cat_data['trend'] == 'increasing' else "📉" if cat_data['trend'] == 'decreasing' else "➡️"
                print(f"  {trend_icon} {category}: ${cat_data['total_forecast']:,.0f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Forecast failed: {e}")
        return False

def test_budget_variance():
    """Test budget variance analysis."""
    print("\n💰 Testing Budget Variance Analysis...")
    
    expenses_file = "data/expenses.csv"
    budgets_file = "data/budgets.csv"
    
    if not Path(expenses_file).exists():
        print(f"❌ Expenses data not found: {expenses_file}")
        return False
    
    if not Path(budgets_file).exists():
        print(f"❌ Budget data not found: {budgets_file}")
        return False
    
    try:
        forecaster = BudgetForecaster()
        
        # Load expense data
        if not forecaster.load_historical_data(expenses_file):
            print("❌ Failed to load expense data")
            return False
        
        # Analyze variance
        print("🔍 Analyzing budget variance...")
        variance = forecaster.analyze_budget_variance(budgets_file)
        
        if 'error' in variance:
            print(f"❌ Variance analysis failed: {variance['error']}")
            return False
        
        # Display results
        print("✅ Budget Variance Results:")
        print(f"  🎯 Total budgeted: ${variance['total_budgeted']:,.0f}")
        print(f"  💰 Total actual: ${variance['total_actual']:,.0f}")
        print(f"  📊 Total variance: ${variance['total_variance']:+,.0f}")
        print(f"  📈 Variance %: {variance['total_variance_percent']:+.1f}%")
        print(f"  🔴 Over budget: {variance['over_budget_items']} items")
        print(f"  🟢 Under budget: {variance['under_budget_items']} items")
        
        # Show top variances
        print("\n📋 Largest Variances:")
        for item in variance['line_items'][:5]:  # Top 5
            status_icon = "🔴" if item['status'] == 'over_budget' else "🟢"
            print(f"  {status_icon} {item['department']} - {item['category']}: "
                  f"${item['variance']:+,.0f} ({item['variance_percent']:+.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ Variance analysis failed: {e}")
        return False

def test_insights_generation():
    """Test insights generation."""
    print("\n💡 Testing Insights Generation...")
    
    data_file = "data/expenses.csv"
    if not Path(data_file).exists():
        print(f"❌ Test data not found: {data_file}")
        return False
    
    try:
        forecaster = BudgetForecaster()
        
        # Load and analyze data
        if not forecaster.load_historical_data(data_file):
            print("❌ Failed to load data")
            return False
        
        forecaster.analyze_spending_patterns()
        
        # Generate insights
        print("🧠 Generating insights...")
        insights = forecaster.get_insights()
        
        if 'error' in insights:
            print(f"❌ Insights failed: {insights['error']}")
            return False
        
        # Display insights
        if insights.get('insights'):
            print(f"✅ Generated {len(insights['insights'])} insights:")
            for insight in insights['insights']:
                icon = "⚠️" if insight['type'] == 'warning' else "✅" if insight['type'] == 'positive' else "ℹ️"
                print(f"  {icon} {insight['title']}: {insight['message']}")
        else:
            print("✅ No specific insights found (normal for well-balanced spending)")
        
        return True
        
    except Exception as e:
        print(f"❌ Insights generation failed: {e}")
        return False

def main():
    """Run all forecasting tests."""
    print("🧪 Testing Nsight AI Budget Forecasting System")
    print("=" * 60)
    
    tests = [
        ("Spending Analysis", test_spending_analysis),
        ("Spending Forecast", test_spending_forecast),
        ("Budget Variance", test_budget_variance),
        ("Insights Generation", test_insights_generation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  • {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All budget forecasting tests PASSED!")
        print("💡 The forecasting system is fully operational!")
        
        print(f"\n🚀 Ready to use:")
        print(f"  • py -m src.cli analyze-trends")
        print(f"  • py -m src.cli forecast 6")
        print(f"  • py -m src.cli budget-variance")
        
    else:
        print("⚠️  Some tests failed - check data files and try again")

if __name__ == "__main__":
    main() 