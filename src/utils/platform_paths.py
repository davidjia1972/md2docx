"""
跨平台用户数据目录管理模块

为 md2docx 应用提供跨平台的用户数据目录管理，根据运行平台自动适配到对应的标准位置：
- macOS: ~/Library/Application Support/, ~/Library/Caches/, ~/Library/Logs/
- Windows: %APPDATA%/, %LOCALAPPDATA%/
- Linux: ~/.config/, ~/.cache/, ~/.local/share/

支持开发环境和打包环境的自动检测。
"""

import os
import sys
import platform
from pathlib import Path
from typing import Dict, Optional

# 应用名称，用于创建目录
APP_NAME = "md2docx"


def is_bundled() -> bool:
    """
    检测应用是否已被打包（PyInstaller、py2app等）
    
    Returns:
        bool: True 如果是打包后的应用，False 如果是开发环境
    """
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def get_bundle_resource_path(relative_path: str) -> Path:
    """
    获取打包应用中的资源文件路径
    
    Args:
        relative_path: 相对于资源目录的路径
        
    Returns:
        Path: 资源文件的绝对路径
    """
    if is_bundled():
        # PyInstaller 创建临时目录，存储在 sys._MEIPASS
        base_path = getattr(sys, '_MEIPASS', Path(__file__).parent)
    else:
        # 开发环境，使用项目根目录
        base_path = Path(__file__).parent.parent.parent
    
    return Path(base_path) / relative_path


def get_platform_user_dirs() -> Dict[str, Path]:
    """
    根据运行平台获取用户数据目录
    
    Returns:
        Dict[str, Path]: 包含各类目录路径的字典
            - config: 配置文件目录
            - cache: 缓存文件目录  
            - logs: 日志文件目录
            - data: 用户数据目录
            - templates: 用户模板目录
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        base_support = Path.home() / "Library" / "Application Support" / APP_NAME
        cache_dir = Path.home() / "Library" / "Caches" / APP_NAME
        logs_dir = Path.home() / "Library" / "Logs" / APP_NAME
        data_dir = base_support
        
    elif system == "Windows":
        # 使用环境变量，提供备用路径
        appdata = Path(os.environ.get('APPDATA', Path.home() / "AppData" / "Roaming"))
        localappdata = Path(os.environ.get('LOCALAPPDATA', Path.home() / "AppData" / "Local"))
        
        base_support = appdata / APP_NAME
        cache_dir = localappdata / APP_NAME
        logs_dir = localappdata / APP_NAME / "logs"
        data_dir = base_support
        
    elif system == "Linux":
        # 遵循 XDG Base Directory 规范
        base_support = Path.home() / ".config" / APP_NAME
        cache_dir = Path.home() / ".cache" / APP_NAME
        logs_dir = Path.home() / ".local" / "share" / APP_NAME / "logs"
        data_dir = Path.home() / ".local" / "share" / APP_NAME
        
    else:
        # 未知平台，使用通用备用方案
        base_dir = Path.home() / f".{APP_NAME}"
        base_support = base_dir
        cache_dir = base_dir / "cache"
        logs_dir = base_dir / "logs"
        data_dir = base_dir
    
    return {
        'config': base_support,
        'cache': cache_dir,
        'logs': logs_dir,
        'data': data_dir,
        'templates': data_dir / 'templates'
    }


def get_development_dirs() -> Dict[str, Path]:
    """
    获取开发环境的目录路径（项目根目录相对路径）
    
    Returns:
        Dict[str, Path]: 开发环境的目录路径
    """
    project_root = Path(__file__).parent.parent.parent
    
    return {
        'config': project_root / 'config',
        'cache': project_root / 'temp',
        'logs': project_root / 'logs',
        'data': project_root / 'data',
        'templates': project_root / 'templates'
    }


def get_app_directories(force_user_dirs: bool = None) -> Dict[str, Path]:
    """
    获取应用的所有目录路径，自动检测环境
    
    Args:
        force_user_dirs: 强制使用用户目录（用于测试）
                        None=自动检测, True=强制用户目录, False=强制开发目录
    
    Returns:
        Dict[str, Path]: 应用目录路径字典
    """
    # 决定使用哪种目录模式
    if force_user_dirs is None:
        use_user_dirs = is_bundled()
    else:
        use_user_dirs = force_user_dirs
    
    if use_user_dirs:
        dirs = get_platform_user_dirs()
    else:
        dirs = get_development_dirs()
    
    return dirs


def ensure_directories_exist(directories: Dict[str, Path]) -> None:
    """
    确保所有必需的目录存在，如不存在则创建
    
    Args:
        directories: 目录路径字典
    """
    for dir_type, dir_path in directories.items():
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Warning: Failed to create {dir_type} directory {dir_path}: {e}")


def copy_default_resources_if_needed(app_dirs: Dict[str, Path]) -> None:
    """
    首次运行时复制默认资源到用户目录
    
    Args:
        app_dirs: 应用目录路径字典
    """
    # 检查是否需要初始化
    config_file = app_dirs['config'] / 'settings.json'
    if config_file.exists():
        return  # 已经初始化过了
    
    try:
        # 不复制默认模板 - 内置模板应该从bundle中直接使用
        # 用户模板目录仅用于用户自定义的模板文件
        pass
        
        # 复制默认配置（如果存在）
        default_config = get_bundle_resource_path('config/settings.json')
        if default_config.exists():
            import shutil
            shutil.copy2(default_config, config_file)
            
    except Exception as e:
        print(f"Warning: Failed to copy default resources: {e}")


def initialize_app_directories(force_user_dirs: bool = None) -> Dict[str, Path]:
    """
    初始化应用目录，包括创建目录和复制默认资源
    
    Args:
        force_user_dirs: 强制使用用户目录模式
        
    Returns:
        Dict[str, Path]: 初始化完成的目录路径字典
    """
    # 获取目录路径
    app_dirs = get_app_directories(force_user_dirs)
    
    # 创建必要目录
    ensure_directories_exist(app_dirs)
    
    # 复制默认资源（仅在用户目录模式下）
    if force_user_dirs or is_bundled():
        copy_default_resources_if_needed(app_dirs)
    
    return app_dirs


# 全局变量，存储应用目录（延迟初始化）
_app_directories: Optional[Dict[str, Path]] = None


def get_app_dirs() -> Dict[str, Path]:
    """
    获取应用目录（单例模式，首次调用时初始化）
    
    Returns:
        Dict[str, Path]: 应用目录路径字典
    """
    global _app_directories
    if _app_directories is None:
        _app_directories = initialize_app_directories()
    return _app_directories


if __name__ == "__main__":
    # 测试脚本 - 仅在调试模式下输出
    import os
    debug = os.environ.get('DEBUG', '').lower() in ['1', 'true', 'yes']
    
    if debug:
        print(f"Platform: {platform.system()}")
        print(f"Is bundled: {is_bundled()}")
        print("\nApp directories:")
        
        dirs = get_app_directories()
        for dir_type, dir_path in dirs.items():
            print(f"  {dir_type:10}: {dir_path}")
            print(f"             exists: {dir_path.exists()}")
        
        print("\nInitializing directories...")
        initialized_dirs = initialize_app_directories()
        print("Initialization complete!")
    else:
        # 静默初始化
        initialize_app_directories()