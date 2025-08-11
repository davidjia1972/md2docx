#!/usr/bin/env python3
"""
发布管理脚本

Usage:
    python release.py [command] [options]
    
Commands:
    build [platform]    - Build for specific platform (or current)
    package [version]   - Package all platforms for release
    clean              - Clean build artifacts
    info               - Show release information
    
Options:
    --version VERSION  - Override version number
    --no-checksums     - Skip checksum generation
    --dry-run          - Show what would be done without executing
"""

import sys
import os
import shutil
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# Add packaging directory to path for build utilities
sys.path.insert(0, str(Path(__file__).parent / "packaging"))

try:
    from build_utils import (
        get_version, get_build_timestamp, get_project_root,
        ensure_releases_dir, calculate_checksums, update_release_notes,
        create_latest_symlink, print_build_info
    )
except ImportError:
    print("Error: Could not import build utilities. Run from project root.")
    sys.exit(1)


class ReleaseManager:
    def __init__(self):
        self.project_root = get_project_root()
        self.version = get_version()
        self.platforms = ['macos', 'windows', 'linux']
        
    def show_info(self):
        """显示发布信息"""
        print("📋 RELEASE INFORMATION")
        print("=" * 50)
        print(f"Project root: {self.project_root}")
        print(f"Current version: {self.version}")
        print(f"Build timestamp: {get_build_timestamp()}")
        print(f"Supported platforms: {', '.join(self.platforms)}")
        
        # Check existing releases
        releases_dir = self.project_root / "releases"
        if releases_dir.exists():
            versions = [d.name for d in releases_dir.iterdir() if d.is_dir() and d.name.startswith('v')]
            if versions:
                print(f"Existing versions: {', '.join(sorted(versions))}")
            else:
                print("No existing releases found")
        else:
            print("No releases directory found")
        
        # Check build scripts
        print("\n🔧 BUILD SCRIPT STATUS")
        print("=" * 50)
        for platform in self.platforms:
            script_path = self.project_root / "packaging" / platform / f"build_{platform}.{'sh' if platform != 'windows' else 'bat'}"
            status = "✅ Ready" if script_path.exists() else "❌ Missing"
            print(f"{platform:10}: {status}")
        
        print()
    
    def build_platform(self, platform, dry_run=False):
        """构建指定平台"""
        if platform not in self.platforms:
            print(f"Error: Unknown platform '{platform}'")
            print(f"Supported platforms: {', '.join(self.platforms)}")
            return False
        
        script_name = f"build_{platform}.{'sh' if platform != 'windows' else 'bat'}"
        script_path = self.project_root / "packaging" / platform / script_name
        
        if not script_path.exists():
            print(f"Error: Build script not found: {script_path}")
            return False
        
        print(f"🔨 Building {platform}...")
        
        if dry_run:
            print(f"[DRY RUN] Would execute: {script_path}")
            return True
        
        try:
            # Change to the platform directory and run build script
            cwd = script_path.parent
            
            if platform == 'windows':
                # Run Windows batch file
                result = subprocess.run(
                    [str(script_path)],
                    cwd=cwd,
                    shell=True,
                    check=True
                )
            else:
                # Run Unix shell script
                result = subprocess.run(
                    ["bash", str(script_path)],
                    cwd=cwd,
                    check=True
                )
            
            print(f"✅ {platform} build completed successfully")
            return result.returncode == 0
            
        except subprocess.CalledProcessError as e:
            print(f"❌ {platform} build failed: {e}")
            return False
        except Exception as e:
            print(f"❌ {platform} build error: {e}")
            return False
    
    def build_all(self, dry_run=False):
        """构建所有平台"""
        print(f"🚀 Building all platforms for version {self.version}")
        print("=" * 50)
        
        results = {}
        for platform in self.platforms:
            print(f"\n{'='*20} {platform.upper()} {'='*20}")
            results[platform] = self.build_platform(platform, dry_run)
        
        # 显示构建结果摘要
        print(f"\n{'='*50}")
        print("📊 BUILD SUMMARY")
        print(f"{'='*50}")
        
        success_count = 0
        for platform, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"{platform:10}: {status}")
            if success:
                success_count += 1
        
        print(f"\nBuilds completed: {success_count}/{len(self.platforms)}")
        
        if success_count == len(self.platforms):
            print("🎉 All builds completed successfully!")
            return True
        else:
            print("⚠️  Some builds failed. Check output above.")
            return False
    
    def package_release(self, version=None, skip_checksums=False, dry_run=False):
        """打包发布版本"""
        if version:
            self.version = version
        
        print(f"📦 Packaging release v{self.version}")
        print("=" * 50)
        
        releases_dir = ensure_releases_dir(self.version)
        
        if dry_run:
            print(f"[DRY RUN] Would package release in: {releases_dir}")
            return True
        
        # 检查是否有构建产物
        missing_artifacts = []
        for platform in self.platforms:
            platform_dir = self.project_root / "packaging" / platform / "dist"
            if not platform_dir.exists() or not any(platform_dir.iterdir()):
                missing_artifacts.append(platform)
        
        if missing_artifacts:
            print(f"⚠️  Missing build artifacts for: {', '.join(missing_artifacts)}")
            print("Run builds first with: python release.py build all")
            return False
        
        # 生成校验和
        if not skip_checksums:
            print("🔐 Generating checksums...")
            calculate_checksums(releases_dir)
        
        # 更新发布说明
        print("📝 Updating release notes...")
        update_release_notes(self.version)
        
        # 创建最新版本链接
        print("🔗 Creating latest symlink...")
        create_latest_symlink(self.version)
        
        # 显示发布包内容
        print(f"\n📁 Release package contents (v{self.version}):")
        if releases_dir.exists():
            for file_path in sorted(releases_dir.iterdir()):
                if file_path.is_file():
                    size = file_path.stat().st_size / (1024*1024)  # MB
                    print(f"  {file_path.name:<30} ({size:.1f} MB)")
        
        print(f"\n✅ Release v{self.version} packaged successfully!")
        print(f"📂 Location: {releases_dir}")
        return True
    
    def clean_builds(self, dry_run=False):
        """清理构建产物"""
        print("🧹 Cleaning build artifacts...")
        
        cleaned_items = []
        
        # Clean platform build directories
        for platform in self.platforms:
            platform_dir = self.project_root / "packaging" / platform
            for dir_name in ['build', 'dist']:
                dir_path = platform_dir / dir_name
                if dir_path.exists():
                    cleaned_items.append(str(dir_path))
                    if not dry_run:
                        shutil.rmtree(dir_path)
                        print(f"Removed: {dir_path}")
        
        # Clean temporary files
        temp_patterns = ['*.pyc', '*.pyo', '__pycache__', '*.spec']
        for pattern in temp_patterns:
            for file_path in self.project_root.rglob(pattern):
                if file_path.is_file():
                    cleaned_items.append(str(file_path))
                    if not dry_run:
                        file_path.unlink()
                elif file_path.is_dir() and pattern == '__pycache__':
                    cleaned_items.append(str(file_path))
                    if not dry_run:
                        shutil.rmtree(file_path)
        
        if dry_run:
            print(f"[DRY RUN] Would clean {len(cleaned_items)} items:")
            for item in cleaned_items[:10]:  # Show first 10
                print(f"  {item}")
            if len(cleaned_items) > 10:
                print(f"  ... and {len(cleaned_items) - 10} more")
        else:
            print(f"✅ Cleaned {len(cleaned_items)} items")
        
        return True
    
    def interactive_menu(self):
        """交互式菜单"""
        while True:
            print("\n🔧 MD2DOCX RELEASE MANAGER")
            print("=" * 30)
            print("1. Show release information")
            print("2. Build single platform")
            print("3. Build all platforms") 
            print("4. Package release")
            print("5. Clean build artifacts")
            print("6. Exit")
            print()
            
            try:
                choice = input("Select option (1-6): ").strip()
                
                if choice == '1':
                    self.show_info()
                elif choice == '2':
                    print(f"Available platforms: {', '.join(self.platforms)}")
                    platform = input("Enter platform: ").strip().lower()
                    if platform in self.platforms:
                        self.build_platform(platform)
                    else:
                        print(f"Invalid platform: {platform}")
                elif choice == '3':
                    self.build_all()
                elif choice == '4':
                    version = input(f"Version ({self.version}): ").strip()
                    if not version:
                        version = self.version
                    self.package_release(version)
                elif choice == '5':
                    confirm = input("Clean all build artifacts? [y/N]: ").strip().lower()
                    if confirm in ['y', 'yes']:
                        self.clean_builds()
                elif choice == '6':
                    print("👋 Goodbye!")
                    break
                else:
                    print("Invalid choice. Please select 1-6.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="md2docx Release Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'command', 
        nargs='?',
        choices=['build', 'package', 'clean', 'info'],
        help='Command to execute'
    )
    
    parser.add_argument(
        'target',
        nargs='?',
        help='Build target (platform name or version)'
    )
    
    parser.add_argument(
        '--version',
        help='Override version number'
    )
    
    parser.add_argument(
        '--no-checksums',
        action='store_true',
        help='Skip checksum generation'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without executing'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    
    args = parser.parse_args()
    
    manager = ReleaseManager()
    
    # Interactive mode
    if args.interactive or not args.command:
        manager.interactive_menu()
        return
    
    # Override version if specified
    if args.version:
        manager.version = args.version
    
    # Execute command
    if args.command == 'info':
        manager.show_info()
        
    elif args.command == 'build':
        if args.target == 'all':
            success = manager.build_all(args.dry_run)
        elif args.target:
            success = manager.build_platform(args.target, args.dry_run)
        else:
            # Build current platform
            import platform
            current_platform = {
                'Darwin': 'macos',
                'Windows': 'windows',
                'Linux': 'linux'
            }.get(platform.system())
            
            if current_platform:
                success = manager.build_platform(current_platform, args.dry_run)
            else:
                print(f"Unsupported platform: {platform.system()}")
                success = False
        
        sys.exit(0 if success else 1)
        
    elif args.command == 'package':
        version = args.target or args.version
        success = manager.package_release(version, args.no_checksums, args.dry_run)
        sys.exit(0 if success else 1)
        
    elif args.command == 'clean':
        success = manager.clean_builds(args.dry_run)
        sys.exit(0 if success else 1)
        
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()