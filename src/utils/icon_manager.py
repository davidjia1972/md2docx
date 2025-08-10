# -*- coding: utf-8 -*-
import os
from pathlib import Path
from typing import Optional
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QSize

class IconManager:
    """图标管理器，处理应用程序图标的加载和使用"""
    
    def __init__(self):
        # 图标目录路径
        self.icon_dir = Path(__file__).parent.parent.parent / "assets" / "icons"
        self.png_dir = self.icon_dir / "png"
        
        # 常用尺寸
        self.icon_sizes = [16, 24, 32, 48, 64, 128, 256, 512]
    
    
    def get_multi_size_icon(self) -> Optional[QIcon]:
        """
        获取包含多种尺寸的图标
        适用于系统托盘、窗口图标等需要自适应尺寸的场景
        为macOS优化，优先使用高分辨率图标
        
        Returns:
            包含多种尺寸的QIcon对象
        """
        icon = QIcon()
        
        # macOS程序坞特别需要的尺寸（按优先级排序）
        priority_sizes = [128, 256, 512, 64, 48, 32, 24, 16]
        
        # 首先添加高优先级尺寸
        for size in priority_sizes:
            if size in self.icon_sizes:
                icon_path = self.png_dir / f"icon_{size}.png"
                if icon_path.exists():
                    pixmap = QPixmap(str(icon_path))
                    # 确保pixmap质量
                    if not pixmap.isNull():
                        icon.addPixmap(pixmap, QIcon.Normal, QIcon.Off)
        
        # 添加剩余尺寸
        for size in self.icon_sizes:
            if size not in priority_sizes:
                icon_path = self.png_dir / f"icon_{size}.png"
                if icon_path.exists():
                    pixmap = QPixmap(str(icon_path))
                    if not pixmap.isNull():
                        icon.addPixmap(pixmap, QIcon.Normal, QIcon.Off)
        
        # 如果没有找到任何PNG图标，尝试主图标
        if icon.isNull():
            main_icon_path = self.icon_dir / "app_icon.png"
            if main_icon_path.exists():
                main_pixmap = QPixmap(str(main_icon_path))
                if not main_pixmap.isNull():
                    icon = QIcon(main_pixmap)
        
        return icon if not icon.isNull() else None
    
    def get_window_icon(self) -> Optional[QIcon]:
        """
        获取窗口图标
        优先使用32px，回退到其他尺寸
        """
        return self.get_multi_size_icon()
    
    
    

# 全局图标管理器实例
icon_manager = IconManager()