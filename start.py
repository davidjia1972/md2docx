#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Starter script for Markdown to DOCX Converter
Checks dependencies and starts the application
"""

import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_pyside6():
    """Check PySide6 availability"""
    try:
        import PySide6
        print("✅ PySide6 is available")
        return True
    except ImportError:
        print("❌ PySide6 not found")
        print("   Install with: pip install -r requirements.txt")
        return False

def check_pandoc():
    """Check Pandoc availability"""
    try:
        result = subprocess.run(['pandoc', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ {version_line}")
            return True
        else:
            print("❌ Pandoc found but not working properly")
            return False
    except FileNotFoundError:
        print("❌ Pandoc not found")
        print("   Install from: https://pandoc.org/installing.html")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Pandoc check timeout")
        return False
    except Exception as e:
        print(f"❌ Error checking Pandoc: {e}")
        return False

def run_application():
    """Run the main application"""
    try:
        # Change to src directory and run main.py
        src_path = Path(__file__).parent / "src"
        sys.path.insert(0, str(src_path))
        
        from main import main
        return main()
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        return 1

def main():
    """Main function"""
    print("=" * 60)
    print("Markdown to DOCX Converter")
    print("=" * 60)
    print("Checking dependencies...\n")
    
    # Check all dependencies
    checks = [
        check_python_version(),
        check_pyside6(), 
        check_pandoc()
    ]
    
    print("\n" + "=" * 60)
    
    # 检查核心依赖（Python和PySide6）
    python_ok = checks[0]
    pyside6_ok = checks[1] 
    pandoc_ok = checks[2]
    
    if python_ok and pyside6_ok:
        if pandoc_ok:
            print("🎉 All dependencies available! Starting application...\n")
        else:
            print("⚠️  Pandoc not found, but starting application anyway...")
            print("   (The app will show installation instructions)\n")
        return run_application()
    else:
        print("❌ Critical dependencies missing. Cannot start application:")
        print("\n📝 Installation steps:")
        if not pyside6_ok:
            print("1. Install PySide6: pip install -r requirements.txt")
        if not pandoc_ok:
            print("2. Install Pandoc: https://pandoc.org/installing.html")
        print("3. Run again: python start.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())