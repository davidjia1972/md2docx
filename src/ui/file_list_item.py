# -*- coding: utf-8 -*-
from pathlib import Path
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QListWidgetItem
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QCursor

class FileListItemWidget(QWidget):
    """自定义文件列表项组件，支持悬停删除功能"""
    
    delete_requested = Signal(str)  # 删除请求信号，传递文件路径
    
    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.file_name = Path(file_path).name
        
        self.setup_ui()
        self.setMouseTracking(True)  # 启用鼠标跟踪
    
    def setup_ui(self):
        """设置UI组件"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(10)
        
        # 文件图标和名称 - 增大字号
        self.file_label = QLabel(f"📄 {self.file_name}")
        label_font = QFont()
        label_font.setPointSize(13)  # 从11增加到13
        self.file_label.setFont(label_font)
        self.file_label.setStyleSheet("color: #333; background: transparent;")
        layout.addWidget(self.file_label)
        
        # 弹性空间
        layout.addStretch()
        
        # 删除按钮（初始隐藏）- 改为带X的圆形按钮
        self.delete_btn = QPushButton("×")
        self.delete_btn.setFixedSize(20, 20)  # 从24x24缩小到20x20
        from utils.i18n_manager import t
        self.delete_btn.setToolTip(t("tooltips.delete_from_list"))
        self.delete_btn.setCursor(QCursor(Qt.PointingHandCursor))  # 设置手形光标
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4757;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff3742;
            }
            QPushButton:pressed {
                background-color: #ff2d3a;
            }
        """)
        self.delete_btn.clicked.connect(self.on_delete_clicked)
        self.delete_btn.setVisible(False)  # 初始隐藏
        
        layout.addWidget(self.delete_btn)
        
        # 初始化样式状态
        self._is_hovered = False
        self.update_style()
    
    def update_style(self):
        """更新样式"""
        if self._is_hovered:
            # 悬停状态 - 淡蓝色背景
            self.setStyleSheet("""
                FileListItemWidget {
                    background-color: #f0f8ff;
                    border: none;
                    border-radius: 4px;
                    padding: 2px;
                }
            """)
            self.file_label.setStyleSheet("color: #333; background: transparent;")
        else:
            # 正常状态 - 透明背景
            self.setStyleSheet("""
                FileListItemWidget {
                    background-color: transparent;
                    border: none;
                    border-radius: 4px;
                    padding: 2px;
                }
            """)
            self.file_label.setStyleSheet("color: #333; background: transparent;")
    
    def enterEvent(self, event):
        """鼠标进入事件"""
        super().enterEvent(event)
        print(f"鼠标进入: {self.file_name}")  # 调试信息
        self._is_hovered = True
        self.delete_btn.setVisible(True)
        self.update_style()
    
    def leaveEvent(self, event):
        """鼠标离开事件"""
        super().leaveEvent(event)
        print(f"鼠标离开: {self.file_name}")  # 调试信息
        self._is_hovered = False
        self.delete_btn.setVisible(False)
        self.update_style()
    
    def on_delete_clicked(self):
        """删除按钮点击事件"""
        self.delete_requested.emit(self.file_path)
    
    def sizeHint(self):
        """返回建议的尺寸"""
        return QSize(400, 36)  # 增加高度以适应更大的字体


class FileListItem(QListWidgetItem):
    """自定义文件列表项，用于包装FileListItemWidget"""
    
    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.widget = None
        
        # 设置项目数据
        self.setData(Qt.UserRole, file_path)
        self.setToolTip(file_path)
        
        # 设置项目尺寸
        self.setSizeHint(QSize(400, 40))  # 增加高度
    
    def create_widget(self, list_widget):
        """创建并返回自定义widget"""
        if self.widget is None:
            self.widget = FileListItemWidget(self.file_path)
            # 连接删除信号到列表widget
            if hasattr(list_widget, 'remove_file'):
                self.widget.delete_requested.connect(list_widget.remove_file)
        
        return self.widget
    
    def get_file_path(self):
        """获取文件路径"""
        return self.file_path