"""
PyInstaller setup script for Linux packaging

Usage:
    cd packaging/linux
    python3 setup_pyinstaller.py

Requirements:
    pip install pyinstaller
"""

import PyInstaller.__main__
import os
import sys
from pathlib import Path

# Get project root directory
project_root = Path(__file__).parent.parent.parent
src_dir = project_root / "src"

def build_linux_app():
    """Build Linux executable with PyInstaller"""
    
    app_name = "md2docx"
    version = "1.0.0"
    # 从 VERSION 文件读取版本号
    version_file = project_root / "VERSION"
    if version_file.exists():
        with open(version_file, 'r') as f:
            version = f.read().strip()
        # 确保版本号不为空
        if not version:
            version = "1.0.0"
    
    # PyInstaller arguments
    args = [
        str(src_dir / "main.py"),  # Main script
        "--name", app_name,
        "--onedir",  # Create one directory
        "--windowed",  # No console (GUI app)
        "--clean",  # Clean cache
        
        # Icon (for desktop integration)
        "--icon", str(project_root / "assets" / "icons" / "app_icon.png"),
        
        # Additional data files
        "--add-data", f"{project_root / 'locales'}:locales",
        "--add-data", f"{project_root / 'templates'}:templates", 
        "--add-data", f"{project_root / 'assets' / 'icons'}:assets/icons",
        
        # Hidden imports
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtWidgets", 
        "--hidden-import", "PySide6.QtGui",
        "--hidden-import", "emoji",
        "--hidden-import", "platformdirs",
        "--hidden-import", "platform",
        "--hidden-import", "pathlib",
        "--hidden-import", "json",
        "--hidden-import", "shutil",
        "--hidden-import", "zipfile",
        "--hidden-import", "subprocess",
        "--hidden-import", "logging",
        
        # Exclude unnecessary modules
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib",
        "--exclude-module", "numpy",
        "--exclude-module", "scipy",
        "--exclude-module", "PIL",
        "--exclude-module", "wx",
        
        # Optimization
        "--optimize", "1",
        "--strip",
        
        # Output directory
        "--distpath", "dist",
        "--workpath", "build", 
        "--specpath", ".",
    ]
    
    print("🐧 Building Linux executable with PyInstaller...")
    print(f"Arguments: {' '.join(args)}")
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print("✅ Build completed!")
    
    # Create .desktop file for Linux desktop integration
    create_desktop_file(app_name, version)
    
    # Create AppImage if appimage-builder is available
    try_create_appimage(app_name, version)


def create_desktop_file(app_name, version):
    """Create .desktop file for Linux desktop integration"""
    
    desktop_content = f"""[Desktop Entry]
Name=Markdown to Word
GenericName=Document Converter
Comment=Convert Markdown files to Word documents
Exec={app_name}
Icon={app_name}
Terminal=false
Type=Application
Categories=Office;WordProcessor;
MimeType=text/markdown;text/x-markdown;
StartupNotify=true
StartupWMClass=md2docx
"""
    
    desktop_file = Path("dist") / f"{app_name}.desktop"
    with open(desktop_file, "w", encoding="utf-8") as f:
        f.write(desktop_content)
    
    # Make executable
    os.chmod(desktop_file, 0o755)
    
    print(f"Created desktop file: {desktop_file}")


def try_create_appimage(app_name, version):
    """Try to create AppImage if tools are available"""
    
    try:
        # Check if appimagetool is available
        import subprocess
        result = subprocess.run(["which", "appimagetool"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Creating AppImage...")
            create_appdir_structure(app_name, version)
        else:
            print("AppImage tools not found, skipping AppImage creation")
            print("Install with: wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage")
            
    except Exception as e:
        print(f"AppImage creation failed: {e}")


def create_appdir_structure(app_name, version):
    """Create AppDir structure for AppImage"""
    
    app_dir = Path("dist") / f"{app_name}.AppDir"
    app_dir.mkdir(exist_ok=True)
    
    # Create directory structure
    (app_dir / "usr" / "bin").mkdir(parents=True, exist_ok=True)
    (app_dir / "usr" / "share" / "applications").mkdir(parents=True, exist_ok=True)
    (app_dir / "usr" / "share" / "pixmaps").mkdir(parents=True, exist_ok=True)
    
    # Copy executable
    import shutil
    exe_src = Path("dist") / app_name / app_name
    exe_dst = app_dir / "usr" / "bin" / app_name
    
    if exe_src.exists():
        shutil.copytree(Path("dist") / app_name, app_dir / "usr" / "bin", dirs_exist_ok=True)
    
    # Copy desktop file
    desktop_src = Path("dist") / f"{app_name}.desktop"
    desktop_dst = app_dir / "usr" / "share" / "applications" / f"{app_name}.desktop"
    if desktop_src.exists():
        shutil.copy2(desktop_src, desktop_dst)
        shutil.copy2(desktop_src, app_dir / f"{app_name}.desktop")
    
    # Copy icon
    icon_src = project_root / "assets" / "icons" / "app_icon.png"
    if icon_src.exists():
        shutil.copy2(icon_src, app_dir / "usr" / "share" / "pixmaps" / f"{app_name}.png")
        shutil.copy2(icon_src, app_dir / f"{app_name}.png")
    
    # Create AppRun script
    apprun_content = f"""#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${{SELF%/*}}
export PATH="${{HERE}}/usr/bin:${{PATH}}"
cd "${{HERE}}/usr/bin"
exec "./{app_name}" "$@"
"""
    
    apprun_file = app_dir / "AppRun"
    with open(apprun_file, "w") as f:
        f.write(apprun_content)
    
    os.chmod(apprun_file, 0o755)
    
    print(f"Created AppDir: {app_dir}")
    print("To create AppImage, run:")
    print(f"  appimagetool '{app_dir}' '{app_name}-{version}-x86_64.AppImage'")


if __name__ == "__main__":
    # Change to packaging directory
    os.chdir(Path(__file__).parent)
    
    # Add src to Python path
    sys.path.insert(0, str(src_dir))
    
    build_linux_app()