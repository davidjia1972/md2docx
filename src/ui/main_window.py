# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path
from typing import List, Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QListWidget, QListWidgetItem, QPushButton, QCheckBox, 
    QComboBox, QButtonGroup, QRadioButton, QGroupBox,
    QFileDialog, QMessageBox, QProgressBar, QTextEdit,
    QSplitter, QFrame, QMenu
)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QDragEnterEvent, QDropEvent, QPixmap

# Import core modules
from converter.batch_converter import get_conversion_manager, ConversionQuality
from converter.pandoc_wrapper import pandoc
from templates.template_manager import get_template_manager
from utils.file_scanner import quick_scan
from utils.config_manager import get_config
from utils.icon_manager import icon_manager
from utils.i18n_manager import i18n, t
from utils.emoji_processor import emoji_processor, cleanup_orphaned_temp_files
from ui.file_list_item import FileListItem, FileListItemWidget

class DropArea(QFrame):
    """Drag and drop area component"""
    
    files_dropped = Signal(list)  # File drop signal
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setFrameStyle(QFrame.NoFrame)  # Explicitly no frame style
        self.setStyleSheet("""
            DropArea {
                border: 2px dashed #aaa;
                border-radius: 10px;
                background-color: #f9f9f9;
                min-height: 192px;
            }
            DropArea:hover {
                border-color: #007acc;
                background-color: #f0f8ff;
            }
        """)
        
        # Setup UI - simplified without icon
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        self.text_label = QLabel(t("ui.drag_drop.text"))
        self.text_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        self.text_label.setFont(font)
        self.text_label.setStyleSheet("color: #666; border: none; background: transparent;")
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.select_files_btn = QPushButton(t("ui.drag_drop.select_files"))
        self.select_files_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:pressed {
                background-color: #2a5d8f;
            }
        """)
        
        self.select_dir_btn = QPushButton(t("ui.drag_drop.select_folder"))
        self.select_dir_btn.setStyleSheet("""
            QPushButton {
                background-color: #50c878;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3eb370;
            }
            QPushButton:pressed {
                background-color: #2d8a5b;
            }
        """)
        
        button_layout.addWidget(self.select_files_btn)
        button_layout.addWidget(self.select_dir_btn)
        
        layout.addWidget(self.text_label)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def update_texts(self):
        """Update text labels for language change"""
        self.text_label.setText(t("ui.drag_drop.text"))
        self.select_files_btn.setText(t("ui.drag_drop.select_files"))
        self.select_dir_btn.setText(t("ui.drag_drop.select_folder"))
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                DropArea {
                    border: 2px solid #007acc;
                    border-radius: 10px;
                    background-color: #e6f3ff;
                    min-height: 192px;
                }
            """)
    
    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            DropArea {
                border: 2px dashed #aaa;
                border-radius: 10px;
                background-color: #f9f9f9;
                min-height: 192px;
            }
            DropArea:hover {
                border-color: #007acc;
                background-color: #f0f8ff;
            }
        """)
    
    def dropEvent(self, event: QDropEvent):
        files = []
        for url in event.mimeData().urls():
            files.append(url.toLocalFile())
        
        if files:
            self.files_dropped.emit(files)
        
        self.dragLeaveEvent(event)
        event.acceptProposedAction()

class MainWindow(QMainWindow):
    """Main window interface"""
    
    def __init__(self):
        super().__init__()
        self.markdown_files = []
        self.setup_ui()
        self.connect_signals()
        self.load_settings()
        
        # Pandoc check will be done in showEvent
        self._pandoc_checked = False
    
    def showEvent(self, event):
        """窗口显示事件 - 在窗口真正显示后检查pandoc"""
        super().showEvent(event)
        
        # 强制窗口置顶和激活
        self.raise_()
        self.activateWindow()
        
        # 只检查一次pandoc
        if not self._pandoc_checked:
            self._pandoc_checked = True
            # 使用QTimer延迟一点，确保窗口完全显示
            from PySide6.QtCore import QTimer
            QTimer.singleShot(100, self.check_pandoc_availability)
    
    def setup_ui(self):
        """Setup user interface"""
        self.setWindowTitle("Markdown to Word")
        self.setMinimumSize(760, 750)
        self.resize(760, 750)
        
        # Set window icon
        window_icon = icon_manager.get_window_icon()
        if window_icon:
            self.setWindowIcon(window_icon)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        self.title_label = QLabel(t("app.name"))
        self.title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #333; margin-bottom: 10px;")
        self.title_label.setFixedHeight(30)  # Fix title height
        main_layout.addWidget(self.title_label)
        
        # Drop area
        self.drop_area = DropArea()
        # Allow drop area to expand vertically
        from PySide6.QtWidgets import QSizePolicy
        self.drop_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.drop_area, 2)  # Stretch factor of 2
        
        # Add some space
        main_layout.addSpacing(3)
        
        # Recursive option
        self.recursive_checkbox = QCheckBox("Recursively search for Markdown files in subdirectories")
        self.recursive_checkbox.setChecked(True)
        self.recursive_checkbox.setFixedHeight(20)  # Fix checkbox height
        main_layout.addWidget(self.recursive_checkbox)
        
        # Add some space
        main_layout.addSpacing(5)
        
        # Convert button - moved here above file list
        convert_button_layout = QHBoxLayout()
        self.convert_btn = QPushButton(t("ui.buttons.start"))
        self.convert_btn.setFixedHeight(40)
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004080;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #999;
            }
        """)
        convert_button_layout.addWidget(self.convert_btn)
        main_layout.addLayout(convert_button_layout)
        
        # Add some space after button
        main_layout.addSpacing(8)
        
        # File list header with clear button
        files_header_layout = QHBoxLayout()
        
        self.files_label = QLabel(t("ui.labels.files_to_convert"))
        files_font = QFont()
        files_font.setPointSize(12)
        files_font.setBold(True)
        self.files_label.setFont(files_font)
        self.files_label.setFixedHeight(20)  # Fix label height
        
        # Clear list button
        self.clear_list_btn = QPushButton(t("ui.buttons.clear_list"))
        self.clear_list_btn.setFixedHeight(24)
        self.clear_list_btn.setMaximumWidth(80)
        self.clear_list_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #666;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 2px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
                color: #333;
            }
            QPushButton:pressed {
                background-color: #ddd;
            }
        """)
        self.clear_list_btn.clicked.connect(self.clear_file_list)
        
        files_header_layout.addWidget(self.files_label)
        files_header_layout.addStretch()  # Push clear button to the right
        files_header_layout.addWidget(self.clear_list_btn)
        
        main_layout.addLayout(files_header_layout)
        
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(100)  # Set minimum height instead of maximum
        # Allow file list to expand vertically
        self.file_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Enable right-click context menu
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_file_context_menu)
        
        # Set file list styles with working hover effects
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
                outline: none;
            }
            QListWidget::item {
                padding: 8px 12px;
                margin: 1px 0px;
                border-radius: 4px;
                color: #333;
                background-color: transparent;
                border: none;
            }
            QListWidget::item:hover {
                background-color: #f0f8ff;
                color: #333;
            }
            QListWidget::item:selected {
                background-color: #007acc;
                color: white;
            }
            QListWidget::item:selected:hover {
                background-color: #0066cc;
                color: white;
            }
        """)
        main_layout.addWidget(self.file_list, 1)  # Stretch factor of 1
        
        # File statistics
        self.file_count_label = QLabel(t("ui.labels.file_stats", count=0))
        self.file_count_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        self.file_count_label.setFixedHeight(20)  # Fix stats label height
        main_layout.addWidget(self.file_count_label)
        
        # Add some space before settings
        main_layout.addSpacing(5)
        
        # Settings group
        self.settings_group = QGroupBox(t("ui.labels.conversion_settings"))
        self.settings_group.setFixedHeight(120)  # Fix settings group height
        settings_layout = QVBoxLayout(self.settings_group)
        settings_layout.setSpacing(8)
        
        # Create 4-column grid layout for responsive design
        settings_grid = QGridLayout()
        
        # === Create control groups for each cell ===
        
        # Row 0, Column 0: Template control group
        template_container = QWidget()
        template_layout = QHBoxLayout(template_container)
        template_layout.setContentsMargins(0, 0, 0, 0)
        template_layout.setSpacing(5)
        
        self.template_label = QLabel(t("ui.labels.template"))
        
        # Create a container widget for template ComboBox with arrow
        combo_container = QWidget()
        combo_container_layout = QHBoxLayout(combo_container)
        combo_container_layout.setContentsMargins(0, 0, 0, 0)
        combo_container_layout.setSpacing(0)
        
        self.template_combo = QComboBox()
        self.template_combo.setMinimumWidth(200)
        # 设置下拉列表的尺寸策略
        self.template_combo.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        # Simple ComboBox style without arrow
        self.template_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 3px 0px 0px 3px;
                padding: 5px 8px;
                color: black;
                min-height: 18px;
            }
            QComboBox:hover {
                border-color: #007acc;
            }
            QComboBox:focus {
                border-color: #007acc;
                outline: none;
            }
            QComboBox::drop-down {
                width: 0px;
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #ccc;
                selection-background-color: #007acc;
                selection-color: white;
                outline: none;
                min-width: 220px;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px;
                border: none;
                color: black;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #007acc;
                color: white;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #e6f3ff;
                color: black;
            }
        """)
        
        # Arrow indicator label with click functionality
        arrow_label = QLabel("▼")
        arrow_label.setFixedSize(20, 28)
        arrow_label.setAlignment(Qt.AlignCenter)
        arrow_label.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-left: none;
                border-radius: 0px 3px 3px 0px;
                color: #666;
                font-size: 10px;
            }
            QLabel:hover {
                background-color: #e8e8e8;
                color: #333;
            }
        """)
        
        # Make arrow label clickable to show dropdown
        def on_arrow_clicked(event):
            self.template_combo.showPopup()
        
        arrow_label.mousePressEvent = on_arrow_clicked
        
        combo_container_layout.addWidget(self.template_combo)
        combo_container_layout.addWidget(arrow_label)
        
        self.browse_template_btn = QPushButton(t("ui.buttons.browse"))
        
        template_layout.addWidget(self.template_label)
        template_layout.addWidget(combo_container)
        template_layout.addWidget(self.browse_template_btn)
        
        # Row 0, Column 2: Language control group
        language_container = QWidget()
        language_layout = QHBoxLayout(language_container)
        language_layout.setContentsMargins(0, 0, 0, 0)
        language_layout.setSpacing(5)
        
        self.language_label = QLabel(t("ui.labels.language"))
        
        self.language_combo = QComboBox()
        self.language_combo.setMinimumWidth(150)
        self.language_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px 8px;
                color: black;
                min-height: 18px;
            }
            QComboBox:hover {
                border-color: #007acc;
            }
            QComboBox:focus {
                border-color: #007acc;
                outline: none;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #ccc;
                border-left-style: solid;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #666;
                width: 0px;
                height: 0px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #ccc;
                selection-background-color: #007acc;
                selection-color: white;
                outline: none;
                min-width: 170px;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px;
                border: none;
                color: black;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #007acc;
                color: white;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #e6f3ff;
                color: black;
            }
        """)
        
        language_layout.addWidget(self.language_label)
        language_layout.addWidget(self.language_combo)
        
        # Row 1, Column 0: File handling control group
        file_handling_container = QWidget()
        file_handling_layout = QHBoxLayout(file_handling_container)
        file_handling_layout.setContentsMargins(0, 0, 0, 0)
        file_handling_layout.setSpacing(5)
        
        self.file_handling_label = QLabel(t("ui.labels.file_handling"))
        
        self.overwrite_radio = QRadioButton(t("ui.options.overwrite"))
        self.auto_rename_radio = QRadioButton(t("ui.options.auto_rename"))
        self.auto_rename_radio.setChecked(True)  # Default to auto rename
        
        # Keep timestamp and increment radio buttons for future use, but don't show them
        self.timestamp_radio = QRadioButton("Timestamp suffix")
        self.increment_radio = QRadioButton("Number suffix")
        self.timestamp_radio.setChecked(True)  # Default to timestamp naming
        
        # Add button groups
        self.handling_group = QButtonGroup()
        self.handling_group.addButton(self.overwrite_radio)
        self.handling_group.addButton(self.auto_rename_radio)
        
        self.naming_group = QButtonGroup()
        self.naming_group.addButton(self.timestamp_radio)
        self.naming_group.addButton(self.increment_radio)
        
        file_handling_layout.addWidget(self.file_handling_label)
        file_handling_layout.addWidget(self.overwrite_radio)
        file_handling_layout.addWidget(self.auto_rename_radio)
        file_handling_layout.addStretch()  # 显式添加右侧拉伸，确保控件左对齐紧凑排列
        
        # Row 1, Column 2: Emoji removal option
        self.remove_emoji_checkbox = QCheckBox(t("ui.options.remove_emoji"))
        self.remove_emoji_checkbox.setToolTip(t("ui.tooltips.remove_emoji"))
        self.remove_emoji_checkbox.setChecked(True)  # Default enabled as requested
        self.remove_emoji_checkbox.setMinimumWidth(150)  # Match language combo width
        
        # === Add widgets to grid layout ===
        settings_grid.addWidget(template_container, 0, 0)      # Row 0, Col 0: Template group
        settings_grid.addWidget(language_container, 0, 2)      # Row 0, Col 2: Language group
        settings_grid.addWidget(file_handling_container, 1, 0) # Row 1, Col 0: File handling group
        settings_grid.addWidget(self.remove_emoji_checkbox, 1, 2) # Row 1, Col 2: Emoji option
        
        # === Configure column stretch behavior ===
        settings_grid.setColumnStretch(0, 0)  # Column 0: content-driven width
        settings_grid.setColumnStretch(1, 0)  # Column 1: fixed spacing, no stretch
        settings_grid.setColumnStretch(2, 0)  # Column 2: content-driven width
        settings_grid.setColumnStretch(3, 1)  # Column 3: absorbs all extra space
        
        # Set fixed spacing for column 1
        settings_grid.setColumnMinimumWidth(1, 30)  # 30px spacing between left and right groups
        
        settings_layout.addLayout(settings_grid)
        main_layout.addWidget(self.settings_group)
        
        # Add some space before buttons
        main_layout.addSpacing(5)
        
        # Convert button and progress
        bottom_layout = QVBoxLayout()
        
        # Create cancel button (will be added to status layout later)
        self.cancel_btn = QPushButton(t("ui.buttons.cancel"))
        self.cancel_btn.setMinimumSize(80, 30)
        self.cancel_btn.setVisible(False)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFA500;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF8C00;
            }
            QPushButton:pressed {
                background-color: #FF7F00;
            }
        """)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(20)  # Fix progress bar height
        bottom_layout.addWidget(self.progress_bar)
        
        # Status label and cancel button layout
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_label.setStyleSheet("color: #666; margin: 5px;")
        self.status_label.setFixedHeight(35)  # Increased height for better alignment
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.cancel_btn)
        
        bottom_layout.addLayout(status_layout)
        
        main_layout.addLayout(bottom_layout)
        
        # Remove addStretch as drop area and file list now handle expansion
    
    def connect_signals(self):
        """Connect signals and slots"""
        # Drop area
        self.drop_area.files_dropped.connect(self.handle_dropped_files)
        self.drop_area.select_files_btn.clicked.connect(self.select_files)
        self.drop_area.select_dir_btn.clicked.connect(self.select_directory)
        
        # File list
        self.recursive_checkbox.toggled.connect(self.on_recursive_changed)
        
        # File handling options
        self.overwrite_radio.toggled.connect(self.on_file_handling_changed)
        self.auto_rename_radio.toggled.connect(self.on_file_handling_changed)
        
        # Emoji removal option
        self.remove_emoji_checkbox.toggled.connect(self.on_emoji_removal_changed)
        
        # Template
        self.template_combo.currentTextChanged.connect(self.on_template_changed)
        self.browse_template_btn.clicked.connect(self.browse_template)
        
        # Language
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        
        # Conversion
        self.convert_btn.clicked.connect(self.start_conversion)
        self.cancel_btn.clicked.connect(self.cancel_conversion)
        
        # Conversion manager signals (lazy initialization)
        conversion_manager = get_conversion_manager()
        conversion_manager.converter.conversion_started.connect(self.on_conversion_started)
        conversion_manager.converter.conversion_finished.connect(self.on_conversion_finished)
        conversion_manager.converter.error_occurred.connect(self.on_conversion_error)
        
        # Progress tracking
        progress_tracker = conversion_manager.get_progress_tracker()
        progress_tracker.progress_updated.connect(self.on_progress_updated)
        progress_tracker.task_started.connect(self.on_task_started)
        progress_tracker.task_completed.connect(self.on_task_completed)
        progress_tracker.batch_started.connect(self.on_batch_started)
        progress_tracker.batch_completed.connect(self.on_batch_completed)
        progress_tracker.time_estimated.connect(self.on_time_estimated)
    
    def load_settings(self):
        """Load settings"""
        config = get_config()
        
        # Load recursive setting
        recursive = config.get("ui.recursive_scan", True)
        self.recursive_checkbox.setChecked(recursive)
        
        # Load output settings
        output_settings = config.get_output_settings()
        overwrite = output_settings.get("overwrite_files", False)
        naming_strategy = output_settings.get("naming_strategy", "timestamp")
        remove_emoji = output_settings.get("remove_emoji", True)
        
        if overwrite:
            self.overwrite_radio.setChecked(True)
        else:
            self.auto_rename_radio.setChecked(True)
            
        self.remove_emoji_checkbox.setChecked(remove_emoji)
        
        if naming_strategy == "timestamp":
            self.timestamp_radio.setChecked(True)
        else:
            self.increment_radio.setChecked(True)
        
        # Load template list
        self.refresh_template_list()
        
        # Load language list
        self.refresh_language_list()
        
        # Connect language change signal
        i18n.language_changed.connect(self.on_ui_language_changed)
        
        # Apply user's saved language setting and sync UI
        self._apply_saved_language_setting()
    
    def _apply_saved_language_setting(self):
        """Apply saved language setting and sync UI"""
        try:
            config = get_config()
            saved_language = config.get_language_setting()
            
            if saved_language and saved_language != "auto":
                # Set specific language
                i18n.set_language(saved_language)
            else:
                # Use current auto-detected language and make sure UI is synced
                # Trigger UI update even if language doesn't change
                self.update_ui_texts()
                self.update_language_list_texts()
                
        except Exception as e:
            # Keep critical error information for debugging
            import traceback
            traceback.print_exc()
    
    def refresh_template_list(self):
        """Refresh template list"""
        try:
            self.template_combo.clear()
            
            template_manager = get_template_manager()
            templates = template_manager.get_all_templates()
            
            if not templates:
                self.template_combo.addItem(t("templates.no_templates"))
                return
            
            for template in templates:
                display_name = template["name"]
                if template["type"] == "builtin":
                    display_name += " (Built-in)"
                
                # Use template path if available, otherwise use None
                template_path = template.get("path")
                self.template_combo.addItem(display_name, template_path)
        
        except Exception as e:
            self.template_combo.addItem(t("templates.error_loading"))
        
        # Select default template
        default_template = template_manager.get_default_template_path()
        if default_template:
            for i in range(self.template_combo.count()):
                if self.template_combo.itemData(i) == default_template:
                    self.template_combo.setCurrentIndex(i)
                    break
    
    def refresh_language_list(self):
        """Refresh language list"""
        try:
            # Temporarily disconnect signal to prevent triggering on_language_changed
            self.language_combo.currentTextChanged.disconnect()
            
            self.language_combo.clear()
            
            # Add auto-detect option
            self.language_combo.addItem(t("ui.options.auto_detect_language"), "auto")
            
            # Add available languages
            available_languages = i18n.get_available_languages()
            for lang_code, lang_info in available_languages.items():
                display_name = lang_info['native_name']
                self.language_combo.addItem(display_name, lang_code)
            
            # Select current language
            config = get_config()
            saved_language = config.get_language_setting()
            if saved_language == "auto":
                self.language_combo.setCurrentIndex(0)
            else:
                for i in range(1, self.language_combo.count()):  # Skip auto option
                    if self.language_combo.itemData(i) == saved_language:
                        self.language_combo.setCurrentIndex(i)
                        break
            
            # Reconnect signal
            self.language_combo.currentTextChanged.connect(self.on_language_changed)
                        
        except Exception as e:
            # Keep critical error for debugging
            import traceback
            traceback.print_exc()
            self.language_combo.addItem(t("tooltips.language_load_failed"), None)
            # Make sure to reconnect signal even if error occurred
            try:
                self.language_combo.currentTextChanged.connect(self.on_language_changed)
            except:
                pass
    
    def on_language_changed(self):
        """Language selection changed"""
        selected_data = self.language_combo.currentData()
        if selected_data is None:
            return
            
        # Save language setting
        config = get_config()
        config.set_language_setting(selected_data)
        
        # Apply language change
        if selected_data == "auto":
            # Re-detect system language
            i18n._auto_detect_system_language()
            detected_lang = i18n.get_current_language()
            
            # Always update UI when switching to auto-detect, even if language is the same
            success = i18n.set_language(detected_lang)
            if success:
                # Force UI update for auto-detect mode
                self.update_ui_texts()
                self.update_language_list_texts()
                self._update_qt_translator(detected_lang)
        else:
            # Set specific language
            success = i18n.set_language(selected_data)
            if success:
                self._update_qt_translator(selected_data)
    
    def _update_qt_translator(self, language_code):
        """Update Qt translator for application UI (native dialogs use system language)"""
        # Native dialogs automatically use system language, this is only for Qt widgets
        pass
    
    def on_ui_language_changed(self, language_code):
        """Handle UI language change"""
        
        # Update all UI elements with new translations
        self.update_ui_texts()
        
        # Update language list without changing selection
        self.update_language_list_texts()
    
    def update_language_list_texts(self):
        """Update language list text without changing selection"""
        # Remember current selection
        current_data = self.language_combo.currentData()
        
        # Block signals to prevent triggering language change
        self.language_combo.blockSignals(True)
        
        try:
            # Update auto-detect option
            self.language_combo.setItemText(0, t("ui.options.auto_detect_language"))
            
            # Restore selection
            for i in range(self.language_combo.count()):
                if self.language_combo.itemData(i) == current_data:
                    self.language_combo.setCurrentIndex(i)
                    break
                    
        finally:
            # Restore signal connections
            self.language_combo.blockSignals(False)
    
    def update_ui_texts(self):
        """Update all UI text elements with current language"""
        # Window title - fixed English for global compatibility
        self.setWindowTitle("Markdown to Word")
        
        # Update main labels
        self.title_label.setText(t("app.name"))
        self.files_label.setText(t("ui.labels.files_to_convert"))
        self.settings_group.setTitle(t("ui.labels.conversion_settings"))
        self.template_label.setText(t("ui.labels.template"))
        self.language_label.setText(t("ui.labels.language"))
        self.file_handling_label.setText(t("ui.labels.file_handling"))
        
        # Update DropArea texts
        if hasattr(self.drop_area, 'update_texts'):
            self.drop_area.update_texts()
            
        # Update main UI elements
        self.convert_btn.setText(t("ui.buttons.start"))
        self.cancel_btn.setText(t("ui.buttons.cancel"))
        self.browse_template_btn.setText(t("ui.buttons.browse"))
        self.clear_list_btn.setText(t("ui.buttons.clear_list"))
        
        # Update radio buttons
        self.overwrite_radio.setText(t("ui.options.overwrite"))
        self.auto_rename_radio.setText(t("ui.options.auto_rename"))
        
        # Update checkboxes
        self.recursive_checkbox.setText(t("ui.labels.recursive_scan"))
        self.remove_emoji_checkbox.setText(t("ui.options.remove_emoji"))
        self.remove_emoji_checkbox.setToolTip(t("ui.tooltips.remove_emoji"))
        
        # Update file count
        count = len(self.markdown_files) if hasattr(self, 'markdown_files') else 0
        self.file_count_label.setText(t("ui.labels.file_stats", count=count))
        
        # Refresh template list to update "No templates" text
        self.refresh_template_list()
        
        # Update current status if pandoc not available
        if not pandoc.is_pandoc_available():
            self.status_label.setText(t("ui.status.pandoc_not_installed"))
        else:
            version = pandoc.get_pandoc_version()
            if version:
                self.status_label.setText(t("ui.status.pandoc_ready", version=version))
    
    def check_pandoc_availability(self):
        """Check Pandoc availability and version"""
        if not pandoc.is_pandoc_available():
            # 创建更明显的警告对话框
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle(t("dialogs.pandoc_not_installed.title"))
            msg_box.setText(t("dialogs.pandoc_not_installed.message"))
            msg_box.setDetailedText(pandoc.get_installation_help())
            
            # 使用自定义按钮并设置统一的最小宽度
            ok_button = msg_box.addButton(t("ui.buttons.ok"), QMessageBox.AcceptRole)
            msg_box.setDefaultButton(ok_button)
            
            # 设置按钮样式，确保一致的最小宽度
            msg_box.setStyleSheet("""
                QMessageBox QPushButton {
                    min-width: 80px;
                    min-height: 25px;
                    padding: 5px 15px;
                    font-weight: 500;
                }
            """)
            
            # 确保对话框在最前面
            msg_box.setWindowModality(Qt.ApplicationModal)
            msg_box.raise_()
            msg_box.activateWindow()
            msg_box.exec()
            
            self.convert_btn.setEnabled(False)
            self.status_label.setText(t("ui.status.pandoc_not_installed"))
        else:
            version = pandoc.get_pandoc_version()
            if version:
                self.status_label.setText(t("ui.status.pandoc_ready", version=version))
                
                # Check for version warnings
                warning = pandoc.get_version_warning()
                if warning:
                    QMessageBox.information(self, t("dialogs.pandoc_version_notice.title"), warning)
    
    def handle_dropped_files(self, file_paths: List[str]):
        """Handle dropped files"""
        self.scan_and_add_files(file_paths)
    
    def select_files(self):
        """Select files"""
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            t("file_operations.select_markdown_files"), 
            "", 
            t("file_operations.markdown_filter")
        )
        if files:
            self.scan_and_add_files(files)
    
    
    def select_directory(self):
        """Select directory"""
        directory = QFileDialog.getExistingDirectory(
            self, 
            t("file_operations.select_directory")
        )
        if directory:
            self.scan_and_add_files([directory])
    
    
    
    def scan_and_add_files(self, paths: List[str]):
        """Scan and add files"""
        recursive = self.recursive_checkbox.isChecked()
        
        try:
            found_files = quick_scan(paths, recursive)
            
            # Merge file lists and remove duplicates
            all_files = set(self.markdown_files + found_files)
            self.markdown_files = sorted(list(all_files))
            
            self.refresh_file_list()
            
        except Exception as e:
            QMessageBox.critical(self, t("dialogs.file_scan_failed.title"), 
                               t("dialogs.file_scan_failed.message", error=str(e)))
    
    def refresh_file_list(self):
        """Refresh file list with custom FileListItem widgets"""
        from ui.file_list_item import ConversionStatus
        
        # Store current file statuses to preserve them
        current_statuses = {}
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if isinstance(item, FileListItem):
                current_statuses[item.get_file_path()] = item.get_status()
        
        self.file_list.clear()
        
        for file_path in self.markdown_files:
            # Create FileListItem with status tracking
            item = FileListItem(file_path)
            widget = item.create_widget(self.file_list)
            
            # Restore previous status if it existed
            if file_path in current_statuses:
                item.set_status(current_statuses[file_path])
            
            # Connect delete signal
            widget.delete_requested.connect(self.remove_file)
            
            # Add to list and set widget
            self.file_list.addItem(item)
            self.file_list.setItemWidget(item, widget)
        
        # Update file statistics
        count = len(self.markdown_files)
        self.file_count_label.setText(t("ui.labels.file_stats", count=count))
        
        # Update convert button state
        self.convert_btn.setEnabled(count > 0 and pandoc.is_pandoc_available())
    
    def show_file_context_menu(self, position):
        """显示文件列表右键菜单"""
        item = self.file_list.itemAt(position)
        if item is None:
            return
        
        # 创建右键菜单
        menu = QMenu(self)
        
        # 添加删除动作
        delete_action = menu.addAction(t("context_menu.remove_from_list"))
        delete_action.triggered.connect(lambda: self.remove_selected_file(item))
        
        # 添加分隔线和其他操作
        menu.addSeparator()
        
        # 添加在文件夹中显示动作
        show_action = menu.addAction(t("context_menu.show_in_folder"))
        file_path = item.data(Qt.UserRole)
        show_action.triggered.connect(lambda: self.show_file_in_folder(file_path))
        
        # 显示菜单
        menu.exec(self.file_list.mapToGlobal(position))
    
    def remove_selected_file(self, item: QListWidgetItem):
        """从文件列表中移除选中的文件"""
        file_path = item.data(Qt.UserRole)
        if file_path and file_path in self.markdown_files:
            self.markdown_files.remove(file_path)
            self.refresh_file_list()
    
    def show_file_in_folder(self, file_path: str):
        """在文件夹中显示文件"""
        if file_path and Path(file_path).exists():
            import subprocess
            import platform
            
            system = platform.system()
            try:
                if system == "Darwin":  # macOS
                    subprocess.run(["open", "-R", file_path])
                elif system == "Windows":
                    subprocess.run(["explorer", "/select,", file_path])
                else:  # Linux
                    subprocess.run(["xdg-open", Path(file_path).parent])
            except Exception as e:
                QMessageBox.information(self, t("dialogs.open_folder_error.title"), 
                                       t("file_errors.open_folder_failed").format(error=str(e)))
        else:
            QMessageBox.warning(self, t("dialogs.file_not_exist.title"), t("file_errors.file_not_exist"))
    
    def remove_file(self, file_path: str):
        """从文件列表中移除指定文件（保留兼容性）"""
        try:
            if file_path in self.markdown_files:
                self.markdown_files.remove(file_path)
                self.refresh_file_list()
        except ValueError:
            pass
    
    def clear_file_list(self):
        """清除所有文件"""
        if self.markdown_files:
            # Create message box with custom button text
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setWindowTitle(t("dialogs.clear_list_confirm.title"))
            msg_box.setText(t("dialogs.clear_list_confirm.message"))
            
            # Add custom buttons with translated text
            yes_button = msg_box.addButton(t("ui.buttons.yes"), QMessageBox.YesRole)
            no_button = msg_box.addButton(t("ui.buttons.no"), QMessageBox.NoRole)
            msg_box.setDefaultButton(no_button)
            
            # Show dialog and check result
            msg_box.exec()
            if msg_box.clickedButton() == yes_button:
                self.markdown_files.clear()
                self.refresh_file_list()
    
    def get_files_needing_conversion(self) -> List[str]:
        """获取需要转换的文件列表（状态为PENDING或FAILED的文件）"""
        from ui.file_list_item import ConversionStatus
        
        files_needing_conversion = []
        
        # 遍历文件列表中的所有项
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if isinstance(item, FileListItem):
                status = item.get_status()
                file_path = item.get_file_path()
                if status in [ConversionStatus.PENDING, ConversionStatus.FAILED]:
                    files_needing_conversion.append(file_path)
        
        # 向后兼容：只有当列表中没有任何FileListItem时，才返回所有文件
        has_file_list_items = any(isinstance(self.file_list.item(i), FileListItem) 
                                 for i in range(self.file_list.count()))
        
        if not has_file_list_items and self.markdown_files:
            files_needing_conversion = self.markdown_files.copy()
        
        return files_needing_conversion
    
    def update_file_status(self, file_path: str, status: 'ConversionStatus'):
        """根据文件路径更新文件状态"""
        from ui.file_list_item import ConversionStatus
        
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if isinstance(item, FileListItem) and item.get_file_path() == file_path:
                item.set_status(status)
                break
    
    def set_files_converting(self, file_paths: List[str]):
        """将指定文件状态设置为转换中"""
        from ui.file_list_item import ConversionStatus
        
        for file_path in file_paths:
            self.update_file_status(file_path, ConversionStatus.CONVERTING)
    
    def mark_file_success(self, file_path: str):
        """标记文件转换成功"""
        from ui.file_list_item import ConversionStatus
        self.update_file_status(file_path, ConversionStatus.SUCCESS)
    
    def mark_file_failed(self, file_path: str):
        """标记文件转换失败"""
        from ui.file_list_item import ConversionStatus
        self.update_file_status(file_path, ConversionStatus.FAILED)
    
    def on_recursive_changed(self):
        """Recursive option changed"""
        config = get_config()
        config.set("ui.recursive_scan", self.recursive_checkbox.isChecked())
    
    def on_file_handling_changed(self):
        """File handling option changed"""
        config = get_config()
        overwrite = self.overwrite_radio.isChecked()
        config.set("output_settings.overwrite_files", overwrite)
    
    def on_emoji_removal_changed(self):
        """Emoji removal option changed"""
        config = get_config()
        remove_emoji = self.remove_emoji_checkbox.isChecked()
        config.set("output_settings.remove_emoji", remove_emoji)
    
    def on_template_changed(self):
        """Template selection changed"""
        current_data = self.template_combo.currentData()
        if current_data:
            template_manager = get_template_manager()
            template_manager.set_default_template(current_data)
    
    def browse_template(self):
        """Browse template file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            t("file_operations.select_template_file"), 
            "", 
            t("file_operations.word_documents_filter")
        )
        
        if file_path:
            # Add to template manager
            template_manager = get_template_manager()
            success, message = template_manager.add_user_template(
                Path(file_path), Path(file_path).stem
            )
            
            if success:
                self.refresh_template_list()
                # Select newly added template
                for i in range(self.template_combo.count()):
                    if self.template_combo.itemData(i) and Path(self.template_combo.itemData(i)).name == Path(file_path).name:
                        self.template_combo.setCurrentIndex(i)
                        break
                QMessageBox.information(self, t("dialogs.add_template_success.title"), message)
            else:
                QMessageBox.warning(self, t("dialogs.add_template_failed.title"), message)
    
    def start_conversion(self):
        """Start conversion"""
        if not self.markdown_files:
            QMessageBox.warning(self, t("dialogs.select_files_first.title"), 
                              t("dialogs.select_files_first.message"))
            return
        
        if not pandoc.is_pandoc_available():
            QMessageBox.warning(self, t("dialogs.install_pandoc_first.title"), 
                              t("dialogs.install_pandoc_first.message"))
            return
        
        # Get files that need conversion (only pending and failed files)
        files_to_convert = self.get_files_needing_conversion()
        
        if not files_to_convert:
            QMessageBox.information(self, t("dialogs.no_files_to_convert.title"),
                                  t("dialogs.no_files_to_convert.message"))
            return
        
        # Save settings
        self.save_current_settings()
        
        # Get template path
        template_path = self.template_combo.currentData()
        
        # Validate files and template
        conversion_manager = get_conversion_manager()
        valid, message = conversion_manager.validate_files_and_template(
            files_to_convert, template_path
        )
        
        if not valid:
            QMessageBox.warning(self, t("dialogs.validation_failed.title"), message)
            return
        
        # Set files to converting status before starting
        self.set_files_converting(files_to_convert)
        
        # Start conversion
        success = conversion_manager.start_conversion(
            files_to_convert,
            template_path,
            ConversionQuality.STANDARD
        )
        
        if not success:
            QMessageBox.warning(self, t("dialogs.conversion_failed.title"), 
                              t("dialogs.conversion_failed.message"))
    
    def cancel_conversion(self):
        """Cancel conversion"""
        conversion_manager = get_conversion_manager()
        conversion_manager.stop_conversion()
    
    def save_current_settings(self):
        """Save current settings"""
        config = get_config()
        # Save output settings
        config.set("output_settings.overwrite_files", self.overwrite_radio.isChecked())
        config.set("output_settings.remove_emoji", self.remove_emoji_checkbox.isChecked())
        
        # Default to timestamp naming since the option is hidden from UI
        # Keep the button logic for future customization features
        naming_strategy = "timestamp" if self.timestamp_radio.isChecked() else "increment"
        config.set("output_settings.naming_strategy", naming_strategy)
    
    def on_conversion_started(self):
        """Conversion started"""
        self.convert_btn.setVisible(False)
        self.cancel_btn.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(t("ui.status.starting_conversion"))
    
    def on_conversion_finished(self, summary):
        """Conversion finished"""
        self.convert_btn.setVisible(True)
        self.cancel_btn.setVisible(False)
        self.progress_bar.setVisible(False)
        
        # Show results
        total = summary["total_files"]
        successful = summary["successful"]
        failed = summary["failed"]
        
        if failed == 0:
            self.status_label.setText(t("ui.status.conversion_completed", successful=successful))
            QMessageBox.information(self, t("dialogs.conversion_complete.title"), 
                                  t("dialogs.conversion_complete.message", successful=successful, total=total))
        else:
            self.status_label.setText(t("ui.status.conversion_completed_with_failures", successful=successful, failed=failed))
            
            # Show detailed results
            details = t("dialogs.conversion_results.summary", successful=successful, failed=failed) + "\n\n"
            if summary["failed_files"]:
                details += t("dialogs.conversion_results.failed_files_header") + "\n"
                for failed_file in summary["failed_files"][:5]:  # Show only first 5
                    details += f"• {Path(failed_file['file']).name}: {failed_file['error']}\n"
                if len(summary["failed_files"]) > 5:
                    remaining = len(summary['failed_files']) - 5
                    details += t("dialogs.conversion_results.more_files", count=remaining) + "\n"
            
            QMessageBox.warning(self, t("dialogs.conversion_complete_with_failures.title"), details)
    
    def on_conversion_error(self, error_message):
        """Conversion error"""
        self.convert_btn.setVisible(True)
        self.cancel_btn.setVisible(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText(t("ui.status.conversion_failed", error=error_message))
        
        QMessageBox.critical(self, t("dialogs.conversion_error.title"), error_message)
    
    def on_progress_updated(self, progress, message, stats):
        """Progress updated"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)
    
    def on_task_started(self, task_id: str, filename: str):
        """Task started - update file status"""
        # File is already set to CONVERTING status by set_files_converting
        pass
    
    def on_task_completed(self, task_id: str, success: bool, message: str):
        """Task completed - update file status"""
        # We need to find the file path associated with this task
        # Since we don't have direct access to task info here, we'll use a workaround
        # by checking the conversion manager's progress tracker
        conversion_manager = get_conversion_manager()
        progress_tracker = conversion_manager.get_progress_tracker()
        task = progress_tracker.get_task(task_id)
        
        if task and task.input_file:
            if success:
                self.mark_file_success(task.input_file)
            else:
                self.mark_file_failed(task.input_file)
    
    def on_batch_started(self, total_tasks: int):
        """Batch started"""
        pass
    
    def on_batch_completed(self, stats):
        """Batch completed"""
        pass
    
    def on_time_estimated(self, time_str: str):
        """Time estimate updated"""
        pass
    
    
    def closeEvent(self, event):
        """Close event"""
        # If conversion is running, ask if user wants to cancel
        conversion_manager = get_conversion_manager()
        if conversion_manager.is_converting:
            # Create message box with custom button text
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setWindowTitle(t("dialogs.confirm_close.title"))
            msg_box.setText(t("dialogs.confirm_close.message"))
            
            # Add custom buttons with translated text
            yes_button = msg_box.addButton(t("ui.buttons.yes"), QMessageBox.YesRole)
            no_button = msg_box.addButton(t("ui.buttons.no"), QMessageBox.NoRole)
            msg_box.setDefaultButton(no_button)
            
            # Show dialog and check result
            msg_box.exec()
            if msg_box.clickedButton() == yes_button:
                conversion_manager.stop_conversion()
                self._cleanup_on_exit()
                event.accept()
            else:
                event.ignore()
        else:
            self._cleanup_on_exit()
            event.accept()
    
    def _cleanup_on_exit(self):
        """Cleanup resources on application exit"""
        # Save current settings
        self.save_current_settings()
        
        # Cleanup temporary emoji-processed files
        emoji_processor.cleanup_all_temp_files()
        
        # Cleanup any orphaned temp files from previous runs
        cleanup_orphaned_temp_files()