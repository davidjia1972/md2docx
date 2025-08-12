"""
py2app setup script for macOS packaging

Usage:
    cd packaging/macos
    python setup_py2app.py py2app

Requirements:
    pip install py2app
"""

from setuptools import setup
import os
import sys
from pathlib import Path

# Ensure we use PEP 517 compliant build
os.environ['PIP_USE_PEP517'] = '1'

# Add src directory to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

APP = [str(project_root / "src" / "main.py")]

# Get version info
VERSION = "1.0.0"
# 从 VERSION 文件读取版本号
version_file = project_root / "VERSION"
if version_file.exists():
    with open(version_file, 'r') as f:
        VERSION = f.read().strip()

NAME = "md2docx"
DISPLAY_NAME = "Markdown to Word"

# Data files to include
DATA_FILES = [
    # Localization files
    (str(project_root / "locales"), [
        str(f) for f in (project_root / "locales").rglob("*.json")
    ]),
    
    # Built-in templates
    (str(project_root / "templates"), [
        str(f) for f in (project_root / "templates").glob("*.docx")
    ]),
    
    # Icons
    (str(project_root / "assets" / "icons"), [
        str(f) for f in (project_root / "assets" / "icons").glob("*.icns")
        if f.is_file()
    ]),
]

# Options for py2app
OPTIONS = {
    'py2app': {
        'argv_emulation': False,
        'iconfile': str(project_root / "assets" / "icons" / "app_icon.icns"),
        'plist': {
            'CFBundleName': DISPLAY_NAME,
            'CFBundleDisplayName': DISPLAY_NAME,
            'CFBundleIdentifier': f'com.convertertools.{NAME}',
            'CFBundleVersion': VERSION,
            'CFBundleShortVersionString': VERSION,
            'CFBundleInfoDictionaryVersion': '6.0',
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeName': 'Markdown Files',
                    'CFBundleTypeExtensions': ['md', 'markdown'],
                    'CFBundleTypeRole': 'Editor',
                    'CFBundleTypeIconFile': 'markdown.icns',
                }
            ],
            'UTExportedTypeDeclarations': [
                {
                    'UTTypeIdentifier': 'net.daringfireball.markdown',
                    'UTTypeDescription': 'Markdown Document',
                    'UTTypeTagSpecification': {
                        'public.filename-extension': ['md', 'markdown'],
                        'public.mime-type': ['text/markdown'],
                    },
                    'UTTypeConformsTo': ['public.plain-text'],
                }
            ],
        },
        'packages': [
            'PySide6',
            'emoji',
            'platformdirs',
        ],
        'includes': [
            'platform',
            'pathlib',
            'json',
            'shutil',
            'zipfile',
            'subprocess',
            'logging',
        ],
        'excludes': [
            'tkinter',
            'matplotlib',
            'numpy',
            'scipy',
            'PIL',
            'wx',
            # 排除Windows特定模块以避免在macOS上出现警告
            '_overlapped',
            # 排除PySide6中不适用于macOS的模块
            'PySide6.support.signature',
            'PySide6.support.signature.lib',
            'PySide6.support.signature.typing',
            'deploy_lib',
        ],
        'resources': DATA_FILES,
        'optimize': 1,
        'compressed': True,
        'semi_standalone': True,  # 减少不必要的模块包含
    }
}

# Ensure PEP 517 compatibility
def get_long_description():
    try:
        with open(project_root / 'README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return "Modern GUI application for converting Markdown to DOCX"

# Setup configuration
setup(
    name=NAME,
    version=VERSION,
    description="Modern GUI application for converting Markdown to DOCX",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="David Jia",
    url="https://github.com/davidjia1972/md2docx",
    app=APP,
    data_files=DATA_FILES,
    options=OPTIONS,
    setup_requires=['py2app>=0.28'],
    install_requires=[
        'PySide6>=6.5.0,<7.0.0',
        'emoji>=2.2.0,<3.0.0',
        'platformdirs>=3.0.0,<5.0.0',
    ],
    python_requires='>=3.8',
    zip_safe=False,
)