#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图标状态检查工具
检查应用程序图标的完整性和可用性
"""

import sys
from pathlib import Path

# 添加src路径
sys.path.append(str(Path(__file__).parent / "src"))

from utils.icon_manager import icon_manager

def main():
    print("🎨 应用程序图标状态检查")
    print("=" * 50)
    
    # 1. 检查图标目录是否存在
    print(f"📁 图标目录: {icon_manager.icon_dir}")
    if icon_manager.icon_dir.exists():
        print("   ✅ 图标目录存在")
    else:
        print("   ❌ 图标目录不存在")
        return
    
    # 2. 检查主图标
    main_icon = icon_manager.icon_dir / "app_icon.png"
    print(f"\n🖼️  主图标: {main_icon}")
    if main_icon.exists():
        print("   ✅ 主图标存在")
    else:
        print("   ❌ 主图标不存在")
    
    # 3. 检查PNG图标目录
    print(f"\n📂 PNG图标目录: {icon_manager.png_dir}")
    if icon_manager.png_dir.exists():
        print("   ✅ PNG图标目录存在")
        
        # 检查各种尺寸
        print("\n📏 图标尺寸检查:")
        for size in icon_manager.icon_sizes:
            icon_path = icon_manager.png_dir / f"icon_{size}.png"
            status = "✅" if icon_path.exists() else "❌"
            print(f"   {status} {size}x{size} px")
    else:
        print("   ❌ PNG图标目录不存在")
    
    # 4. 检查SVG图标目录
    svg_dir = icon_manager.icon_dir / "svg"
    print(f"\n🎭 SVG图标目录: {svg_dir}")
    if svg_dir.exists():
        print("   ✅ SVG图标目录存在")
        svg_icon = svg_dir / "app_icon.svg"
        if svg_icon.exists():
            print("   ✅ SVG图标存在")
        else:
            print("   ❌ SVG图标不存在")
    else:
        print("   ❌ SVG图标目录不存在")
    
    # 5. 检查ICO文件
    ico_file = icon_manager.icon_dir / "app_icon.ico"
    print(f"\n🪟 ICO文件: {ico_file}")
    if ico_file.exists():
        print("   ✅ ICO文件存在")
    else:
        print("   ❌ ICO文件不存在")
    
    # 6. 功能测试
    print(f"\n🔧 功能测试:")
    print(f"   图标存在: {'✅' if icon_manager.icon_exists() else '❌'}")
    
    missing_sizes = icon_manager.get_missing_sizes()
    if missing_sizes:
        print(f"   缺失尺寸: {missing_sizes}")
    else:
        print(f"   ✅ 所有尺寸完整")
    
    # 7. 设计建议
    print(f"\n💡 设计建议:")
    print("   1. 创建主图标 app_icon.png (512x512)")
    print("   2. 创建多尺寸PNG图标 (16, 24, 32, 48, 64, 128, 256, 512)")
    print("   3. 创建ICO文件用于Windows兼容性")
    print("   4. 可选: 创建SVG矢量图标")
    
    print(f"\n🎯 推荐工具:")
    print("   - Adobe Illustrator (矢量设计)")
    print("   - Figma (界面设计)")
    print("   - GIMP (免费位图编辑)")
    print("   - ImageMagick (批量转换)")
    print("   - ICO Convert (在线ICO转换)")

if __name__ == "__main__":
    main()