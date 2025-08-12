#!/usr/bin/env python3
"""
构建工具和版本管理

提供版本读取、时间戳生成、文件复制等构建辅助功能
"""

import os
import sys
import shutil
import hashlib
import platform
from datetime import datetime
from pathlib import Path


def get_project_root():
    """获取项目根目录"""
    return Path(__file__).parent.parent


def get_version():
    """从 VERSION 文件读取版本号"""
    version_file = get_project_root() / "VERSION"
    if version_file.exists():
        version = version_file.read_text().strip()
        # 确保版本号不为空
        if version:
            return version
    return "1.0.0"


def get_build_timestamp():
    """获取构建时间戳"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def get_release_name(platform_name, version=None):
    """生成发布文件名"""
    if version is None:
        version = get_version()
    
    platform_map = {
        'macos': 'macOS',
        'windows': 'Windows', 
        'linux': 'Linux'
    }
    
    platform_display = platform_map.get(platform_name, platform_name)
    return f"md2docx-v{version}-{platform_display}"


def get_platform_extension(platform_name):
    """获取平台对应的文件扩展名"""
    extensions = {
        'macos': '.dmg',
        'windows': '.zip',
        'linux': '.tar.gz'
    }
    return extensions.get(platform_name, '.zip')


def ensure_releases_dir(version=None):
    """确保发布目录存在"""
    if version is None:
        version = get_version()
    
    releases_dir = get_project_root() / "releases" / f"v{version}"
    releases_dir.mkdir(parents=True, exist_ok=True)
    return releases_dir


def copy_to_releases(source_path, platform_name, version=None):
    """复制构建产物到发布目录"""
    if version is None:
        version = get_version()
    
    releases_dir = ensure_releases_dir(version)
    release_name = get_release_name(platform_name, version)
    
    source = Path(source_path)
    
    if not source.exists():
        print(f"Warning: Source path does not exist: {source}")
        return None
    
    print(f"Copying {source} to releases directory for {platform_name}")
    print(f"Source exists: {source.exists()}")
    print(f"Source is dir: {source.is_dir()}")
    
    # 根据平台决定复制策略
    if platform_name == 'macos':
        if source.suffix == '.dmg':
            # 直接复制 DMG 文件
            dest_path = releases_dir / f"{release_name}.dmg"
            shutil.copy2(source, dest_path)
        elif source.suffix == '.app' or source.name.endswith('.app'):
            # 为 .app 创建 DMG (需要额外工具)
            dest_path = releases_dir / f"{release_name}.dmg"
            print(f"Note: {source} copied. Create DMG manually if needed.")
            return source  # 返回原路径，由调用者处理
        else:
            # 复制整个应用目录
            dest_path = releases_dir / release_name
            if source.is_dir():
                shutil.copytree(source, dest_path, dirs_exist_ok=True)
            else:
                shutil.copy2(source, dest_path)
    
    elif platform_name == 'windows':
        # Windows: 复制整个目录并压缩为 ZIP
        dest_dir = releases_dir / release_name
        dest_zip = releases_dir / f"{release_name}.zip"
        
        print(f"Windows build - source: {source}")
        print(f"Windows build - dest_dir: {dest_dir}")
        print(f"Windows build - dest_zip: {dest_zip}")
        
        if source.is_dir():
            shutil.copytree(source, dest_dir, dirs_exist_ok=True)
            # 创建 ZIP 文件，修复文件名重复添加扩展名的问题
            zip_base_name = str(dest_zip.with_suffix(''))
            print(f"Creating zip archive with base name: {zip_base_name}")
            try:
                result = shutil.make_archive(zip_base_name, 'zip', dest_dir)
                print(f"Created zip archive: {result}")
            except Exception as e:
                print(f"Failed to create zip archive: {e}")
                raise
            # 可选：删除临时目录
            # shutil.rmtree(dest_dir)
        else:
            shutil.copy2(source, dest_dir)
    
    elif platform_name == 'linux':
        # Linux: 复制目录并创建 tar.gz
        dest_dir = releases_dir / release_name
        dest_tar = releases_dir / f"{release_name}.tar.gz"
        
        if source.is_dir():
            shutil.copytree(source, dest_dir, dirs_exist_ok=True)
            # 创建 tar.gz 文件，修复文件名重复添加扩展名的问题
            shutil.make_archive(str(dest_tar.with_suffix('')), 'gztar', dest_dir.parent, dest_dir.name)
            # 可选：删除临时目录
            # shutil.rmtree(dest_dir)
        else:
            shutil.copy2(source, dest_dir)
        
        # 同时复制 AppImage 如果存在
        appimage_source = source.parent / f"md2docx-v{version}-x86_64.AppImage"
        if appimage_source.exists():
            appimage_dest = releases_dir / f"md2docx-v{version}-x86_64.AppImage"
            shutil.copy2(appimage_source, appimage_dest)
    
    print(f"Copied build artifacts to: {releases_dir}")
    # 列出发布目录中的文件
    if releases_dir.exists():
        print("Files in releases directory:")
        for f in releases_dir.iterdir():
            print(f"  {f.name}")
    return releases_dir


def calculate_checksums(directory):
    """计算目录中所有文件的 SHA256 校验和"""
    directory = Path(directory)
    checksums = {}
    
    for file_path in directory.glob("*"):
        if file_path.is_file() and file_path.name != "checksums.txt":
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            checksums[file_path.name] = sha256_hash.hexdigest()
    
    # 写入校验和文件
    checksums_file = directory / "checksums.txt"
    with open(checksums_file, "w") as f:
        f.write("# SHA256 Checksums\n")
        f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
        for filename, checksum in sorted(checksums.items()):
            f.write(f"{checksum}  {filename}\n")
    
    print(f"Generated checksums: {checksums_file}")
    return checksums_file


def update_release_notes(version=None):
    """更新发布说明中的时间戳"""
    if version is None:
        version = get_version()
    
    releases_dir = ensure_releases_dir(version)
    release_notes = releases_dir / "RELEASE_NOTES.md"
    
    if release_notes.exists():
        content = release_notes.read_text()
        
        # 更新时间戳
        build_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        release_date = datetime.now().strftime("%Y-%m-%d")
        
        content = content.replace("**Release Date**: TBD", f"**Release Date**: {release_date}")
        content = content.replace("**Build Date**: TBD", f"**Build Date**: {build_date}")
        
        release_notes.write_text(content)
        print(f"Updated release notes: {release_notes}")


def create_latest_symlink(version=None):
    """创建指向最新版本的符号链接"""
    if version is None:
        version = get_version()
    
    releases_root = get_project_root() / "releases"
    latest_link = releases_root / "latest"
    version_dir = f"v{version}"
    
    # 删除现有链接
    if latest_link.exists() or latest_link.is_symlink():
        latest_link.unlink()
    
    # 创建新链接
    try:
        latest_link.symlink_to(version_dir)
        print(f"Created symlink: latest -> {version_dir}")
    except OSError:
        # Windows 可能不支持符号链接，创建副本或跳过
        print(f"Note: Could not create symlink (platform limitation)")


def print_build_info():
    """打印构建信息"""
    print("=" * 50)
    print("BUILD INFORMATION")
    print("=" * 50)
    print(f"Version: {get_version()}")
    print(f"Build timestamp: {get_build_timestamp()}")
    print(f"Build platform: {platform.system()}")
    print(f"Python version: {sys.version}")
    print(f"Project root: {get_project_root()}")
    print("=" * 50)


if __name__ == "__main__":
    # 测试功能
    print_build_info()
    
    # 测试版本读取
    print(f"Version: {get_version()}")
    
    # 测试发布目录创建
    releases_dir = ensure_releases_dir()
    print(f"Releases directory: {releases_dir}")
    
    # 测试文件名生成
    for platform in ['macos', 'windows', 'linux']:
        name = get_release_name(platform)
        ext = get_platform_extension(platform)
        print(f"{platform}: {name}{ext}")