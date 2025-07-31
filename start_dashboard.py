"""Startup script for Nsight AI Budgeting System Streamlit Dashboard."""

import sys
import subprocess
import time
import requests
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = ['streamlit', 'pandas', 'plotly', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    return missing_packages

def install_dependencies():
    """Install Streamlit dashboard dependencies."""
    print("📦 Installing Streamlit dashboard dependencies...")
    try:
        # Install from requirements file
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements_dashboard.txt'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully!")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_api_backend():
    """Check if the FastAPI backend is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ FastAPI backend is running")
            return True
        else:
            print("❌ FastAPI backend responded with error")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ FastAPI backend is not running")
        return False
    except Exception as e:
        print(f"❌ Error checking backend: {e}")
        return False

def start_dashboard(port: int = 8501):
    """Start the Streamlit dashboard."""
    print(f"🚀 Starting Nsight AI Budgeting Dashboard...")
    print(f"📍 Dashboard will be available at: http://localhost:{port}")
    print("=" * 60)
    
    try:
        # Start Streamlit
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run',
            'dashboard/main.py',
            '--server.port', str(port),
            '--server.headless', 'false',
            '--browser.gatherUsageStats', 'false'
        ])
    except KeyboardInterrupt:
        print("\n\n⚠️  Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting dashboard: {e}")

def main():
    """Main startup function."""
    print("🎨 Nsight AI Budgeting System Dashboard Startup")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("dashboard/main.py").exists():
        print("❌ Error: dashboard/main.py not found!")
        print("Please run this script from the project root directory.")
        return
    
    # Check dependencies
    missing = check_dependencies()
    
    if missing:
        print(f"\n📦 Missing dependencies: {', '.join(missing)}")
        
        response = input("\nWould you like to install them now? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            if not install_dependencies():
                print("❌ Failed to install dependencies. Please install manually:")
                print("   pip install -r requirements_dashboard.txt")
                return
        else:
            print("❌ Cannot start dashboard without required dependencies.")
            print("Install them with: pip install -r requirements_dashboard.txt")
            return
    
    print("\n🎯 All dependencies are ready!")
    
    # Check backend status
    print("\n🔌 Checking FastAPI backend status...")
    if not check_api_backend():
        print("\n⚠️  FastAPI backend is not running!")
        print("The dashboard will work but with limited functionality.")
        print("\n💡 To start the backend:")
        print("   1. Open a new terminal")
        print("   2. Run: python start_api.py")
        print("   3. Keep both running for full functionality")
        
        response = input("\nContinue with dashboard anyway? (y/n): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Please start the backend first, then try again.")
            return
    
    # Get dashboard configuration
    port_input = input("\nEnter dashboard port (default: 8501): ").strip()
    port = int(port_input) if port_input else 8501
    
    print(f"\n🎨 Starting dashboard on port {port}...")
    print("💡 The dashboard will open automatically in your browser")
    print("🔄 To stop: Press Ctrl+C in this terminal")
    
    # Start the dashboard
    start_dashboard(port)

if __name__ == "__main__":
    main() 