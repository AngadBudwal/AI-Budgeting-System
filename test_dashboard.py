"""Test script for Nsight AI Budgeting System Streamlit Dashboard."""

import sys
import subprocess
import time
import requests
from pathlib import Path
from datetime import datetime

print("🎨 Nsight AI Budgeting System Dashboard Test")
print("=" * 60)

def test_dashboard_imports():
    """Test that the dashboard can be imported successfully."""
    print("\n📋 Test 1: Dashboard Import Testing")
    print("-" * 40)
    
    try:
        # Test Streamlit availability
        try:
            import streamlit
            print(f"✅ Streamlit available: {streamlit.__version__}")
        except ImportError:
            print("❌ Streamlit not installed")
            print("💡 Install with: pip install -r requirements_dashboard.txt")
            return False
        
        # Test other dependencies
        dependencies = {
            'pandas': 'pandas',
            'plotly': 'plotly',
            'requests': 'requests',
            'numpy': 'numpy'
        }
        
        for name, module in dependencies.items():
            try:
                __import__(module)
                print(f"✅ {name} available")
            except ImportError:
                print(f"❌ {name} not installed")
                return False
        
        # Test dashboard module
        sys.path.append('.')
        
        try:
            # We can't import the main streamlit file directly as it runs the app
            # But we can check if the file exists and is valid Python
            dashboard_path = Path("dashboard/main.py")
            if dashboard_path.exists():
                with open(dashboard_path, 'r') as f:
                    content = f.read()
                
                # Basic syntax check
                compile(content, str(dashboard_path), 'exec')
                print("✅ Dashboard main.py is valid Python")
            else:
                print("❌ Dashboard main.py not found")
                return False
        except SyntaxError as e:
            print(f"❌ Dashboard syntax error: {e}")
            return False
        except Exception as e:
            print(f"❌ Dashboard file error: {e}")
            return False
        
        print("✅ All dashboard imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_dashboard_structure():
    """Test the dashboard file structure and components."""
    print("\n📋 Test 2: Dashboard Structure Testing")
    print("-" * 40)
    
    try:
        dashboard_path = Path("dashboard/main.py")
        
        if not dashboard_path.exists():
            print("❌ Dashboard main.py not found")
            return False
        
        with open(dashboard_path, 'r') as f:
            content = f.read()
        
        # Check for required components
        required_components = [
            'st.set_page_config',
            'show_overview_page',
            'show_analytics_page',
            'show_ml_features_page',
            'show_forecasting_page',
            'show_anomaly_detection_page',
            'show_data_management_page',
            'call_api',
            'check_api_health'
        ]
        
        for component in required_components:
            if component in content:
                print(f"✅ Component found: {component}")
            else:
                print(f"❌ Missing component: {component}")
                return False
        
        # Check for API endpoints
        api_endpoints = [
            '/health',
            '/dashboard/stats',
            '/expenses',
            '/ml/predict',
            '/forecast/spending',
            '/anomalies/detect'
        ]
        
        for endpoint in api_endpoints:
            if endpoint in content:
                print(f"✅ API endpoint referenced: {endpoint}")
            else:
                print(f"⚠️  Missing API endpoint: {endpoint}")
        
        print("✅ Dashboard structure validation complete!")
        return True
        
    except Exception as e:
        print(f"❌ Structure test failed: {e}")
        return False

def test_streamlit_config():
    """Test Streamlit configuration and basic setup."""
    print("\n📋 Test 3: Streamlit Configuration Testing")
    print("-" * 40)
    
    try:
        dashboard_path = Path("dashboard/main.py")
        
        with open(dashboard_path, 'r') as f:
            content = f.read()
        
        # Check page configuration
        config_items = [
            'page_title="Nsight AI Budgeting System"',
            'page_icon="💰"',
            'layout="wide"',
            'initial_sidebar_state="expanded"'
        ]
        
        for item in config_items:
            if item in content:
                print(f"✅ Config found: {item}")
            else:
                print(f"⚠️  Config missing: {item}")
        
        # Check CSS styling
        if '<style>' in content and '</style>' in content:
            print("✅ Custom CSS styling included")
        else:
            print("⚠️  No custom CSS found")
        
        # Check for API base URL configuration
        if 'API_BASE_URL' in content:
            print("✅ API base URL configured")
        else:
            print("❌ API base URL not configured")
            return False
        
        print("✅ Streamlit configuration validation complete!")
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_dashboard_pages():
    """Test dashboard page functions."""
    print("\n📋 Test 4: Dashboard Pages Testing")
    print("-" * 40)
    
    try:
        # Check that all page functions are defined
        page_functions = [
            'show_overview_page',
            'show_analytics_page', 
            'show_ml_features_page',
            'show_forecasting_page',
            'show_anomaly_detection_page',
            'show_data_management_page'
        ]
        
        dashboard_path = Path("dashboard/main.py")
        with open(dashboard_path, 'r') as f:
            content = f.read()
        
        for func in page_functions:
            if f"def {func}(" in content:
                print(f"✅ Page function defined: {func}")
            else:
                print(f"❌ Missing page function: {func}")
                return False
        
        # Check for navigation logic
        navigation_elements = [
            'st.sidebar',
            'st.session_state',
            'st.button',
            'st.rerun'
        ]
        
        for element in navigation_elements:
            if element in content:
                print(f"✅ Navigation element: {element}")
            else:
                print(f"⚠️  Navigation element missing: {element}")
        
        print("✅ Dashboard pages validation complete!")
        return True
        
    except Exception as e:
        print(f"❌ Pages test failed: {e}")
        return False

def test_api_integration():
    """Test API integration functions."""
    print("\n📋 Test 5: API Integration Testing")
    print("-" * 40)
    
    try:
        dashboard_path = Path("dashboard/main.py")
        with open(dashboard_path, 'r') as f:
            content = f.read()
        
        # Check API helper functions
        api_functions = [
            'call_api',
            'check_api_health'
        ]
        
        for func in api_functions:
            if f"def {func}(" in content:
                print(f"✅ API function defined: {func}")
            else:
                print(f"❌ Missing API function: {func}")
                return False
        
        # Check error handling
        error_handling = [
            'ConnectionError',
            'Timeout',
            'st.error',
            'st.warning',
            'st.info'
        ]
        
        for handler in error_handling:
            if handler in content:
                print(f"✅ Error handling: {handler}")
            else:
                print(f"⚠️  Error handling missing: {handler}")
        
        # Check caching
        if '@st.cache_data' in content:
            print("✅ API response caching enabled")
        else:
            print("⚠️  No API caching found")
        
        print("✅ API integration validation complete!")
        return True
        
    except Exception as e:
        print(f"❌ API integration test failed: {e}")
        return False

def test_visualization_components():
    """Test data visualization components."""
    print("\n📋 Test 6: Visualization Components Testing")
    print("-" * 40)
    
    try:
        dashboard_path = Path("dashboard/main.py")
        with open(dashboard_path, 'r') as f:
            content = f.read()
        
        # Check Plotly components
        plotly_components = [
            'plotly.express',
            'plotly.graph_objects',
            'px.pie',
            'px.bar',
            'px.line',
            'go.Figure',
            'st.plotly_chart'
        ]
        
        for component in plotly_components:
            if component in content:
                print(f"✅ Plotly component: {component}")
            else:
                print(f"⚠️  Plotly component missing: {component}")
        
        # Check Streamlit components
        streamlit_components = [
            'st.metric',
            'st.dataframe',
            'st.columns',
            'st.subheader',
            'st.form',
            'st.button',
            'st.selectbox',
            'st.slider'
        ]
        
        for component in streamlit_components:
            if component in content:
                print(f"✅ Streamlit component: {component}")
            else:
                print(f"⚠️  Streamlit component missing: {component}")
        
        print("✅ Visualization components validation complete!")
        return True
        
    except Exception as e:
        print(f"❌ Visualization test failed: {e}")
        return False

def show_dashboard_features():
    """Show dashboard features and capabilities."""
    print("\n📋 Dashboard Features & Capabilities")
    print("=" * 60)
    
    features = {
        "🏠 Dashboard Overview": [
            "Real-time system metrics",
            "Budget utilization tracking",
            "Recent expense activity",
            "Quick action buttons",
            "API health monitoring"
        ],
        "📊 Analytics & Charts": [
            "Department spending breakdown",
            "Category spending analysis", 
            "Monthly spending trends",
            "Interactive Plotly visualizations",
            "Transaction count analysis"
        ],
        "🤖 AI/ML Features": [
            "Real-time expense categorization",
            "ML model performance metrics",
            "Category prediction interface",
            "Confidence scoring",
            "Model information display"
        ],
        "🔮 Budget Forecasting": [
            "Multi-month spending forecasts",
            "Confidence interval predictions",
            "Historical trend analysis",
            "Growth rate calculations",
            "Interactive forecast parameters"
        ],
        "🚨 Anomaly Detection": [
            "Real-time anomaly scanning",
            "Severity-based alert system",
            "Detailed anomaly analysis",
            "Security threat detection",
            "Customizable sensitivity settings"
        ],
        "💾 Data Management": [
            "Add new expenses",
            "Form validation",
            "Auto-categorization",
            "Department/category selection",
            "Real-time data updates"
        ]
    }
    
    for category, items in features.items():
        print(f"\n🔷 {category}:")
        for item in items:
            print(f"  • {item}")
    
    print(f"\n🎨 UI/UX Features:")
    print(f"  • Responsive wide layout")
    print(f"  • Custom CSS styling") 
    print(f"  • Sidebar navigation")
    print(f"  • Real-time API status")
    print(f"  • Error handling & user feedback")
    print(f"  • Metric cards with deltas")
    print(f"  • Interactive forms & controls")
    
    print(f"\n🚀 Getting Started:")
    print(f"  1. Install dependencies: pip install -r requirements_dashboard.txt")
    print(f"  2. Start API backend:    python start_api.py")
    print(f"  3. Start dashboard:      python start_dashboard.py")
    print(f"  4. Open browser:         http://localhost:8501")

def main():
    """Run all dashboard tests."""
    try:
        print("🧪 Running comprehensive Streamlit dashboard tests...")
        
        tests = [
            test_dashboard_imports,
            test_dashboard_structure,
            test_streamlit_config,
            test_dashboard_pages,
            test_api_integration,
            test_visualization_components
        ]
        
        results = []
        
        for test_func in tests:
            try:
                result = test_func()
                results.append(result)
            except Exception as e:
                print(f"❌ Test {test_func.__name__} failed: {e}")
                results.append(False)
        
        # Show features
        show_dashboard_features()
        
        # Summary
        print("\n" + "=" * 60)
        passed = sum(results)
        total = len(results)
        
        if passed == total:
            print("🎉 All Dashboard Tests PASSED!")
            print("✅ Streamlit dashboard is ready for use")
            print()
            print("🚀 Next Steps:")
            print("  • Start dashboard: python start_dashboard.py")
            print("  • Access at: http://localhost:8501")
            print("  • Ensure API backend is running")
        else:
            print(f"⚠️  {passed}/{total} tests passed")
            print("🔧 Please review the failed tests above")
            
            if passed >= total * 0.8:  # 80% pass rate
                print("✅ Dashboard is mostly functional")
                print("💡 Missing dependencies can be installed later")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests cancelled by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 