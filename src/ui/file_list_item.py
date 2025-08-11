# -*- coding: utf-8 -*-
from pathlib import Path
from enum import Enum
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QListWidgetItem
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtGui import QFont, QCursor, QPainter, QPen

class ConversionStatus(Enum):
    """转换状态枚举"""
    PENDING = "pending"      # 未转换
    CONVERTING = "converting" # 转换中
    SUCCESS = "success"       # 转换成功
    FAILED = "failed"         # 转换失败

class DeleteButton(QPushButton):
    """自定义删除按钮，绘制X图形"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(16, 16)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.is_hovered = False
        
    def enterEvent(self, event):
        super().enterEvent(event)
        self.is_hovered = True
        self.update()
        
    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.is_hovered = False
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制背景圆形 - 更大的圆形
        if self.is_hovered:
            painter.setBrush(Qt.red)
        else:
            painter.setBrush(Qt.lightGray)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(1, 1, 14, 14)  # 从 2,2,12,12 改为 1,1,14,14
        
        # 绘制X - 更小的叉，不撑满圆形
        pen = QPen(Qt.white if self.is_hovered else Qt.darkGray)
        pen.setWidth(2)
        painter.setPen(pen)
        
        # 绘制两条对角线，留出边距
        painter.drawLine(6, 6, 10, 10)  # 从 5,5,11,11 改为 6,6,10,10
        painter.drawLine(10, 6, 6, 10)  # 从 11,5,5,11 改为 10,6,6,10

class FileListItemWidget(QWidget):
    """自定义文件列表项组件，支持悬停删除功能"""
    
    delete_requested = Signal(str)  # 删除请求信号，传递文件路径
    
    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.file_name = Path(file_path).name
        self.status = ConversionStatus.PENDING  # 初始状态为未转换
        
        # 转换中动画定时器
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_frame = 0
        
        self.setup_ui()
        self.setMouseTracking(True)  # 启用鼠标跟踪
    
    def setup_ui(self):
        """设置UI组件"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)
        
        # 状态图标标签
        self.status_label = QLabel()
        self.status_label.setFixedSize(16, 16)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label, 0, Qt.AlignVCenter)
        
        # 文件名称 - 增大字号
        self.file_label = QLabel(self.file_name)
        label_font = QFont()
        label_font.setPointSize(13)  # 从11增加到13
        self.file_label.setFont(label_font)
        self.file_label.setStyleSheet("color: #333; background: transparent;")
        layout.addWidget(self.file_label)
        
        # 更新状态显示
        self._update_status_display()
        
        # 弹性空间
        layout.addStretch()
        
        # 删除按钮（初始隐藏）- 使用自定义绘制的按钮
        self.delete_btn = DeleteButton()
        self.delete_btn.setStyleSheet("background: transparent; border: none;")
        self.delete_btn.clicked.connect(self.on_delete_clicked)
        self.delete_btn.setVisible(False)  # 初始隐藏
        
        layout.addWidget(self.delete_btn, 0, Qt.AlignVCenter)
        
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
        self._is_hovered = True
        self.delete_btn.setVisible(True)
        self.update_style()
    
    def leaveEvent(self, event):
        """鼠标离开事件"""
        super().leaveEvent(event)
        self._is_hovered = False
        self.delete_btn.setVisible(False)
        self.update_style()
    
    def on_delete_clicked(self):
        """删除按钮点击事件"""
        self.delete_requested.emit(self.file_path)
    
    def set_status(self, status: ConversionStatus):
        """设置转换状态"""
        self.status = status
        self._update_status_display()
        
        # 管理动画定时器
        if status == ConversionStatus.CONVERTING:
            self.animation_timer.start(500)  # 每500ms更新一次动画
        else:
            self.animation_timer.stop()
            self.animation_frame = 0
    
    def get_status(self) -> ConversionStatus:
        """获取当前转换状态"""
        return self.status
    
    def _update_status_display(self):
        """更新状态显示"""
        if self.status == ConversionStatus.PENDING:
            self.status_label.setText("📄")
            self.status_label.setToolTip("待转换")
            self.file_label.setStyleSheet("color: #333; background: transparent;")
        elif self.status == ConversionStatus.CONVERTING:
            # 转换中使用动画图标
            animation_icons = ["⏳", "⏰", "⏱️", "⏲️"]
            icon = animation_icons[self.animation_frame % len(animation_icons)]
            self.status_label.setText(icon)
            self.status_label.setToolTip("转换中...")
            self.file_label.setStyleSheet("color: #007acc; background: transparent;")
        elif self.status == ConversionStatus.SUCCESS:
            self.status_label.setText("✅")
            self.status_label.setToolTip("转换成功")
            self.file_label.setStyleSheet("color: #666; background: transparent;")
        elif self.status == ConversionStatus.FAILED:
            self.status_label.setText("❌")
            self.status_label.setToolTip("转换失败")
            self.file_label.setStyleSheet("color: #ff4757; background: transparent;")
    
    def _update_animation(self):
        """更新转换中动画"""
        self.animation_frame += 1
        if self.status == ConversionStatus.CONVERTING:
            self._update_status_display()
    
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
        self.setSizeHint(QSize(400, 36))  # 保持原始高度
    
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
    
    def set_status(self, status: ConversionStatus):
        """设置转换状态"""
        if self.widget:
            self.widget.set_status(status)
    
    def get_status(self) -> ConversionStatus:
        """获取当前转换状态"""
        if self.widget:
            return self.widget.get_status()
        return ConversionStatus.PENDING