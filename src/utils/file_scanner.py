# -*- coding: utf-8 -*-
import os
from pathlib import Path
from typing import List, Set, Iterator, Optional
from PySide6.QtCore import QObject, Signal, QThread

class FileScanner(QObject):
    """��k�h(��~Markdown��"""
    
    # ���I
    file_found = Signal(str)  # Ѱ�������
    scan_progress = Signal(int, str)  # k�ۦ (��p�, SM�U)
    scan_completed = Signal(list)  # kό�އ�h
    scan_error = Signal(str)  # k��
    
    # /�Markdown��iU
    MARKDOWN_EXTENSIONS = {'.md', '.markdown', '.mdown', '.mkd', '.mkdn'}
    
    def __init__(self):
        super().__init__()
        self.found_files = []
        self.scanned_files_count = 0
        self.should_stop = False
    
    def scan_files(self, paths: List[str], recursive: bool = True) -> List[Path]:
        """
        ekχ�
        paths: ���U�h
        recursive: /&Rk�P�U
        ��: Markdown���h
        """
        self.found_files = []
        self.scanned_files_count = 0
        self.should_stop = False
        
        for path_str in paths:
            if self.should_stop:
                break
            
            path = Path(path_str)
            if not path.exists():
                continue
            
            if path.is_file():
                self._process_file(path)
            elif path.is_dir():
                self._scan_directory(path, recursive)
        
        return list(self.found_files)
    
    def _process_file(self, file_path: Path):
        """U*��"""
        if self.is_markdown_file(file_path):
            self.found_files.append(file_path)
            self.file_found.emit(str(file_path))
    
    def _scan_directory(self, directory: Path, recursive: bool):
        """k��U"""
        try:
            if recursive:
                self._scan_recursive(directory)
            else:
                self._scan_single_level(directory)
        except PermissionError:
            self.scan_error.emit(f"�	CP���U: {directory}")
        except Exception as e:
            self.scan_error.emit(f"k��U��: {str(e)}")
    
    def _scan_recursive(self, directory: Path):
        """Rk��U"""
        for root, dirs, files in os.walk(directory):
            if self.should_stop:
                break
            
            root_path = Path(root)
            self.scan_progress.emit(self.scanned_files_count, str(root_path))
            
            # ����U�y��U
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {
                '__pycache__', 'node_modules', '.git', '.svn', '.hg'
            }]
            
            for filename in files:
                if self.should_stop:
                    break
                
                file_path = root_path / filename
                if self.is_markdown_file(file_path):
                    self.found_files.append(file_path)
                    self.file_found.emit(str(file_path))
                    self.scanned_files_count += 1
    
    def _scan_single_level(self, directory: Path):
        """�k�UB�U"""
        try:
            for item in directory.iterdir():
                if self.should_stop:
                    break
                
                if item.is_file() and self.is_markdown_file(item):
                    self.found_files.append(item)
                    self.file_found.emit(str(item))
                    self.scanned_files_count += 1
            
            self.scan_progress.emit(self.scanned_files_count, str(directory))
            
        except PermissionError:
            self.scan_error.emit(f"�	CP���U: {directory}")
    
    def is_markdown_file(self, file_path: Path) -> bool:
        """$�/&:Markdown��"""
        return (file_path.suffix.lower() in self.MARKDOWN_EXTENSIONS and 
                file_path.is_file() and 
                not file_path.name.startswith('.'))
    
    def stop_scan(self):
        """停止扫描"""
        self.should_stop = True

def quick_scan(paths: List[str], recursive: bool = True) -> List[str]:
    """
    快速扫描Markdown文件的便捷函数
    
    Args:
        paths: 要扫描的路径列表
        recursive: 是否递归扫描子目录
        
    Returns:
        找到的Markdown文件路径列表（字符串格式）
    """
    scanner = FileScanner()
    found_files = scanner.scan_files(paths, recursive)
    return [str(f) for f in found_files]
