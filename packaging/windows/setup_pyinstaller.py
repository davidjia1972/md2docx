"""
PyInstaller setup script for Windows packaging

Usage:
    cd packaging/windows
    python setup_pyinstaller.py

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
packaging_dir = Path(__file__).parent

print(f"Project root: {project_root}")
print(f"Source directory: {src_dir}")
print(f"Packaging directory: {packaging_dir}")

# Build configuration
def build_windows_app():
    """Build Windows executable with PyInstaller"""
    
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
    
    print(f"Building version: {version}")
    
    # PyInstaller arguments
    args = [
        str(src_dir / "main.py"),  # Main script
        "--name", app_name,
        "--onedir",  # Create one directory (easier for debugging)
        "--windowed",  # No console window
        "--clean",  # Clean cache
        
        # Icon
        "--icon", str(project_root / "assets" / "icons" / "app_icon.ico"),
        
        # Additional data files
        "--add-data", f"{project_root / 'locales'};locales",
        "--add-data", f"{project_root / 'templates'};templates", 
        "--add-data", f"{project_root / 'assets' / 'icons'};assets/icons",
        
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
        
        # Output directory - 使用绝对路径
        "--distpath", str(packaging_dir / "dist"),
        "--workpath", str(packaging_dir / "build"),
        "--specpath", str(packaging_dir),
        
        # Version info
        "--version-file", str(packaging_dir / "version_info.txt"),
    ]
    
    # Create version info file
    create_version_info(version)
    
    print("🔨 Building Windows executable with PyInstaller...")
    print(f"Arguments: {' '.join(args)}")
    
    # Run PyInstaller
    try:
        PyInstaller.__main__.run(args)
        print("✅ Build completed!")
        
        # Check if output was created
        expected_output = packaging_dir / "dist" / app_name / f"{app_name}.exe"
        if expected_output.exists():
            print(f"✅ Executable created: {expected_output}")
        else:
            print(f"❌ Executable not found at expected location: {expected_output}")
            print("Contents of dist directory:")
            dist_dir = packaging_dir / "dist"
            if dist_dir.exists():
                for item in dist_dir.rglob("*"):
                    print(f"  {item}")
            else:
                print("  dist directory does not exist")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Build failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def create_version_info(version):
    """Create Windows version info file"""
    version_parts = version.split('.')
    version_tuple = tuple(int(v) for v in version_parts) + (0,) * (4 - len(version_parts))
    
    version_info_content = f"""# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    filevers={version_tuple},
    prodvers={version_tuple},
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x4,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'Converter Tools'),
          StringStruct(u'FileDescription', u'Markdown to Word Converter'),
          StringStruct(u'FileVersion', u'{version}'),
          StringStruct(u'InternalName', u'md2docx'),
          StringStruct(u'LegalCopyright', u'Copyright © 2024 Converter Tools'),
          StringStruct(u'OriginalFilename', u'md2docx.exe'),
          StringStruct(u'ProductName', u'Markdown to Word'),
          StringStruct(u'ProductVersion', u'{version}')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    
    version_info_path = packaging_dir / "version_info.txt"
    with open(version_info_path, "w", encoding="utf-8") as f:
        f.write(version_info_content)
    
    print(f"Created version_info.txt at {version_info_path}")


if __name__ == "__main__":
    # Change to packaging directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # Add src to Python path
    sys.path.insert(0, str(src_dir))
    
    print(f"Working directory changed to: {os.getcwd()}")
    
    build_windows_app()