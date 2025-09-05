#!/usr/bin/env python3
"""
跨平台构建脚本

Usage:
    python build.py [platform]
    
    platform: macos, windows, linux, all
    如果不指定平台，将构建当前平台版本
"""

import sys
import platform
import subprocess
import os
from pathlib import Path

def get_current_platform():
    """获取当前平台名称"""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows" 
    elif system == "linux":
        return "linux"
    else:
        return "unknown"

def build_macos():
    """构建 macOS 版本 - 使用快速PyInstaller方案"""
    print("🍎 Building for macOS with PyInstaller (fast)...")
    
    script_path = Path(__file__).parent / "packaging" / "macos" / "build_macos_fast.py"
    if not script_path.exists():
        print(f"Error: Build script not found: {script_path}")
        return False
    
    try:
        # 执行快速的PyInstaller构建脚本
        result = subprocess.run(
            ["python3", str(script_path)],
            cwd=Path(__file__).parent,  # 在项目根目录执行
            check=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"macOS build failed: {e}")
        return False

def build_windows():
    """构建 Windows 版本"""
    print("🪟 Building for Windows...")
    
    script_path = Path(__file__).parent / "packaging" / "windows" / "build_windows.bat"
    if not script_path.exists():
        print(f"Error: Build script not found: {script_path}")
        return False
    
    try:
        # 执行构建脚本
        result = subprocess.run(
            [str(script_path)],
            cwd=script_path.parent,
            shell=True,
            check=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Windows build failed: {e}")
        return False

def build_linux():
    """构建 Linux 版本"""
    print("🐧 Building for Linux...")
    
    script_path = Path(__file__).parent / "packaging" / "linux" / "build_linux.sh"
    if not script_path.exists():
        print(f"Error: Build script not found: {script_path}")
        return False
    
    try:
        # 执行构建脚本
        result = subprocess.run(
            ["bash", str(script_path)],
            cwd=script_path.parent,
            check=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Linux build failed: {e}")
        return False

def main():
    """主函数"""
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        target_platform = sys.argv[1].lower()
    else:
        target_platform = get_current_platform()
    
    print(f"🔨 md2docx Cross-Platform Build Script")
    print(f"Target platform: {target_platform}")
    print(f"Current platform: {get_current_platform()}")
    print()
    
    success = True
    
    if target_platform == "macos":
        success = build_macos()
    elif target_platform == "windows":
        success = build_windows()
    elif target_platform == "linux":
        success = build_linux()
    elif target_platform == "all":
        print("Building for all platforms...")
        platforms = ["macos", "windows", "linux"]
        results = {}
        
        for plt in platforms:
            print(f"\n{'='*50}")
            print(f"Building for {plt}...")
            print(f"{'='*50}")
            
            if plt == "macos":
                results[plt] = build_macos()
            elif plt == "windows":
                results[plt] = build_windows()
            elif plt == "linux":
                results[plt] = build_linux()
        
        # 显示总结
        print(f"\n{'='*50}")
        print("BUILD SUMMARY")
        print(f"{'='*50}")
        
        all_success = True
        for plt, result in results.items():
            status = "✅ SUCCESS" if result else "❌ FAILED"
            print(f"{plt:10}: {status}")
            if not result:
                all_success = False
        
        success = all_success
    else:
        print(f"Error: Unknown platform '{target_platform}'")
        print("Supported platforms: macos, windows, linux, all")
        success = False
    
    if success:
        print(f"\n🎉 Build completed successfully!")
        print(f"\nBuilt artifacts can be found in:")
        if target_platform == "macos":
            print(f"  packaging/macos/dist/")
        elif target_platform == "windows":
            print(f"  packaging/windows/dist/")
        elif target_platform == "linux":
            print(f"  packaging/linux/dist/")
        else:
            print(f"  packaging/{target_platform}/dist/")
    else:
        print(f"\n❌ Build failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())