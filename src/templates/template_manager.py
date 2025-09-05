# -*- coding: utf-8 -*-
import os
import shutil
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config_manager import get_config
from utils.i18n_manager import t
from utils.platform_paths import get_app_dirs

class TemplateManager:
    """Template manager, manages DOCX template files"""
    
    def __init__(self):
        # Get platform-appropriate directories
        app_dirs = get_app_dirs()
        
        # Built-in templates from app bundle/resources
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller打包后的环境
            self.builtin_template_dir = Path(sys._MEIPASS) / "templates"
        else:
            # 开发环境
            self.builtin_template_dir = Path(__file__).parent.parent.parent / "templates"
        
        # User templates in platform-specific directory
        self.user_template_dir = app_dirs['templates']
        
        # Ensure user template directory exists
        self.user_template_dir.mkdir(parents=True, exist_ok=True)
        
        # Built-in default template path
        self.default_template_path = self.builtin_template_dir / "default.docx"
        
        # Initialize config manager
        self.config = get_config()
    
    def is_valid_docx(self, file_path: Path) -> bool:
        """Validate if file is valid DOCX"""
        if not file_path.exists() or file_path.suffix.lower() != '.docx':
            return False
        
        try:
            # Try to open DOCX file (actually a ZIP file)
            with ZipFile(file_path, 'r') as docx:
                # Check required DOCX file structure
                required_files = [
                    'word/document.xml',
                    '[Content_Types].xml'
                ]
                
                file_list = docx.namelist()
                for required_file in required_files:
                    if required_file not in file_list:
                        return False
                
                return True
        except Exception:
            return False
    
    def get_all_templates(self) -> List[Dict[str, str]]:
        """Get all available template list - directly from file system"""
        templates = []
        
        # Built-in default template (always show, even if not found)
        template_exists = self.default_template_path.exists() and self.is_valid_docx(self.default_template_path)
        template_name = "Default Template"
        if not template_exists:
            template_name += t("templates_extended.not_found_suffix")
        
        templates.append({
            "name": template_name,
            "path": str(self.default_template_path) if template_exists else None,
            "type": "builtin",
            "available": template_exists
        })
        
        # User custom templates - scan directly from file system
        if self.user_template_dir.exists():
            try:
                for template_file in self.user_template_dir.glob("*.docx"):
                    if self.is_valid_docx(template_file):
                        # Use filename without extension as display name
                        display_name = template_file.stem
                        
                        # Check if it's a duplicated file with number suffix
                        if display_name.endswith(')') and '(' in display_name:
                            # Extract original name from "name(1)" format
                            base_name = display_name.split('(')[0]
                            if base_name:
                                display_name = base_name
                        
                        templates.append({
                            "name": display_name,
                            "path": str(template_file),
                            "type": "user",
                            "available": True
                        })
            except Exception as e:
                print(f"Error scanning user templates: {e}")
        
        return templates
    
    def get_default_template_path(self) -> Optional[str]:
        """Get current default template path"""
        default_template = self.config.get("templates.default_template", "default.docx")
        
        # If built-in template
        if default_template == "default.docx":
            if self.default_template_path.exists():
                return str(self.default_template_path)
            else:
                return None
        
        # User template
        template_path = Path(default_template)
        if not template_path.is_absolute():
            template_path = self.user_template_dir / template_path
        
        if template_path.exists() and self.is_valid_docx(template_path):
            return str(template_path)
        
        # If default template doesn't exist, fallback to built-in template
        if self.default_template_path.exists():
            return str(self.default_template_path)
        
        return None
    
    def add_user_template(self, source_path: Path, display_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Add user template
        Returns: (success_flag, message/error_info)
        """
        if not source_path.exists():
            return False, t("templates_extended.file_not_exist")
        
        if not self.is_valid_docx(source_path):
            return False, t("templates_extended.invalid_docx")
        
        # Generate display name
        if display_name is None:
            display_name = source_path.stem
        
        # Generate target filename (avoid conflicts)
        target_filename = source_path.name
        target_path = self.user_template_dir / target_filename
        
        counter = 1
        while target_path.exists():
            name_part = source_path.stem
            target_filename = f"{name_part}({counter}).docx"
            target_path = self.user_template_dir / target_filename
            counter += 1
        
        try:
            # Copy file to user template directory
            shutil.copy2(source_path, target_path)
            
            # No longer need to update config since we read directly from file system
            return True, t("templates_extended.added_successfully", name=display_name)
            
        except Exception as e:
            return False, t("templates_extended.copy_failed", error=str(e))
    
    
    def set_default_template(self, template_path: str):
        """Set default template"""
        path = Path(template_path)
        
        if path == self.default_template_path:
            self.config.set_default_template("default.docx")
        else:
            # Path relative to user directory
            if path.is_absolute() and path.is_relative_to(self.user_template_dir):
                relative_path = path.relative_to(self.user_template_dir)
                self.config.set_default_template(str(relative_path))
            else:
                self.config.set_default_template(template_path)
    
    def create_default_template(self):
        """Create a basic default template file"""
        if self.default_template_path.exists():
            return
        
        # Create internationalized README file with template usage instructions
        readme_content = t("templates_extended.readme_content")
        
        # Create instruction file in user template directory
        readme_path = self.user_template_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
    

# Global template manager instance - lazy initialization
_template_manager_instance = None

def get_template_manager() -> TemplateManager:
    """获取模板管理器单例"""
    global _template_manager_instance
    if _template_manager_instance is None:
        _template_manager_instance = TemplateManager()
    return _template_manager_instance

# 向后兼容的全局实例
template_manager = None  # 将在首次调用 get_template_manager() 时初始化