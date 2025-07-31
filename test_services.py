"""Test script to check if backend and frontend services are running."""

import requests
import time
from urllib.parse import urljoin

def test_backend():
    """Test if FastAPI backend is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend (FastAPI) is running at http://localhost:8000")
            return True
        else:
            print(f"❌ Backend responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not responding (connection failed)")
        return False
    except requests.exceptions.Timeout:
        print("❌ Backend is not responding (timeout)")
        return False
    except Exception as e:
        print(f"❌ Backend test error: {e}")
        return False

def test_frontend():
    """Test if Streamlit frontend is running."""
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend (Streamlit) is running at http://localhost:8501")
            return True
        else:
            print(f"❌ Frontend responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Frontend is not responding (connection failed)")
        return False
    except requests.exceptions.Timeout:
        print("❌ Frontend is not responding (timeout)")
        return False
    except Exception as e:
        print(f"❌ Frontend test error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Nsight AI Budgeting System Services...")
    print("=" * 50)
    
    print("\n🔍 Testing Backend Service...")
    backend_ok = test_backend()
    
    print("\n🔍 Testing Frontend Service...")
    frontend_ok = test_frontend()
    
    print("\n" + "=" * 50)
    if backend_ok and frontend_ok:
        print("🎉 All services are running successfully!")
        print("\n📖 Access your budgeting system:")
        print("   • API Docs: http://localhost:8000/docs")
        print("   • Dashboard: http://localhost:8501")
    elif backend_ok:
        print("⚠️  Backend is running, but frontend needs attention")
    elif frontend_ok:
        print("⚠️  Frontend is running, but backend needs attention")
    else:
        print("🚨 Both services need attention - check the startup windows") 