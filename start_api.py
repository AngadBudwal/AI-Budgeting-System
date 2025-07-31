"""Startup script for Nsight AI Budgeting System API."""

import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = ['fastapi', 'uvicorn', 'pydantic']
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
    """Install FastAPI dependencies."""
    print("📦 Installing FastAPI dependencies...")
    try:
        # Install from requirements file
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements_api.txt'
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

def start_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = True):
    """Start the FastAPI server."""
    print(f"🚀 Starting Nsight AI Budgeting API server...")
    print(f"📍 Server will be available at: http://{host}:{port}")
    print(f"📖 API Documentation: http://{host}:{port}/docs")
    print(f"📝 Alternative docs: http://{host}:{port}/redoc")
    print("=" * 60)
    
    try:
        # Start with uvicorn
        subprocess.run([
            sys.executable, '-m', 'uvicorn',
            'src.api.main:app',
            '--host', host,
            '--port', str(port),
            '--reload' if reload else '--no-reload'
        ])
    except KeyboardInterrupt:
        print("\n\n⚠️  Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")

def main():
    """Main startup function."""
    print("🔥 Nsight AI Budgeting System API Startup")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("src/api/main.py").exists():
        print("❌ Error: src/api/main.py not found!")
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
                print("   pip install -r requirements_api.txt")
                return
        else:
            print("❌ Cannot start server without required dependencies.")
            print("Install them with: pip install -r requirements_api.txt")
            return
    
    print("\n🎯 All dependencies are ready!")
    
    # Get server configuration
    host = input("Enter host (default: 127.0.0.1): ").strip() or "127.0.0.1"
    port_input = input("Enter port (default: 8000): ").strip()
    port = int(port_input) if port_input else 8000
    
    reload_input = input("Enable auto-reload? (y/n, default: y): ").strip().lower()
    reload = reload_input not in ['n', 'no']
    
    # Start the server
    start_server(host, port, reload)

if __name__ == "__main__":
    main() 