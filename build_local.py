#!/usr/bin/env python3
"""
本地构建脚本 - 解决PEP 517兼容性问题
支持macOS, Windows, Linux平台

使用方法:
    python build_local.py         # 自动检测平台
    python build_local.py macos   # 指定构建macOS版本
    python build_local.py windows # 指定构建Windows版本
    python build_local.py linux   # 指定构建Linux版本
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

# 项目配置
PROJECT_ROOT = Path(__file__).parent
VERSION_FILE = PROJECT_ROOT / "VERSION"
VERSION = VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else "1.0.0"

# 颜色输出
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_status(message, color=Colors.BLUE):
    """打印带颜色的状态消息"""
    print(f"{color}{message}{Colors.NC}")

def print_success(message):
    """打印成功消息"""
    print(f"{Colors.GREEN}✅ {message}{Colors.NC}")

def print_warning(message):
    """打印警告消息"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.NC}")

def print_error(message):
    """打印错误消息"""
    print(f"{Colors.RED}❌ {message}{Colors.NC}")

def run_command(cmd, cwd=None, check=True):
    """运行命令并处理错误"""
    print_status(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd, 
            cwd=cwd or PROJECT_ROOT,
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {' '.join(cmd)}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        if check:
            sys.exit(1)
        return e

def check_python_requirements():
    """检查Python环境和PIP版本"""
    print_status("🐍 检查Python环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version < (3, 8):
        print_error(f"Python 3.8+ required, got {python_version.major}.{python_version.minor}")
        sys.exit(1)
    
    print_success(f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 升级pip, setuptools, wheel到最新版本以解决PEP 517问题
    print_status("📦 升级构建工具...")
    essential_packages = [
        "pip>=23.0",
        "setuptools>=61.0", 
        "wheel>=0.38.0",
        "build>=0.10.0"
    ]
    
    for package in essential_packages:
        result = run_command([
            sys.executable, "-m", "pip", "install", 
            "--upgrade", "--force-reinstall", package
        ], check=False)
        if result.returncode != 0:
            print_warning(f"Failed to upgrade {package}, continuing...")
    
    print_success("构建工具升级完成")

def fix_setuptools_conflicts():
    """修复setuptools和相关包的冲突问题"""
    print_status("🔧 修复setuptools依赖冲突...")
    
    # 安装可能缺失的backports包
    conflict_packages = [
        "backports.tarfile",
        "jaraco.context",
        "importlib-metadata"
    ]
    
    for package in conflict_packages:
        result = run_command([
            sys.executable, "-m", "pip", "install", "--upgrade", package
        ], check=False)
        if result.returncode == 0:
            print_success(f"安装/升级 {package}")

def install_platform_build_tools(target_platform):
    """安装平台特定的构建工具"""
    print_status(f"🔧 安装{target_platform}构建工具...")
    
    # 先修复setuptools冲突
    fix_setuptools_conflicts()
    
    if target_platform == "macos":
        # 安装py2app
        result = run_command([
            sys.executable, "-m", "pip", "install",
            "--upgrade", "py2app>=0.28"
        ], check=False)
        
        if result.returncode != 0:
            print_error("py2app安装失败")
            sys.exit(1)
            
    elif target_platform in ["windows", "linux"]:
        # 安装PyInstaller  
        result = run_command([
            sys.executable, "-m", "pip", "install",
            "--upgrade", "pyinstaller>=5.13"
        ], check=False)
        
        if result.returncode != 0:
            print_error("PyInstaller安装失败")
            sys.exit(1)
    
    print_success(f"{target_platform}构建工具安装完成")

def install_dependencies():
    """安装项目依赖"""
    print_status("📋 安装项目依赖...")
    
    # 使用--use-pep517强制使用PEP 517
    result = run_command([
        sys.executable, "-m", "pip", "install", 
        "--use-pep517", "--force-reinstall",
        "-r", "requirements.txt"
    ], check=False)
    
    if result.returncode != 0:
        print_warning("依赖安装可能有问题，尝试单独安装...")
        
        # 尝试单独安装每个依赖
        deps = ["PySide6>=6.5.0,<7.0.0", "emoji>=2.2.0,<3.0.0", "platformdirs>=3.0.0,<5.0.0"]
        for dep in deps:
            run_command([
                sys.executable, "-m", "pip", "install",
                "--use-pep517", dep
            ])
    
    print_success("项目依赖安装完成")

def build_macos():
    """构建macOS版本"""
    print_status("🍎 构建macOS应用...")
    
    build_dir = PROJECT_ROOT / "packaging" / "macos"
    
    # 清理旧的构建文件
    for dir_name in ["build", "dist"]:
        dir_path = build_dir / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print_status(f"清理 {dir_path}")
    
    # 运行py2app构建
    result = run_command([
        sys.executable, "setup_py2app.py", "py2app", "--optimize=1"
    ], cwd=build_dir)
    
    # 检查构建结果
    app_path = build_dir / "dist" / "md2docx.app"
    if app_path.exists():
        print_success(f"macOS应用构建成功: {app_path}")
        
        # 显示应用大小
        result = run_command(["du", "-sh", str(app_path)], check=False)
        if result.returncode == 0:
            print_success(f"应用大小: {result.stdout.split()[0]}")
        
        return app_path
    else:
        print_error("macOS应用构建失败")
        sys.exit(1)

def build_windows():
    """构建Windows版本"""
    print_status("🪟 构建Windows应用...")
    
    build_dir = PROJECT_ROOT / "packaging" / "windows"
    
    # 清理旧的构建文件
    for dir_name in ["build", "dist"]:
        dir_path = build_dir / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print_status(f"清理 {dir_path}")
    
    # 运行PyInstaller构建
    result = run_command([
        sys.executable, "setup_pyinstaller.py"
    ], cwd=build_dir)
    
    # 检查构建结果
    exe_path = build_dir / "dist" / "md2docx" / "md2docx.exe"
    if exe_path.exists():
        print_success(f"Windows应用构建成功: {exe_path}")
        return exe_path
    else:
        print_error("Windows应用构建失败")
        sys.exit(1)

def build_linux():
    """构建Linux版本"""
    print_status("🐧 构建Linux应用...")
    
    build_dir = PROJECT_ROOT / "packaging" / "linux"
    
    # 清理旧的构建文件
    for dir_name in ["build", "dist"]:
        dir_path = build_dir / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print_status(f"清理 {dir_path}")
    
    # 运行PyInstaller构建
    result = run_command([
        sys.executable, "setup_pyinstaller.py"
    ], cwd=build_dir)
    
    # 检查构建结果
    exe_path = build_dir / "dist" / "md2docx" / "md2docx"
    if exe_path.exists():
        print_success(f"Linux应用构建成功: {exe_path}")
        return exe_path
    else:
        print_error("Linux应用构建失败")
        sys.exit(1)

def detect_platform():
    """检测当前平台"""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    else:
        print_error(f"不支持的平台: {system}")
        sys.exit(1)

def main():
    """主函数"""
    print_status("🚀 md2docx 本地构建工具")
    print_status(f"📁 项目路径: {PROJECT_ROOT}")
    print_status(f"🏷️  版本: {VERSION}")
    
    # 确定目标平台
    if len(sys.argv) > 1:
        target_platform = sys.argv[1].lower()
        if target_platform not in ["macos", "windows", "linux"]:
            print_error(f"不支持的平台: {target_platform}")
            print("支持的平台: macos, windows, linux")
            sys.exit(1)
    else:
        target_platform = detect_platform()
    
    print_status(f"🎯 目标平台: {target_platform}")
    
    try:
        # 检查并准备环境
        check_python_requirements()
        install_platform_build_tools(target_platform)
        install_dependencies()
        
        # 构建应用
        if target_platform == "macos":
            result_path = build_macos()
        elif target_platform == "windows":
            result_path = build_windows()
        elif target_platform == "linux":
            result_path = build_linux()
        
        print()
        print_success("🎉 构建完成!")
        print_success(f"📦 构建结果: {result_path}")
        print()
        print_status("💡 接下来你可以:")
        if target_platform == "macos":
            print(f"   1. 测试应用: open \"{result_path}\"")
            print("   2. 安装pandoc: brew install pandoc")
        elif target_platform == "windows":
            print(f"   1. 测试应用: \"{result_path}\"")
            print("   2. 安装pandoc: choco install pandoc")
        elif target_platform == "linux":
            print(f"   1. 测试应用: \"{result_path}\"")
            print("   2. 安装pandoc: sudo apt install pandoc")
        
    except KeyboardInterrupt:
        print_warning("构建被用户中断")
        sys.exit(1)
    except Exception as e:
        print_error(f"构建过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()