#!/usr/bin/env python3
"""
macOS快速构建脚本 - 使用PyInstaller替代py2app
解决PySide6兼容性问题和PEP 517错误

使用方法:
    python build_macos_pyinstaller.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
VERSION = "1.0.0"

# 颜色输出
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'

def print_status(msg, color=Colors.BLUE):
    print(f"{color}{msg}{Colors.NC}")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.NC}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.NC}")

def run_command(cmd, check=True):
    print_status(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        if result.stdout.strip():
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {e}")
        if e.stderr:
            print(e.stderr)
        if check:
            sys.exit(1)

def main():
    print_status("🚀 macOS快速构建 - 使用PyInstaller")
    
    # 1. 安装PyInstaller
    print_status("📦 安装PyInstaller...")
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pyinstaller>=5.13"])
    
    # 2. 清理旧的构建
    build_dir = PROJECT_ROOT / "build"
    dist_dir = PROJECT_ROOT / "dist"
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print_status(f"清理 {build_dir}")
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
        print_status(f"清理 {dist_dir}")
    
    # 3. 准备构建参数
    main_script = PROJECT_ROOT / "src" / "main.py"
    app_name = "md2docx"
    icon_path = PROJECT_ROOT / "assets" / "icons" / "app_icon.icns"
    
    # PyInstaller命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", app_name,
        "--windowed",  # macOS app bundle
        "--onedir",    # 目录模式，不是单文件
        "--clean",     # 清理临时文件
        
        # 图标
        "--icon", str(icon_path),
        
        # 数据文件
        "--add-data", f"{PROJECT_ROOT / 'locales'}:locales",
        "--add-data", f"{PROJECT_ROOT / 'templates'}:templates", 
        "--add-data", f"{PROJECT_ROOT / 'assets' / 'icons'}:assets/icons",
        
        # 隐藏导入（PySide6相关）
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtWidgets", 
        "--hidden-import", "PySide6.QtGui",
        "--hidden-import", "emoji",
        "--hidden-import", "platformdirs",
        
        # 应用模块
        "--hidden-import", "ui",
        "--hidden-import", "ui.main_window",
        "--hidden-import", "converter", 
        "--hidden-import", "utils",
        "--hidden-import", "templates",
        
        # 排除不需要的模块
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib",
        "--exclude-module", "numpy",
        "--exclude-module", "scipy",
        "--exclude-module", "PIL",
        
        # 主脚本
        str(main_script)
    ]
    
    # 4. 运行构建
    print_status("🔨 开始PyInstaller构建...")
    result = run_command(cmd)
    
    # 5. 检查构建结果
    app_bundle = dist_dir / f"{app_name}.app"
    exe_path = dist_dir / app_name / app_name
    
    if app_bundle.exists():
        print_success(f"macOS应用构建成功: {app_bundle}")
        
        # 显示大小
        result = run_command(["du", "-sh", str(app_bundle)], check=False)
        if result.returncode == 0:
            size = result.stdout.split()[0]
            print_success(f"应用大小: {size}")
            
        # 测试启动
        print_status("🧪 测试应用启动...")
        test_result = run_command([
            str(app_bundle / "Contents" / "MacOS" / app_name), "--version"
        ], check=False)
        
        if test_result.returncode == 0:
            print_success("应用可以正常启动")
        else:
            print_status("应用启动测试完成（--version选项可能不存在，这是正常的）")
            
    elif exe_path.exists():
        print_success(f"应用构建成功: {exe_path}")
    else:
        print_error("构建失败 - 找不到输出文件")
        sys.exit(1)
    
    # 6. 提供使用说明
    print()
    print_success("🎉 构建完成!")
    print()
    print_status("💡 使用说明:")
    if app_bundle.exists():
        print(f"   1. 测试应用: open \"{app_bundle}\"")
        print(f"   2. 应用位置: {app_bundle}")
        print("   3. 安装pandoc: brew install pandoc")
        print(f"   4. 复制到Applications: cp -r \"{app_bundle}\" /Applications/")
    else:
        print(f"   1. 测试应用: \"{exe_path}\"")
        print(f"   2. 应用位置: {exe_path}")

if __name__ == "__main__":
    main()