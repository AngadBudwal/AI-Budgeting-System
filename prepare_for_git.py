#!/usr/bin/env python3
"""
Script to prepare the Nsight AI Budgeting System for Git repository upload.
This script cleans up files and ensures the project is ready for GitHub.
"""

import os
import shutil
from pathlib import Path

def clean_project():
    """Clean up files that shouldn't be in the Git repository."""
    print("🧹 Cleaning project for Git repository...")
    
    # Files and directories to remove
    cleanup_items = [
        # Database files (will be regenerated)
        "budgeting_system.db",
        "budgeting_system.db-journal",
        
        # Python cache
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".Python",
        
        # Environment files
        ".env",
        ".venv",
        "venv",
        "env",
        
        # IDE files
        ".vscode",
        ".idea",
        "*.swp",
        "*.swo",
        
        # OS files
        ".DS_Store",
        "Thumbs.db",
        
        # Logs
        "*.log",
        
        # Temporary files
        "temp",
        "tmp",
    ]
    
    removed_count = 0
    
    for item in cleanup_items:
        # Handle wildcards
        if "*" in item:
            import glob
            for file_path in glob.glob(item, recursive=True):
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"   Removed file: {file_path}")
                        removed_count += 1
                except Exception as e:
                    print(f"   Warning: Could not remove {file_path}: {e}")
        else:
            # Handle specific files/directories
            if os.path.exists(item):
                try:
                    if os.path.isfile(item):
                        os.remove(item)
                        print(f"   Removed file: {item}")
                    elif os.path.isdir(item):
                        shutil.rmtree(item)
                        print(f"   Removed directory: {item}")
                    removed_count += 1
                except Exception as e:
                    print(f"   Warning: Could not remove {item}: {e}")
    
    # Clean __pycache__ directories recursively
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                cache_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(cache_path)
                    print(f"   Removed cache: {cache_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"   Warning: Could not remove {cache_path}: {e}")
    
    print(f"✅ Cleanup completed! Removed {removed_count} items.")

def create_directory_structure():
    """Ensure required directories exist with .gitkeep files."""
    print("📁 Creating directory structure...")
    
    directories = [
        "uploads",
        "models", 
        "reports"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        gitkeep_path = os.path.join(directory, ".gitkeep")
        if not os.path.exists(gitkeep_path):
            with open(gitkeep_path, "w") as f:
                f.write(f"# This file ensures the {directory} directory is tracked in Git\n")
            print(f"   Created: {gitkeep_path}")
    
    print("✅ Directory structure ready!")

def verify_files():
    """Verify that all necessary files are present."""
    print("🔍 Verifying project files...")
    
    required_files = [
        "README.md",
        "requirements.txt", 
        ".gitignore",
        "SETUP.md",
        "LICENSE",
        "src/models.py",
        "src/database.py",
        "src/config.py",
        "dashboard/main.py",
        "migrate_currency.py",
        "test_services.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"   ✓ {file_path}")
    
    if missing_files:
        print("\n❌ Missing required files:")
        for file_path in missing_files:
            print(f"   ✗ {file_path}")
        return False
    else:
        print("✅ All required files present!")
        return True

def main():
    """Main function to prepare project for Git."""
    print("🚀 Preparing Nsight AI Budgeting System for GitHub upload...")
    print("=" * 60)
    
    # Change to project directory
    os.chdir(Path(__file__).parent)
    
    # Clean project
    clean_project()
    print()
    
    # Create directory structure
    create_directory_structure()
    print()
    
    # Verify files
    if verify_files():
        print()
        print("🎉 Project is ready for GitHub!")
        print()
        print("📋 Next steps:")
        print("1. Create a new repository on GitHub")
        print("2. Run the following commands:")
        print()
        print("   git init")
        print("   git add .")
        print('   git commit -m "Initial commit: Nsight AI Budgeting System with multi-currency support"')
        print("   git branch -M main")
        print("   git remote add origin https://github.com/yourusername/nsight-ai-budgeting-system.git")
        print("   git push -u origin main")
        print()
        print("🔗 Don't forget to update the repository URL in SETUP.md!")
    else:
        print()
        print("❌ Project is not ready. Please fix missing files first.")

if __name__ == "__main__":
    main() 