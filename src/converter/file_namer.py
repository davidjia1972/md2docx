# -*- coding: utf-8 -*-
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from enum import Enum

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config_manager import get_config

class NamingStrategy(Enum):
    """File naming strategy"""
    TIMESTAMP = "timestamp"  # Timestamp suffix
    INCREMENT = "increment"   # Number increment suffix

class FileNamer:
    """Smart file namer, handles output filename conflicts"""
    
    def __init__(self, 
                 strategy: NamingStrategy = NamingStrategy.TIMESTAMP,
                 overwrite: bool = False,
                 output_dir: Optional[str] = None):
        """
        Initialize file namer
        strategy: Naming strategy
        overwrite: Whether to overwrite files with same name
        output_dir: Custom output directory, None means same as source file
        """
        self.strategy = strategy
        self.overwrite = overwrite
        self.output_dir = Path(output_dir) if output_dir else None
        
        # Track generated filenames to avoid duplicates in batch processing
        self._used_names = set()
    
    @classmethod
    def from_config(cls) -> 'FileNamer':
        """Create file namer from config file"""
        config = get_config()
        output_settings = config.get_output_settings()
        
        strategy_str = output_settings.get("naming_strategy", "timestamp")
        strategy = NamingStrategy.TIMESTAMP if strategy_str == "timestamp" else NamingStrategy.INCREMENT
        
        overwrite = output_settings.get("overwrite_files", False)
        
        return cls(strategy=strategy, overwrite=overwrite)
    
    def generate_output_path(self, md_path: Path) -> Path:
        """
        Generate output DOCX path for Markdown file
        md_path: Source Markdown file path
        Returns: Output DOCX file path
        """
        # Determine output directory
        if self.output_dir:
            output_dir = self.output_dir
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = md_path.parent
        
        # Base output filename
        base_name = md_path.stem
        base_path = output_dir / f"{base_name}.docx"
        
        # If overwrite allowed or file doesn't exist, return directly
        if self.overwrite or (not base_path.exists() and str(base_path) not in self._used_names):
            self._used_names.add(str(base_path))
            return base_path
        
        # Handle filename conflicts
        final_path = self._resolve_conflict(base_path)
        self._used_names.add(str(final_path))
        return final_path
    
    def _resolve_conflict(self, base_path: Path) -> Path:
        """Resolve filename conflicts"""
        if self.strategy == NamingStrategy.TIMESTAMP:
            return self._generate_timestamp_name(base_path)
        else:
            return self._generate_increment_name(base_path)
    
    def _generate_timestamp_name(self, base_path: Path) -> Path:
        """Generate filename with timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_stem = f"{base_path.stem}_{timestamp}"
        new_path = base_path.with_stem(new_stem)
        
        # If timestamp filename also conflicts, add milliseconds
        if new_path.exists() or str(new_path) in self._used_names:
            timestamp_ms = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # Precision to milliseconds
            new_stem = f"{base_path.stem}_{timestamp_ms}"
            new_path = base_path.with_stem(new_stem)
        
        return new_path
    
    def _generate_increment_name(self, base_path: Path) -> Path:
        """Generate filename with incrementing number"""
        counter = 1
        while True:
            new_stem = f"{base_path.stem}({counter})"
            new_path = base_path.with_stem(new_stem)
            
            if not new_path.exists() and str(new_path) not in self._used_names:
                return new_path
            
            counter += 1
            
            # Prevent infinite loop
            if counter > 9999:
                # If increment to 9999 still no match, use timestamp strategy
                return self._generate_timestamp_name(base_path)
    
    
    def clear_used_names(self):
        """Clear used filename records"""
        self._used_names.clear()

