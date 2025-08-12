"""
简化的macOS构建脚本 - 解决PySide6和py2app的兼容性问题
"""

from setuptools import setup
import sys
from pathlib import Path

# 增加递归深度限制来解决PySide6的问题
sys.setrecursionlimit(5000)

# 获取项目根目录
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# 应用入口
APP = [str(project_root / "src" / "main.py")]

# 基本信息
VERSION = "1.0.0"
# 从 VERSION 文件读取版本号
version_file = project_root / "VERSION"
if version_file.exists():
    with open(version_file, 'r') as f:
        version = f.read().strip()
    # 确保版本号不为空
    if version:
        VERSION = version

NAME = "md2docx"
DISPLAY_NAME = "Markdown to Word"

# 数据文件 - 简化处理
DATA_FILES = []

# 添加本地化文件
locales_dir = project_root / "locales"
if locales_dir.exists():
    for locale_dir in locales_dir.iterdir():
        if locale_dir.is_dir():
            json_files = list(locale_dir.glob("*.json"))
            if json_files:
                DATA_FILES.append((f"locales/{locale_dir.name}", [str(f) for f in json_files]))

# 添加模板文件
templates_dir = project_root / "templates"
if templates_dir.exists():
    template_files = list(templates_dir.glob("*.docx"))
    if template_files:
        DATA_FILES.append(("templates", [str(f) for f in template_files]))

# 添加图标文件
icons_dir = project_root / "assets" / "icons"
if icons_dir.exists():
    icon_files = [f for f in icons_dir.glob("*") if f.is_file() and f.suffix in ['.icns', '.png', '.ico']]
    if icon_files:
        DATA_FILES.append(("assets/icons", [str(f) for f in icon_files]))

# py2app选项 - 简化配置
OPTIONS = {
    'py2app': {
        # 基本配置
        'argv_emulation': False,
        'iconfile': str(project_root / "assets" / "icons" / "app_icon.icns"),
        
        # Info.plist配置
        'plist': {
            'CFBundleName': DISPLAY_NAME,
            'CFBundleDisplayName': DISPLAY_NAME,
            'CFBundleIdentifier': f'com.convertertools.{NAME}',
            'CFBundleVersion': VERSION,
            'CFBundleShortVersionString': VERSION,
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
        },
        
        # 包含的包 - 简化列表
        'packages': ['PySide6', 'emoji', 'platformdirs'],
        
        # 包含的模块
        'includes': [
            'platform', 'pathlib', 'json', 'shutil', 
            'subprocess', 'logging', 'threading'
        ],
        
        # 排除的包 - 减少应用大小
        'excludes': [
            'tkinter', 'matplotlib', 'numpy', 'scipy',
            'PIL', 'wx', 'PyQt5', 'PyQt6',
            # 排除Windows特定模块以避免在macOS上出现警告
            '_overlapped',
            '_io._WindowsConsoleIO',
            # 排除PySide6中不适用于macOS的模块
            'PySide6.support.signature',
            'PySide6.support.signature.lib',
            'PySide6.support.signature.typing',
            'deploy_lib',
            # 排除shiboken6相关警告模块
            'shiboken6.support',
            'shiboken6.support.signature',
            'shiboken6.support.signature.lib',
            # 排除其他可能导致警告的模块
            '_manylinux',
            '_typeshed',
            '_typeshed.importlib',
            '_typeshed.BytesPath',
            '_typeshed.StrOrBytesPath',
            '_typeshed.StrPath',
            'android',
            'jnius',
            'pkg_resources.tests',
            # 排除条件导入中可能引起问题的模块
            'Foundation',  # macOS上由objc提供的模块
            'objc',        # PyObjC相关模块
            # 排除SSL相关特定平台模块
            '_ssl.RAND_egd',
            '_ssl.enum_certificates',
            '_ssl.enum_crls',
            # 排除CTypes特定平台模块
            '_ctypes.FUNCFLAG_STDCALL',
            '_ctypes.FormatError',
            '_ctypes.LoadLibrary',
            '_ctypes._check_HRESULT',
            '_ctypes.get_last_error',
            '_ctypes.set_last_error',
            # 排除Android部署相关模块
            'deploy_lib.DesktopConfig',
            'deploy_lib.Nuitka',
            'deploy_lib.android',
            'deploy_lib.android.AndroidConfig',
            'deploy_lib.android.AndroidData',
            'deploy_lib.android.buildozer',
            'deploy_lib.finalize',
            # 排除其他不必要模块
            'itertools.batched',
            'jaraco.path',
            'jinja2',
            'multiprocessing.context.reduction',
            'pkginfo',
            'project_lib',
            'pytest',
            'qtpy2cpp_lib',
            'tqdm',
        ],
        
        # 构建选项
        'optimize': 1,
        'site_packages': True,
        'strip': False,  # 避免strip导致的问题
        'prefer_ppc': False,
        'semi_standalone': True,  # 减少不必要的模块包含
    }
}

# 简化的setup配置
setup(
    name=NAME,
    version=VERSION,
    description="Modern GUI application for converting Markdown to DOCX",
    author="David Jia",
    url="https://github.com/davidjia1972/md2docx",
    
    # 应用配置
    app=APP,
    data_files=DATA_FILES,
    options=OPTIONS,
    
    # 依赖配置
    setup_requires=['py2app'],
    python_requires='>=3.8',
    
    # 避免PEP 517相关问题
    zip_safe=False,
)