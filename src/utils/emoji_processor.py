# -*- coding: utf-8 -*-
"""
Emoji处理器 - 用于在转换前清除Markdown文件中的emoji字符
"""

import tempfile
import os
import shutil
import logging
from pathlib import Path
from typing import Optional, Set, Tuple
from .i18n_manager import t

try:
    import emoji
    EMOJI_AVAILABLE = True
except ImportError:
    EMOJI_AVAILABLE = False
    logging.warning("emoji package not available, emoji removal feature will be disabled")

class EmojiProcessor:
    """Emoji处理器，负责创建清理emoji的临时文件并管理文件生命周期"""
    
    def __init__(self):
        # 跟踪当前会话创建的所有临时文件
        self.active_temp_files: Set[str] = set()
        
    def is_available(self) -> bool:
        """检查emoji处理功能是否可用"""
        return EMOJI_AVAILABLE
    
    def create_cleaned_temp_file(self, source_file: Path) -> Optional[Tuple[Path, str]]:
        """
        创建清理了emoji的临时文件
        
        Args:
            source_file: 源Markdown文件路径
            
        Returns:
            元组(临时文件路径, 临时文件ID) 或 None（如果失败）
        """
        if not EMOJI_AVAILABLE:
            logging.error("Emoji package not available, cannot create cleaned temp file")
            return None
            
        if not source_file.exists():
            logging.error(f"Source file does not exist: {source_file}")
            return None
            
        try:
            # 读取源文件内容
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 清理emoji字符
            cleaned_content = emoji.replace_emoji(content, replace='')
            
            # 创建临时文件
            # 使用源文件的扩展名，确保pandoc能正确识别文件类型
            suffix = source_file.suffix or '.md'
            temp_fd, temp_path = tempfile.mkstemp(
                suffix=f'_cleaned{suffix}',
                prefix='md2docx_',
                text=True
            )
            
            # 写入清理后的内容
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            
            # 记录临时文件
            temp_path_obj = Path(temp_path)
            temp_id = temp_path_obj.stem
            self.active_temp_files.add(temp_path)
            
            logging.info(f"Created emoji-cleaned temp file: {temp_path} for {source_file}")
            return temp_path_obj, temp_id
            
        except Exception as e:
            logging.error(f"Failed to create cleaned temp file for {source_file}: {e}")
            return None
    
    def cleanup_temp_file(self, temp_path: Path, temp_id: str = None) -> bool:
        """
        清理指定的临时文件
        
        Args:
            temp_path: 临时文件路径
            temp_id: 临时文件ID（可选，用于日志记录）
            
        Returns:
            是否成功清理
        """
        try:
            temp_path_str = str(temp_path)
            
            if temp_path.exists():
                temp_path.unlink()
                logging.info(f"Cleaned up temp file: {temp_path_str}")
            
            # 从活动文件列表中移除
            self.active_temp_files.discard(temp_path_str)
            return True
            
        except Exception as e:
            logging.error(f"Failed to cleanup temp file {temp_path}: {e}")
            return False
    
    def cleanup_all_temp_files(self) -> int:
        """
        清理所有活动的临时文件
        
        Returns:
            成功清理的文件数量
        """
        cleaned_count = 0
        temp_files_copy = self.active_temp_files.copy()
        
        for temp_path_str in temp_files_copy:
            try:
                temp_path = Path(temp_path_str)
                if self.cleanup_temp_file(temp_path):
                    cleaned_count += 1
            except Exception as e:
                logging.error(f"Error during cleanup of {temp_path_str}: {e}")
        
        if cleaned_count > 0:
            logging.info(f"Cleaned up {cleaned_count} temporary emoji-processed files")
        
        return cleaned_count
    

# 全局emoji处理器实例
emoji_processor = EmojiProcessor()

def cleanup_orphaned_temp_files():
    """清理系统中可能遗留的临时文件"""
    try:
        temp_dir = Path(tempfile.gettempdir())
        cleaned_count = 0
        
        # 查找可能的遗留临时文件
        for temp_file in temp_dir.glob("md2docx_*_cleaned.*"):
            try:
                # 检查文件是否较旧（超过1小时未修改，可能是遗留文件）
                import time
                if time.time() - temp_file.stat().st_mtime > 3600:  # 1小时
                    temp_file.unlink()
                    cleaned_count += 1
                    logging.info(f"Cleaned orphaned temp file: {temp_file}")
            except Exception as e:
                logging.warning(f"Failed to clean orphaned file {temp_file}: {e}")
        
        if cleaned_count > 0:
            logging.info(f"Cleaned {cleaned_count} orphaned temporary files")
            
    except Exception as e:
        logging.warning(f"Failed to cleanup orphaned temp files: {e}")