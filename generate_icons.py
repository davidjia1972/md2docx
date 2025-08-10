#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图标生成脚本
从主图标生成多种尺寸的图标

使用方法:
1. 将你的主图标(512x512)保存为 assets/icons/app_icon.png
2. 安装Pillow: pip install Pillow
3. 运行此脚本: python generate_icons.py

注意: 此脚本需要你首先创建主图标文件
"""

import sys
from pathlib import Path

def generate_icons():
    try:
        from PIL import Image
    except ImportError:
        print("❌ 需要安装Pillow库: pip install Pillow")
        return False
    
    # 路径设置
    icon_dir = Path(__file__).parent / "assets" / "icons"
    png_dir = icon_dir / "png"
    main_icon_path = icon_dir / "app_icon.png"
    
    # 检查主图标是否存在
    if not main_icon_path.exists():
        print(f"❌ 主图标不存在: {main_icon_path}")
        print("请先创建 512x512 的主图标 app_icon.png")
        return False
    
    print("🎨 开始生成多尺寸图标...")
    print(f"📁 源图标: {main_icon_path}")
    
    # 确保目录存在
    png_dir.mkdir(parents=True, exist_ok=True)
    
    # 加载主图标
    try:
        main_image = Image.open(main_icon_path)
        print(f"✅ 加载主图标: {main_image.size}")
    except Exception as e:
        print(f"❌ 无法加载主图标: {e}")
        return False
    
    # 生成各种尺寸
    sizes = [16, 24, 32, 48, 64, 128, 256, 512]
    success_count = 0
    
    for size in sizes:
        try:
            # 调整尺寸
            resized = main_image.resize((size, size), Image.Resampling.LANCZOS)
            
            # 保存文件
            output_path = png_dir / f"icon_{size}.png"
            resized.save(output_path, "PNG")
            
            print(f"✅ 生成 {size}x{size}: {output_path}")
            success_count += 1
            
        except Exception as e:
            print(f"❌ 生成 {size}x{size} 失败: {e}")
    
    print(f"\n🎯 完成! 成功生成 {success_count}/{len(sizes)} 个图标")
    
    # 生成ICO文件（可选）
    try:
        ico_path = icon_dir / "app_icon.ico"
        # ICO文件包含多个尺寸
        ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48)]
        ico_images = []
        
        for width, height in ico_sizes:
            ico_image = main_image.resize((width, height), Image.Resampling.LANCZOS)
            ico_images.append(ico_image)
        
        # 保存ICO文件
        ico_images[0].save(ico_path, format='ICO', sizes=ico_sizes)
        print(f"✅ 生成ICO文件: {ico_path}")
        
    except Exception as e:
        print(f"❌ 生成ICO文件失败: {e}")
    
    return True

def main():
    print("🚀 图标生成工具")
    print("=" * 50)
    
    # 检查主图标
    main_icon_path = Path(__file__).parent / "assets" / "icons" / "app_icon.png"
    
    if not main_icon_path.exists():
        print("⚠️  未找到主图标文件")
        print(f"请创建主图标: {main_icon_path}")
        print("\n📝 设计要求:")
        print("   - 尺寸: 512x512 像素")
        print("   - 格式: PNG")
        print("   - 背景: 透明")
        print("   - 主题: Markdown → DOCX 转换")
        print("   - 颜色: 蓝色系 (#007acc)")
        print("\n💡 设计元素建议:")
        print("   - Markdown符号 (# * [])")
        print("   - 文档图标")
        print("   - 转换箭头")
        print("   - 简洁几何图形")
        return
    
    # 开始生成
    if generate_icons():
        print("\n✅ 图标生成完成!")
        print("可以运行 python check_icons.py 检查结果")
    else:
        print("\n❌ 图标生成失败")

if __name__ == "__main__":
    main()