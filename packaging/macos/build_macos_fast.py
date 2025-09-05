#!/usr/bin/env python3
"""
macOS快速构建脚本 - 精简版
只执行必要的构建步骤，无多余测试

使用方法:
    python build_macos_fast.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent  # packaging/macos -> packaging -> project_root

def main():
    print("🍎 macOS快速构建...")
    
    # 清理旧的构建 - 输出到packaging/macos/dist
    packaging_dir = PROJECT_ROOT / "packaging" / "macos"
    build_dir = packaging_dir / "build"
    dist_dir = packaging_dir / "dist"
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    # 准备构建参数
    main_script = PROJECT_ROOT / "src" / "main.py"
    app_name = "md2docx"
    icon_path = PROJECT_ROOT / "assets" / "icons" / "app_icon.icns"
    
    # PyInstaller命令（精简版）
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", app_name,
        "--windowed",
        "--onedir",
        "--clean",
        "--noconfirm",  # 不询问覆盖
        
        # 输出目录
        "--distpath", str(dist_dir),
        "--workpath", str(build_dir),
        "--specpath", str(packaging_dir),
        
        # 图标
        "--icon", str(icon_path),
        
        # 数据文件
        "--add-data", f"{PROJECT_ROOT / 'locales'}:locales",
        "--add-data", f"{PROJECT_ROOT / 'templates'}:templates", 
        "--add-data", f"{PROJECT_ROOT / 'assets' / 'icons'}:assets/icons",
        "--add-data", f"{PROJECT_ROOT / 'config'}:config",
        
        # 必要的隐藏导入
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtWidgets", 
        "--hidden-import", "PySide6.QtGui",
        "--hidden-import", "emoji",
        "--hidden-import", "platformdirs",
        
        # 设置Python路径包含src目录
        "--paths", str(PROJECT_ROOT / "src"),
        
        # 排除不需要的模块（减少体积）
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib",
        "--exclude-module", "numpy",
        "--exclude-module", "scipy",
        "--exclude-module", "PIL",
        "--exclude-module", "pytest",
        "--exclude-module", "IPython",
        "--exclude-module", "jupyter",
        
        # 排除大量PySide6模块
        "--exclude-module", "PySide6.Qt3DAnimation",
        "--exclude-module", "PySide6.Qt3DCore", 
        "--exclude-module", "PySide6.Qt3DExtras",
        "--exclude-module", "PySide6.QtBluetooth",
        "--exclude-module", "PySide6.QtCharts",
        "--exclude-module", "PySide6.QtMultimedia",
        "--exclude-module", "PySide6.QtNetwork",
        "--exclude-module", "PySide6.QtOpenGL",
        "--exclude-module", "PySide6.QtQml",
        "--exclude-module", "PySide6.QtQuick",
        "--exclude-module", "PySide6.QtSql",
        "--exclude-module", "PySide6.QtSvg",
        "--exclude-module", "PySide6.QtWebEngine",
        "--exclude-module", "PySide6.QtWebSockets",
        "--exclude-module", "PySide6.QtXml",
        
        # 优化选项
        "--optimize", "2",
        "--strip",
        "--noupx",
        
        # 主脚本
        str(main_script)
    ]
    
    # 运行构建（静默模式）
    print("🔨 开始构建...")
    try:
        # 切换到packaging目录执行，这样PyInstaller能正确找到模块
        os.chdir(packaging_dir)
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, 
                              env={**os.environ, 'PYTHONPATH': str(PROJECT_ROOT / "src")})
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        if e.stderr:
            print("错误信息:", e.stderr)
        sys.exit(1)
    finally:
        # 切换回原目录
        os.chdir(PROJECT_ROOT)
    
    # 检查结果
    app_bundle = dist_dir / f"{app_name}.app"
    exe_path = dist_dir / app_name / app_name
    
    build_successful = False
    final_artifacts = []
    
    if app_bundle.exists():
        # 显示大小
        try:
            result = subprocess.run(["du", "-sh", str(app_bundle)], 
                                  capture_output=True, text=True, check=True)
            size = result.stdout.split()[0]
            print(f"✅ macOS应用构建成功: {app_bundle} ({size})")
        except:
            print(f"✅ macOS应用构建成功: {app_bundle}")
        
        final_artifacts.append(app_bundle)
        build_successful = True
        
        # 创建DMG
        try:
            # 获取版本号
            version_file = PROJECT_ROOT / "VERSION"
            if version_file.exists():
                with open(version_file, 'r') as f:
                    version = f.read().strip()
            else:
                version = "1.0.0"
            
            # 获取架构信息（优先使用环境变量，用于GitHub Actions）
            arch = os.environ.get('BUILD_ARCH')
            if not arch:
                # 自动检测架构
                if os.uname().machine == "arm64":
                    arch = "silicon"  # 用户友好的Apple Silicon命名
                else:
                    arch = "intel"    # 用户友好的Intel命名
            dmg_name = f"md2docx-v{version}-macOS-{arch}.dmg"
            dmg_path = dist_dir / dmg_name
            
            # 检查是否有create-dmg
            result = subprocess.run(["which", "create-dmg"], capture_output=True)
            if result.returncode == 0:
                print("🔨 创建DMG...")
                subprocess.run([
                    "create-dmg", 
                    "--volname", f"Markdown to Word v{version}",
                    "--window-pos", "200", "120",
                    "--window-size", "600", "400", 
                    "--icon-size", "100",
                    "--icon", f"{app_name}.app", "175", "190",
                    "--hide-extension", f"{app_name}.app",
                    "--app-drop-link", "425", "190",
                    str(dmg_path),
                    str(app_bundle)
                ], check=True, capture_output=True)
                
                if dmg_path.exists():
                    print(f"✅ DMG创建成功: {dmg_path}")
                    final_artifacts.append(dmg_path)
            else:
                print("⚠️  create-dmg未安装，跳过DMG创建")
                print("   安装命令: brew install create-dmg")
                
        except Exception as e:
            print(f"⚠️  DMG创建失败: {e}")
            
    elif exe_path.exists():
        print(f"✅ 应用构建成功: {exe_path}")
        final_artifacts.append(exe_path)
        build_successful = True
    else:
        print("❌ 构建失败 - 找不到输出文件")
        sys.exit(1)
    
    # 构建成功后，清理临时文件
    if build_successful:
        print("\n🧹 清理临时构建文件...")
        
        # 复制最终产物到releases目录（如果需要）
        releases_dir = PROJECT_ROOT / "releases" / f"v{version if 'version' in locals() else '1.0.0'}"
        if not releases_dir.exists():
            releases_dir.mkdir(parents=True, exist_ok=True)
        
        for artifact in final_artifacts:
            if artifact.exists():
                # 如果是DMG文件，复制到releases目录
                if artifact.suffix == '.dmg':
                    import shutil as sh
                    target = releases_dir / artifact.name
                    sh.copy2(artifact, target)
                    print(f"📦 复制到releases: {target}")
        
        # 清理build目录
        if build_dir.exists():
            try:
                shutil.rmtree(build_dir)
                print(f"✅ 已清理: {build_dir}")
            except Exception as e:
                print(f"⚠️  无法清理build目录: {e}")
        
        # 清理PyInstaller生成的可执行文件目录（如果存在.app bundle）
        pyinstaller_dir = dist_dir / app_name
        if app_bundle.exists() and pyinstaller_dir.exists():
            try:
                shutil.rmtree(pyinstaller_dir)
                print(f"✅ 已清理: {pyinstaller_dir}")
            except Exception as e:
                print(f"⚠️  无法清理PyInstaller目录: {e}")
        
        # 清理.spec文件
        spec_file = packaging_dir / f"{app_name}.spec"
        if spec_file.exists():
            try:
                spec_file.unlink()
                print(f"✅ 已清理: {spec_file}")
            except Exception as e:
                print(f"⚠️  无法清理spec文件: {e}")
        
        print("✅ 临时文件清理完成")
    
    print(f"\n📁 构建产物位置: {dist_dir}")
    return True

if __name__ == "__main__":
    main()