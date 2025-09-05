# -*- coding: utf-8 -*-
"""
国际化管理器 - 多语言支持核心组件
"""

import json
import locale
import logging
import sys
from pathlib import Path
from typing import Dict, Optional, Any
from PySide6.QtCore import QObject, Signal

class I18nManager(QObject):
    """国际化管理器"""
    
    # 语言变更信号
    language_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.current_language = "zh_CN"  # 默认语言
        self.fallback_language = "en_US"  # 备用语言
        self.translations = {}  # 翻译缓存
        self.available_languages = {}  # 可用语言列表
        self.translation_stats = {  # 翻译统计
            "missing_keys": set(),
            "fallback_used": set(),
            "critical_missing": set()
        }
        
        # 获取项目根目录和资源目录
        self.root_dir = Path(__file__).parent.parent.parent
        
        # 检查是否在PyInstaller打包环境中
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller打包后的环境
            bundle_dir = Path(sys._MEIPASS)
            self.locales_dir = bundle_dir / "locales"
            self.config_dir = bundle_dir / "config" if (bundle_dir / "config").exists() else self.root_dir / "config"
        else:
            # 开发环境
            self.locales_dir = self.root_dir / "locales"
            self.config_dir = self.root_dir / "config"
        
        # 初始化
        self._load_language_config()
        self._detect_available_languages()
        self._auto_detect_system_language()
        
        # 加载当前语言包
        self.load_language(self.current_language)
    
    def _load_language_config(self):
        """加载语言配置文件"""
        config_file = self.config_dir / "languages.json"
        
        # 默认语言映射配置
        default_config = {
            "languages": {
                "zh_CN": {
                    "name": "简体中文",
                    "native_name": "简体中文",
                    "enabled": True
                },
                "en_US": {
                    "name": "English",
                    "native_name": "English", 
                    "enabled": True
                },
                "zh_TW": {
                    "name": "繁体中文",
                    "native_name": "繁體中文",
                    "enabled": False
                }
            },
            "system_language_mapping": {
                "zh_CN": "zh_CN",
                "zh_TW": "zh_TW", 
                "zh_HK": "zh_TW",
                "zh_SG": "zh_CN",
                "en_US": "en_US",
                "en_GB": "en_US",
                "en": "en_US",
                "zh": "zh_CN"
            }
        }
        
        try:
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.language_config = json.load(f)
            else:
                self.language_config = default_config
                # 创建默认配置文件
                config_file.parent.mkdir(exist_ok=True)
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                    
        except Exception as e:
            logging.warning(f"加载语言配置失败: {e}")
            self.language_config = default_config
    
    def _detect_available_languages(self):
        """检测可用的语言包"""
        self.available_languages = {}
        
        if not self.locales_dir.exists():
            logging.warning("语言包目录不存在")
            return
        
        # 按照 languages.json 中的顺序来构建可用语言列表
        languages_config = self.language_config.get("languages", {})
        
        for lang_code, lang_info in languages_config.items():
            # 检查该语言是否启用
            if not lang_info.get("enabled", True):
                continue
                
            # 检查对应的语言包文件是否存在
            lang_dir = self.locales_dir / lang_code
            messages_file = lang_dir / "messages.json"
            
            if lang_dir.exists() and lang_dir.is_dir() and messages_file.exists():
                self.available_languages[lang_code] = {
                    "native_name": lang_info.get("native_name", lang_code),
                    "path": messages_file
                }
        
        logging.info(f"检测到可用语言: {list(self.available_languages.keys())}")
    
    def _auto_detect_system_language(self):
        """自动检测系统语言"""
        try:
            # 获取系统语言
            system_lang = locale.getdefaultlocale()[0]
            if not system_lang:
                system_lang = "zh_CN"
            
            logging.info(f"系统语言: {system_lang}")
            
            # 查找映射
            mapping = self.language_config.get("system_language_mapping", {})
            mapped_lang = mapping.get(system_lang)
            
            # 如果没有精确匹配，尝试语言代码部分匹配
            if not mapped_lang and "_" in system_lang:
                lang_part = system_lang.split("_")[0]
                mapped_lang = mapping.get(lang_part)
            
            # 检查映射的语言是否可用
            if mapped_lang and mapped_lang in self.available_languages:
                self.current_language = mapped_lang
                logging.info(f"自动选择语言: {mapped_lang}")
            else:
                # 使用默认语言
                if "zh_CN" in self.available_languages:
                    self.current_language = "zh_CN"
                elif "en_US" in self.available_languages:
                    self.current_language = "en_US"
                else:
                    # 使用第一个可用语言
                    if self.available_languages:
                        self.current_language = list(self.available_languages.keys())[0]
                
                logging.info(f"使用默认语言: {self.current_language}")
                
        except Exception as e:
            logging.warning(f"自动检测系统语言失败: {e}")
            self.current_language = "zh_CN"
    
    def load_language(self, lang_code: str) -> bool:
        """加载指定语言包"""
        if lang_code not in self.available_languages:
            logging.warning(f"语言包不可用: {lang_code}")
            return False
        
        try:
            messages_file = self.available_languages[lang_code]["path"]
            with open(messages_file, 'r', encoding='utf-8') as f:
                self.translations[lang_code] = json.load(f)
            
            logging.info(f"语言包加载成功: {lang_code}")
            return True
            
        except Exception as e:
            logging.error(f"加载语言包失败 {lang_code}: {e}")
            return False
    
    def set_language(self, lang_code: str) -> bool:
        """设置当前语言"""
        if lang_code not in self.available_languages:
            logging.warning(f"语言不可用: {lang_code}")
            return False
        
        # 加载语言包（如果还没加载）
        if lang_code not in self.translations:
            if not self.load_language(lang_code):
                return False
        
        old_language = self.current_language
        self.current_language = lang_code
        
        # 发出语言变更信号
        if old_language != lang_code:
            self.language_changed.emit(lang_code)
            logging.info(f"语言已切换: {old_language} -> {lang_code}")
        
        return True
    
    def get_current_language(self) -> str:
        """获取当前语言代码"""
        return self.current_language
    
    def get_available_languages(self) -> Dict[str, Dict[str, str]]:
        """获取可用语言列表"""
        return self.available_languages.copy()
    
    def _get_nested_value(self, data: Dict, key: str) -> Optional[str]:
        """获取嵌套字典中的值，支持点分隔的键"""
        keys = key.split('.')
        current = data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        
        return current if isinstance(current, str) else None
    
    def _generate_friendly_fallback(self, key: str) -> str:
        """为缺失的翻译键生成用户友好的显示文本"""
        # 分解键路径
        parts = key.split('.')
        if len(parts) == 0:
            return "[Missing Text]"
        
        # 取最后一个部分作为基础
        last_part = parts[-1]
        
        # 常见的翻译键模式处理
        friendly_mappings = {
            # 按钮相关
            'start': 'Start',
            'cancel': 'Cancel', 
            'ok': 'OK',
            'yes': 'Yes',
            'no': 'No',
            'browse': 'Browse...',
            
            # 文件操作
            'select_files': 'Select Files',
            'select_folder': 'Select Folder',
            'select_directory': 'Select Directory',
            
            # 状态相关
            'success': 'Success',
            'failed': 'Failed',
            'error': 'Error',
            'warning': 'Warning',
            
            # 通用词汇
            'template': 'Template',
            'language': 'Language',
            'file': 'File',
            'folder': 'Folder',
            'directory': 'Directory',
        }
        
        # 如果有直接映射，使用它
        if last_part in friendly_mappings:
            return friendly_mappings[last_part]
        
        # 否则进行智能转换
        friendly_text = last_part.replace('_', ' ').title()
        
        # 处理一些特殊情况
        if len(friendly_text) > 0:
            # 如果是动词形式，保持原样
            if friendly_text.endswith('ing') or friendly_text.endswith('ed'):
                pass
            # 如果是单个单词且很短，可能是按钮文本
            elif len(friendly_text.split()) == 1 and len(friendly_text) <= 10:
                pass
            # 如果很长，可能是句子，添加省略号
            elif len(friendly_text) > 20:
                friendly_text = friendly_text[:20] + "..."
        
        return friendly_text if friendly_text else f"[{key}]"
    
    def validate_language_completeness(self, language_code: str = None) -> dict:
        """验证语言包的完整性"""
        if language_code is None:
            language_code = self.current_language
        
        result = {
            "language": language_code,
            "is_complete": True,
            "missing_keys": [],
            "total_keys": 0,
            "present_keys": 0,
            "completeness_ratio": 0.0
        }
        
        # 如果没有备用语言，无法验证
        if self.fallback_language not in self.translations:
            if not self.load_language(self.fallback_language):
                result["error"] = f"无法加载备用语言 {self.fallback_language} 进行比较"
                return result
        
        # 如果目标语言没有加载，尝试加载
        if language_code not in self.translations:
            if not self.load_language(language_code):
                result["error"] = f"无法加载语言 {language_code}"
                return result
        
        # 递归收集所有键
        def collect_keys(data, prefix=""):
            keys = []
            if isinstance(data, dict):
                for key, value in data.items():
                    current_key = f"{prefix}.{key}" if prefix else key
                    if isinstance(value, str):
                        keys.append(current_key)
                    elif isinstance(value, dict):
                        keys.extend(collect_keys(value, current_key))
            return keys
        
        # 从备用语言收集所有键作为基准
        baseline_keys = set(collect_keys(self.translations[self.fallback_language]))
        target_keys = set(collect_keys(self.translations[language_code]))
        
        # 计算缺失的键
        missing_keys = baseline_keys - target_keys
        
        result["total_keys"] = len(baseline_keys)
        result["present_keys"] = len(target_keys & baseline_keys)
        result["missing_keys"] = sorted(list(missing_keys))
        result["is_complete"] = len(missing_keys) == 0
        result["completeness_ratio"] = result["present_keys"] / result["total_keys"] if result["total_keys"] > 0 else 1.0
        
        return result
    
    def get_critical_translation_keys(self) -> list:
        """获取关键翻译键列表"""
        return [
            "app.name",
            "app.title",
            "ui.buttons.start",
            "ui.buttons.cancel",
            "ui.buttons.ok",
            "ui.buttons.yes",
            "ui.buttons.no",
            "ui.labels.template",
            "ui.labels.language",
            "ui.options.auto_detect_language",
            "ui.options.remove_emoji",
            "ui.tooltips.remove_emoji",
            "dialogs.pandoc_not_installed.title",
            "dialogs.pandoc_not_installed.message",
            "file_operations.select_markdown_files",
            "file_operations.select_directory",
        ]
    
    def validate_critical_keys(self, language_code: str = None) -> dict:
        """验证关键翻译键的完整性"""
        if language_code is None:
            language_code = self.current_language
        
        critical_keys = self.get_critical_translation_keys()
        result = {
            "language": language_code,
            "critical_keys_complete": True,
            "missing_critical_keys": [],
            "total_critical_keys": len(critical_keys)
        }
        
        if language_code not in self.translations:
            if not self.load_language(language_code):
                result["error"] = f"无法加载语言 {language_code}"
                return result
        
        missing_critical = []
        for key in critical_keys:
            if not self._get_nested_value(self.translations[language_code], key):
                missing_critical.append(key)
        
        result["missing_critical_keys"] = missing_critical
        result["critical_keys_complete"] = len(missing_critical) == 0
        
        return result
    
    def get_translation_stats(self) -> dict:
        """获取翻译统计信息"""
        return {
            "missing_keys_count": len(self.translation_stats["missing_keys"]),
            "fallback_used_count": len(self.translation_stats["fallback_used"]),
            "critical_missing_count": len(self.translation_stats["critical_missing"]),
            "missing_keys": sorted(list(self.translation_stats["missing_keys"])),
            "fallback_used": sorted(list(self.translation_stats["fallback_used"])),
            "critical_missing": sorted(list(self.translation_stats["critical_missing"])),
            "current_language": self.current_language,
            "fallback_language": self.fallback_language
        }
    
    def reset_translation_stats(self):
        """重置翻译统计"""
        self.translation_stats = {
            "missing_keys": set(),
            "fallback_used": set(),
            "critical_missing": set()
        }
    
    def print_translation_report(self):
        """打印翻译报告"""
        # Only print in debug mode
        import os
        if not os.environ.get('DEBUG', '').lower() in ['1', 'true', 'yes']:
            return
            
        stats = self.get_translation_stats()
        
        print(f"\n=== 翻译使用报告 (语言: {stats['current_language']}) ===")
        print(f"缺失翻译键: {stats['missing_keys_count']}")
        print(f"使用备用语言: {stats['fallback_used_count']}")
        print(f"关键翻译缺失: {stats['critical_missing_count']}")
        
        if stats['critical_missing_count'] > 0:
            print(f"\n⚠️ 关键翻译缺失:")
            for key in stats['critical_missing']:
                print(f"  - {key}")
        
        if stats['missing_keys_count'] > 0:
            print(f"\n📋 所有缺失的翻译键:")
            for key in stats['missing_keys']:
                print(f"  - {key}")
        
        if stats['fallback_used_count'] > 0:
            print(f"\n🔄 使用备用语言的翻译键:")
            for key in stats['fallback_used']:
                print(f"  - {key}")
        
        print("=" * 50)
    
    def translate(self, key: str, **kwargs) -> str:
        """翻译指定的键"""
        # 确保当前语言包已加载
        if self.current_language not in self.translations:
            if not self.load_language(self.current_language):
                # 尝试加载备用语言
                if self.fallback_language != self.current_language:
                    if self.fallback_language not in self.translations:
                        self.load_language(self.fallback_language)
        
        # 尝试从当前语言获取翻译
        translation = None
        used_fallback = False
        
        if self.current_language in self.translations:
            translation = self._get_nested_value(self.translations[self.current_language], key)
        
        # 如果当前语言没有翻译，尝试备用语言
        if not translation and self.fallback_language in self.translations:
            translation = self._get_nested_value(self.translations[self.fallback_language], key)
            if translation:
                used_fallback = True
                self.translation_stats["fallback_used"].add(key)
                logging.info(f"使用备用语言翻译: {key} (语言: {self.current_language} -> {self.fallback_language})")
        
        # 如果都没有找到，生成用户友好的显示文本
        if not translation:
            # 统计缺失的键
            self.translation_stats["missing_keys"].add(key)
            
            # 检查是否是关键翻译键
            is_critical = key in self.get_critical_translation_keys()
            if is_critical:
                self.translation_stats["critical_missing"].add(key)
                logging.error(f"关键翻译缺失: {key} (语言: {self.current_language})")
            else:
                logging.warning(f"翻译缺失: {key} (语言: {self.current_language})")
            
            # 生成用户友好的显示文本
            translation = self._generate_friendly_fallback(key)
        
        # 参数替换
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except Exception as e:
                logging.warning(f"翻译参数替换失败 {key}: {e}")
        
        return translation
    
    def t(self, key: str, **kwargs) -> str:
        """translate方法的简写"""
        return self.translate(key, **kwargs)
    
    def refresh_available_languages(self):
        """刷新可用语言列表"""
        self._detect_available_languages()

# 创建全局实例
i18n = I18nManager()

# 提供全局翻译函数
def t(key: str, **kwargs) -> str:
    """全局翻译函数"""
    return i18n.translate(key, **kwargs)

def set_language(lang_code: str) -> bool:
    """设置语言的便捷函数"""
    return i18n.set_language(lang_code)

def get_current_language() -> str:
    """获取当前语言的便捷函数"""
    return i18n.get_current_language()

def get_available_languages() -> Dict[str, Dict[str, str]]:
    """获取可用语言的便捷函数"""
    return i18n.get_available_languages()