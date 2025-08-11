# -*- coding: utf-8 -*-
import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, Optional
from .platform_paths import get_app_dirs

class ConfigManager:
    """Configuration manager for saving and loading user preferences"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            # Use platform-appropriate config directory
            app_dirs = get_app_dirs()
            self.config_dir = app_dirs['config']
        else:
            self.config_dir = Path(config_dir)
        
        self.config_file = self.config_dir / "settings.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Default configuration
        self.default_config = {
            "templates": {
                "default_template": "default.docx",
                "user_templates": []
            },
            "output_settings": {
                "overwrite_files": False,
                "naming_strategy": "timestamp",  # "timestamp" or "increment"
                "preview_outputs": True,
                "remove_emoji": True  # Remove emoji characters before conversion
            },
            "ui": {
                "recursive_scan": True,
                "window_geometry": None,
                "window_state": None,
                "language": "auto"  # "auto" for system detection, or specific language code
            },
            "recent": {
                "directories": [],
                "templates": []
            }
        }
        
        self._config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load config file, create default if not exists"""
        if not self.config_file.exists():
            # Create default config file
            config = self.default_config.copy()
            self._config = config
            self.save_config()
            return config
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    raise json.JSONDecodeError("Empty file", "", 0)
                config = json.loads(content)
            
            # Deserialize config (convert base64 strings back to QByteArray where needed)
            config = self._deserialize_value(config)
            
            # Merge default config (ensure new config items are included)
            return self._merge_config(self.default_config, config)
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"Failed to load config file: {e}")
            
            # Try to load from backup
            backup_file = self.config_file.with_suffix('.json.backup')
            if backup_file.exists():
                try:
                    print(f"Attempting to restore from backup: {backup_file}")
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    # Deserialize backup config
                    config = self._deserialize_value(config)
                    
                    # Restore from backup
                    self._config = self._merge_config(self.default_config, config)
                    self.save_config()
                    return self._config
                    
                except (json.JSONDecodeError, IOError) as backup_error:
                    print(f"Backup file also corrupted: {backup_error}")
            
            # Fall back to default and recreate config file
            print("Using default config and recreating config file")
            config = self.default_config.copy()
            self._config = config
            self.save_config()
            return config
    
    def _merge_config(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge config, ensure new default config items are included"""
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _serialize_value(self, obj):
        """Convert Qt objects to JSON-serializable values"""
        from PySide6.QtCore import QByteArray
        
        if isinstance(obj, QByteArray):
            # Convert QByteArray to base64 string
            return obj.toBase64().data().decode('ascii')
        elif isinstance(obj, dict):
            return {k: self._serialize_value(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_value(item) for item in obj]
        else:
            return obj
    
    def _deserialize_value(self, obj, key_path=""):
        """Convert base64 strings back to QByteArray for specific keys"""
        from PySide6.QtCore import QByteArray
        
        if isinstance(obj, dict):
            return {k: self._deserialize_value(v, f"{key_path}.{k}" if key_path else k) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deserialize_value(item, key_path) for item in obj]
        elif isinstance(obj, str) and key_path.endswith(('geometry', 'state')):
            # Convert base64 string back to QByteArray for geometry/state keys
            try:
                return QByteArray.fromBase64(obj.encode('ascii'))
            except:
                return None
        else:
            return obj

    def save_config(self):
        """Save config to file with backup and integrity check"""
        try:
            # Create backup if original exists
            backup_file = self.config_file.with_suffix('.json.backup')
            if self.config_file.exists():
                shutil.copy2(self.config_file, backup_file)
            
            # Write to temporary file first
            temp_file = self.config_file.with_suffix('.json.tmp')
            
            # Serialize config to make it JSON-compatible
            serializable_config = self._serialize_value(self._config)
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_config, f, indent=2, ensure_ascii=False)
            
            # Verify the written file is valid JSON
            with open(temp_file, 'r', encoding='utf-8') as f:
                json.load(f)  # This will raise an exception if JSON is invalid
            
            # If verification passes, replace the original file
            if temp_file.exists():
                temp_file.replace(self.config_file)
                
        except (IOError, json.JSONDecodeError, TypeError) as e:
            print(f"Failed to save config file: {e}")
            # If temp file exists, remove it
            temp_file = self.config_file.with_suffix('.json.tmp')
            if temp_file.exists():
                temp_file.unlink()
    
    def get(self, key_path: str, default=None) -> Any:
        """Get config value using dot-separated path, e.g. 'ui.recursive_scan'"""
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """Set config value using dot-separated path"""
        keys = key_path.split('.')
        config = self._config
        
        # Navigate to parent level
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set value
        config[keys[-1]] = value
        self.save_config()
    
    
    def get_output_settings(self) -> Dict[str, Any]:
        """Get output settings"""
        return self._config.get("output_settings", self.default_config["output_settings"])
    
    
    def add_user_template(self, name: str, path: str):
        """Add user template"""
        templates = self._config["templates"]["user_templates"]
        
        # Avoid duplicates
        for template in templates:
            if template["path"] == path:
                template["name"] = name  # Update name
                self.save_config()
                return
        
        templates.append({"name": name, "path": path})
        self.save_config()
    
    def remove_user_template(self, path: str):
        """Remove user template"""
        templates = self._config["templates"]["user_templates"]
        templates[:] = [t for t in templates if t["path"] != path]
        self.save_config()
    
    def set_default_template(self, template_path: str):
        """Set default template"""
        self._config["templates"]["default_template"] = template_path
        self.save_config()
    
    
    def get_language_setting(self) -> str:
        """Get language setting"""
        return self.get("ui.language", "auto")
    
    def set_language_setting(self, language: str):
        """Set language setting"""
        self.set("ui.language", language)

# Global config manager instance  
# 延迟初始化，避免在模块导入时就创建目录
_config_instance = None

def get_config() -> ConfigManager:
    """获取配置管理器单例"""
    global _config_instance
    if _config_instance is None:
        try:
            _config_instance = ConfigManager()
        except Exception as e:
            print(f"Failed to initialize config manager: {e}")
            # Return a temporary config manager with default settings
            import tempfile
            temp_dir = Path(tempfile.gettempdir()) / "md2docx_temp"
            _config_instance = ConfigManager(temp_dir)
    return _config_instance

# 向后兼容的全局实例
config = None  # 将在首次调用 get_config() 时初始化