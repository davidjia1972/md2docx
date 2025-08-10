#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import logging
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import PySide6
try:
    from PySide6.QtWidgets import QApplication, QMessageBox
    from PySide6.QtCore import Qt, QLocale, QTranslator
    from PySide6.QtGui import QIcon, QFont
except ImportError:
    # Use basic English message since i18n system isn't loaded yet
    print("Error: PySide6 not found. Please install: pip install PySide6")
    sys.exit(1)

# Import main window
try:
    from ui.main_window import MainWindow
    from templates.template_manager import template_manager
    from converter.pandoc_wrapper import pandoc
    from utils.config_manager import config
except ImportError as e:
    # Use basic English message since i18n system isn't loaded yet  
    print(f"Error: Failed to import modules - {e}")
    sys.exit(1)

class Application:
    """Application class"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        self.qt_translators = []
        
    def setup_logging(self):
        """Setup logging"""
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / "converter.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Set Qt log level
        os.environ['QT_LOGGING_RULES'] = '*=false'
    
    def create_app(self):
        """Create QApplication"""
        # IMPORTANT: Set system locale BEFORE creating QApplication
        # This ensures native dialogs use the correct language from the start
        self._ensure_system_locale()
        
        # Set high DPI support (for Qt 6, these are enabled by default)
        try:
            from PySide6 import __version__ as pyside_version
            # In Qt 6, high DPI is enabled by default, these attributes are deprecated
            pass
        except:
            # Fallback for older versions if needed
            pass
        
        self.app = QApplication(sys.argv)
        
        # Force Qt to use Chinese locale for native dialogs on macOS
        if sys.platform == "darwin":
            from PySide6.QtCore import QLocale
            chinese_locale = QLocale(QLocale.Chinese, QLocale.China)
            QLocale.setDefault(chinese_locale)
            
            # Try to force NSApplication locale using objc
            try:
                import objc
                from Foundation import NSLocale
                # Set NSApp current locale to Chinese
                chinese_nslocale = NSLocale.localeWithLocaleIdentifier_("zh_CN")
                NSLocale.setCurrentLocale_(chinese_nslocale)
                logging.info("Set NSApplication locale to Chinese")
            except Exception as e:
                logging.debug(f"Could not set NSApplication locale: {e}")
            
            self.app.installTranslator(QTranslator())  # Install empty translator to trigger locale system
        
        # Set application info
        self.app.setApplicationName("Markdown to DOCX Converter")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("Converter Tools")
        
        # Set application icon (if exists)
        from utils.icon_manager import icon_manager
        app_icon = icon_manager.get_multi_size_icon()
        if app_icon:
            # Set both application and window icon for better macOS dock support
            self.app.setWindowIcon(app_icon)
            # Also set application icon explicitly
            from PySide6.QtGui import QGuiApplication
            QGuiApplication.setWindowIcon(app_icon)
        
        # Set font
        if sys.platform == "darwin":  # macOS
            font = QFont("PingFang SC", 11)
        elif sys.platform.startswith("win"):  # Windows
            font = QFont("Microsoft YaHei", 9)
        else:  # Linux
            font = QFont("Noto Sans CJK SC", 10)
        
        self.app.setFont(font)
        
        # Set style
        self.setup_style()
        
        return self.app
    
    def setup_style(self):
        """Setup application style"""
        style = """
        QMainWindow {
            background-color: #f8f9fa;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            margin: 5px 0;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            background-color: #f8f9fa;
            color: #495057;
        }
        
        QComboBox {
            border: 1px solid #ced4da;
            border-radius: 3px;
            padding: 5px;
            background-color: white;
            min-height: 20px;
        }
        
        QComboBox:hover {
            border-color: #80bdff;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 1px;
            border-left-color: #ced4da;
            border-left-style: solid;
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
        }
        
        QPushButton {
            background-color: #6c757d;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: 500;
        }
        
        QPushButton:hover {
            background-color: #5a6268;
        }
        
        QPushButton:pressed {
            background-color: #545b62;
        }
        
        QListWidget {
            border: 1px solid #dee2e6;
            border-radius: 4px;
            background-color: white;
            alternate-background-color: #f8f9fa;
            padding: 5px;
        }
        
        QListWidget::item {
            padding: 8px;
            border-bottom: 1px solid #e9ecef;
        }
        
        QListWidget::item:selected {
            background-color: #007bff;
            color: white;
        }
        
        QListWidget::item:hover {
            background-color: #e9ecef;
        }
        
        QProgressBar {
            border: 1px solid #dee2e6;
            border-radius: 4px;
            text-align: center;
            background-color: #e9ecef;
        }
        
        QProgressBar::chunk {
            background-color: #28a745;
            border-radius: 3px;
        }
        
        QCheckBox, QRadioButton {
            spacing: 8px;
            color: #495057;
        }
        
        QCheckBox::indicator, QRadioButton::indicator {
            width: 16px;
            height: 16px;
        }
        
        QCheckBox::indicator:unchecked {
            border: 1px solid #ced4da;
            background-color: white;
            border-radius: 2px;
        }
        
        QCheckBox::indicator:checked {
            border: 1px solid #007bff;
            background-color: #007bff;
            border-radius: 2px;
        }
        
        QRadioButton::indicator:unchecked {
            border: 1px solid #ced4da;
            background-color: white;
            border-radius: 8px;
        }
        
        QRadioButton::indicator:checked {
            border: 1px solid #007bff;
            background-color: #007bff;
            border-radius: 8px;
        }
        """
        
        self.app.setStyleSheet(style)
    
    def check_prerequisites(self):
        """Check prerequisites"""
        issues = []
        
        # Check Python version
        if sys.version_info < (3, 8):
            issues.append("Python 3.8 or higher")
        
        # Don't check Pandoc here - let MainWindow handle it
        # This allows the app to start and show a better warning dialog
        
        # Check template directory
        template_dir = Path(__file__).parent.parent / "templates"
        if not template_dir.exists():
            try:
                template_dir.mkdir(exist_ok=True)
            except Exception:
                issues.append("Cannot create template directory")
        
        return issues
    
    def show_prerequisites_dialog(self, issues):
        """Show prerequisites dialog"""
        from utils.i18n_manager import t
        
        message = t("dialogs.missing_components.message_prefix") + "\n\n"
        for issue in issues:
            message += f"• {issue}\n"
        
        message += "\n" + t("dialogs.missing_components.message_suffix")
        
        QMessageBox.critical(None, t("dialogs.missing_components.title"), message)
    
    def create_main_window(self):
        """Create main window"""
        self.main_window = MainWindow()
        
        # Restore window geometry from config
        geometry = config.get("ui.window_geometry")
        if geometry:
            self.main_window.restoreGeometry(geometry)
        
        return self.main_window
    
    def setup_shutdown_handling(self):
        """Setup shutdown handling"""
        def save_settings():
            """Save settings"""
            if self.main_window:
                # Save window geometry
                config.set("ui.window_geometry", self.main_window.saveGeometry())
        
        self.app.aboutToQuit.connect(save_settings)
    
    def _ensure_system_locale(self):
        """Ensure system locale is properly set for native dialogs"""
        import locale
        import os
        
        try:
            # Special handling for macOS - Force Chinese environment
            if sys.platform == "darwin":
                try:
                    import subprocess
                    # Check macOS system locale
                    result = subprocess.run(['defaults', 'read', '-g', 'AppleLocale'], 
                                          capture_output=True, text=True, timeout=3)
                    if result.returncode == 0:
                        macos_locale = result.stdout.strip()
                        logging.info(f"macOS system locale detected: {macos_locale}")
                        
                        # Force Chinese environment for Qt native dialogs
                        if macos_locale.startswith(('zh', 'zh_CN', 'zh-Hans')):
                            # Set comprehensive Chinese locale environment
                            os.environ['LANG'] = 'zh_CN.UTF-8'
                            os.environ['LC_ALL'] = 'zh_CN.UTF-8'
                            os.environ['LC_MESSAGES'] = 'zh_CN.UTF-8'
                            os.environ['LC_CTYPE'] = 'zh_CN.UTF-8'
                            # Also try macOS specific environment variables
                            os.environ['LANGUAGE'] = 'zh_CN:zh'
                            os.environ['NSLocale'] = 'zh_CN'
                            logging.info("Enforced comprehensive Chinese locale for macOS native dialogs")
                            return
                except Exception as e:
                    logging.debug(f"Could not read macOS locale: {e}")
            
            # Fallback for other systems or if macOS detection fails
            system_lang = os.environ.get('LANG')
            if not system_lang:
                try:
                    default_locale = locale.getdefaultlocale()
                    if default_locale[0]:
                        system_lang = f"{default_locale[0]}.UTF-8"
                except:
                    system_lang = "zh_CN.UTF-8"  # Fallback for Chinese system
            
            # Set environment variables that Qt native dialogs respect
            os.environ['LANG'] = system_lang
            os.environ['LC_ALL'] = system_lang
            os.environ['LC_MESSAGES'] = system_lang
            
            logging.info(f"System locale configured for native dialogs: {system_lang}")
            
        except Exception as e:
            logging.warning(f"Could not configure system locale: {e}")
    
    def _initialize_i18n(self):
        """Initialize internationalization system"""
        try:
            from utils.config_manager import config
            from utils.i18n_manager import i18n
            
            # Load saved language setting
            saved_language = config.get_language_setting()
            
            if saved_language and saved_language != "auto":
                # Set specific language
                i18n.set_language(saved_language)
                logging.info(f"Language set to: {saved_language}")
                # Set Qt translator for system dialogs
                self._set_qt_translator(saved_language)
            else:
                # Use auto-detected language (already done in i18n manager constructor)
                current_lang = i18n.get_current_language()
                logging.info(f"Auto-detected language: {current_lang}")
                # Set Qt translator for system dialogs
                self._set_qt_translator(current_lang)
                
        except Exception as e:
            logging.warning(f"Failed to initialize i18n system: {e}")
    
    def _set_qt_translator(self, language_code):
        """Set Qt translator for application UI (not native dialogs)"""
        # Note: Native dialogs will use system language automatically
        # This translator only affects Qt-rendered UI elements
        try:
            from PySide6.QtCore import QTranslator, QLibraryInfo
            from pathlib import Path
            
            # Remove existing translators if they exist
            if hasattr(self, 'qt_translators') and self.qt_translators:
                for translator in self.qt_translators:
                    self.app.removeTranslator(translator)
            
            # Initialize translator list
            self.qt_translators = []
            
            # Only load Qt translators for internal Qt widgets, not for native dialogs
            # Native dialogs should follow system language automatically
            qt_locale = "zh_CN" if language_code.startswith("zh") else "en"
            
            # Get Qt translation path
            qt_translation_path = QLibraryInfo.path(QLibraryInfo.TranslationsPath)
            translation_path = Path(qt_translation_path)
            
            # Load basic Qt translation for any Qt-rendered widgets
            translator = QTranslator()
            if translator.load(f"qtbase_{qt_locale}", str(translation_path)):
                self.app.installTranslator(translator)
                self.qt_translators.append(translator)
                logging.info(f"Qt base translator loaded for: {qt_locale}")
            
            logging.info(f"Qt translator configured. Native dialogs will use system language.")
                    
        except Exception as e:
            logging.warning(f"Failed to set Qt translator: {e}")
    
    def run(self):
        """Run application"""
        try:
            # Setup logging
            self.setup_logging()
            logging.info("Starting application...")
            
            # Create app
            app = self.create_app()
            
            # Initialize i18n system
            self._initialize_i18n()
            
            # Check prerequisites
            issues = self.check_prerequisites()
            if issues:
                self.show_prerequisites_dialog(issues)
                return 1
            
            # Initialize template manager
            template_manager.create_default_template()
            
            # Create main window
            main_window = self.create_main_window()
            
            # Setup shutdown handling
            self.setup_shutdown_handling()
            
            # Show main window
            main_window.show()
            
            logging.info("Application started successfully")
            
            # Enter event loop
            return app.exec()
            
        except Exception as e:
            logging.error(f"Application startup failed: {e}")
            
            # Show error message
            try:
                from utils.i18n_manager import t
                QMessageBox.critical(None, t("dialogs.startup_error.title"), 
                                   t("dialogs.startup_error.message", error=str(e)))
            except:
                print(f"Startup error: {e}")
            
            return 1

def main():
    """Main function"""
    # Set environment variables
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    
    app = Application()
    return app.run()

if __name__ == "__main__":
    sys.exit(main())