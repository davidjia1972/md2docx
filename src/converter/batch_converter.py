# -*- coding: utf-8 -*-
import uuid
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from PySide6.QtCore import QThread, Signal, QMutex, QMutexLocker

from .pandoc_wrapper import pandoc, ConversionQuality
from .file_namer import FileNamer
from .progress_tracker import ProgressTracker, ConversionTask, TaskStatus
from templates.template_manager import template_manager
from utils.config_manager import config
from utils.emoji_processor import emoji_processor
from utils.i18n_manager import t

class BatchConverter(QThread):
    """Batch conversion engine, executes document conversion in background thread"""
    
    # Signal definitions
    conversion_started = Signal()                    # Conversion started
    conversion_finished = Signal(dict)               # Conversion finished, returns result summary
    conversion_cancelled = Signal()                  # Conversion cancelled
    error_occurred = Signal(str)                     # Error occurred
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Conversion parameters
        self.md_files: List[str] = []
        self.template_path: Optional[str] = None
        self.conversion_quality = ConversionQuality.STANDARD
        self.custom_args: List[str] = []
        
        # Internal components
        self.file_namer: Optional[FileNamer] = None
        self.progress_tracker = ProgressTracker()
        
        # Thread control
        self.mutex = QMutex()
        self.should_stop = False
        self.is_paused = False
        
        # Temporary file tracking
        self.temp_files_for_cleanup = {}  # task_id -> temp_file_path
        
        # Connect progress tracker signals
        self._connect_progress_signals()
    
    def _connect_progress_signals(self):
        """Connect progress tracker signals"""
        self.progress_tracker.progress_updated.connect(self._on_progress_updated)
        self.progress_tracker.task_started.connect(self._on_task_started)
        self.progress_tracker.task_completed.connect(self._on_task_completed)
        self.progress_tracker.batch_started.connect(self._on_batch_started)
        self.progress_tracker.batch_completed.connect(self._on_batch_completed)
        self.progress_tracker.time_estimated.connect(self._on_time_estimated)
    
    def setup_conversion(self, 
                        md_files: List[str],
                        template_path: Optional[str] = None,
                        quality: ConversionQuality = ConversionQuality.STANDARD,
                        custom_args: Optional[List[str]] = None):
        """Setup conversion parameters"""
        with QMutexLocker(self.mutex):
            self.md_files = md_files.copy()
            self.template_path = template_path
            self.conversion_quality = quality
            self.custom_args = custom_args or []
            
            # Create file namer
            self.file_namer = FileNamer.from_config()
            
            self.should_stop = False
            self.is_paused = False
            
            # Reset temporary file tracking
            self.temp_files_for_cleanup.clear()
    
    def run(self):
        """Execute conversion in background thread"""
        try:
            self._perform_conversion()
        except Exception as e:
            self.error_occurred.emit(t("conversion.unknown_error", error=str(e)))
    
    def _perform_conversion(self):
        """Execute conversion process"""
        # Check if pandoc is available
        if not pandoc.is_pandoc_available():
            self.error_occurred.emit(t("conversion.pandoc_required"))
            return
        
        # Validate template file
        template_file = None
        if self.template_path:
            template_file = Path(self.template_path)
            if not template_file.exists():
                self.error_occurred.emit(t("templates_extended.does_not_exist") + f": {self.template_path}")
                return
        
        # Generate output file mappings
        file_mappings = self._generate_file_mappings()
        if not file_mappings:
            self.error_occurred.emit("No valid input files found")
            return
        
        # Create conversion tasks
        tasks = self._create_conversion_tasks(file_mappings)
        
        # Emit conversion started signal
        self.conversion_started.emit()
        
        # Start batch conversion
        self.progress_tracker.start_batch(tasks)
        
        # Process tasks one by one
        for task in tasks:
            if self.should_stop:
                self._cancel_remaining_tasks(tasks)
                break
            
            # Handle pause
            while self.is_paused and not self.should_stop:
                self.msleep(100)  # Wait 100ms
            
            if self.should_stop:
                break
            
            self._process_single_task(task, template_file)
        
        # If cancelled, emit cancel signal
        if self.should_stop:
            self.conversion_cancelled.emit()
    
    def _generate_file_mappings(self) -> Dict[Path, Path]:
        """Generate file mappings (input -> output)"""
        mappings = {}
        
        if not self.file_namer:
            return mappings
        
        for file_str in self.md_files:
            input_path = Path(file_str)
            if input_path.exists() and input_path.suffix.lower() in {'.md', '.markdown'}:
                output_path = self.file_namer.generate_output_path(input_path)
                mappings[input_path] = output_path
        
        return mappings
    
    def _create_conversion_tasks(self, file_mappings: Dict[Path, Path]) -> List[ConversionTask]:
        """Create conversion task list"""
        tasks = []
        
        for input_path, output_path in file_mappings.items():
            task_id = str(uuid.uuid4())
            file_size = input_path.stat().st_size if input_path.exists() else 0
            
            task = ConversionTask(
                id=task_id,
                input_file=str(input_path),
                output_file=str(output_path),
                status=TaskStatus.PENDING,
                file_size=file_size
            )
            
            tasks.append(task)
        
        return tasks
    
    def _process_single_task(self, task: ConversionTask, template_file: Optional[Path]):
        """Process single conversion task"""
        # Start task
        self.progress_tracker.start_task(task.id)
        
        input_path = Path(task.input_file)
        output_path = Path(task.output_file)
        actual_input_path = input_path
        temp_file_info = None
        
        # Check if emoji removal is enabled
        remove_emoji = config.get("output_settings.remove_emoji", True)
        
        if remove_emoji and emoji_processor.is_available():
            # Create temporary cleaned file
            temp_result = emoji_processor.create_cleaned_temp_file(input_path)
            if temp_result:
                temp_path, temp_id = temp_result
                actual_input_path = temp_path
                temp_file_info = (temp_path, temp_id)
                # Track temp file for cleanup
                self.temp_files_for_cleanup[task.id] = temp_path
        
        # Execute conversion with actual input path (original or cleaned temp)
        success, message = pandoc.convert_file(
            actual_input_path,
            output_path,
            template_file,
            self.conversion_quality,
            self.custom_args
        )
        
        # Cleanup temporary file if it was created
        if temp_file_info:
            temp_path, temp_id = temp_file_info
            emoji_processor.cleanup_temp_file(temp_path, temp_id)
            # Remove from tracking
            self.temp_files_for_cleanup.pop(task.id, None)
        
        # Complete task
        self.progress_tracker.complete_task(task.id, success, message)
    
    def _cancel_remaining_tasks(self, tasks: List[ConversionTask]):
        """Cancel remaining tasks"""
        for task in tasks:
            if task.status == TaskStatus.PENDING:
                self.progress_tracker.cancel_task(task.id)
    
    def stop_conversion(self):
        """Stop conversion"""
        with QMutexLocker(self.mutex):
            self.should_stop = True
            self.is_paused = False
        
        # Cancel batch task
        self.progress_tracker.cancel_batch()
        
        # Cleanup any remaining temporary files
        self._cleanup_temp_files()
    
    
    def _cleanup_temp_files(self):
        """Cleanup any remaining temporary files from current conversion"""
        for task_id, temp_path in self.temp_files_for_cleanup.items():
            emoji_processor.cleanup_temp_file(temp_path)
        self.temp_files_for_cleanup.clear()
    
    # Progress tracker signal handlers
    def _on_progress_updated(self, progress: int, message: str, stats):
        """Progress updated"""
        pass
    
    def _on_task_started(self, task_id: str, filename: str):
        """Task started"""
        pass
    
    def _on_task_completed(self, task_id: str, success: bool, message: str):
        """Task completed"""
        pass
    
    def _on_batch_started(self, total_tasks: int):
        """Batch started"""
        pass
    
    def _on_batch_completed(self, stats):
        """Batch completed"""
        summary = self.progress_tracker.get_task_summary()
        self.conversion_finished.emit(summary)
    
    def _on_time_estimated(self, time_str: str):
        """Time estimate updated"""
        pass

class ConversionManager:
    """Conversion manager providing high-level conversion interface"""
    
    def __init__(self):
        self.converter = BatchConverter()
        self.is_converting = False
        
        # Connect signals
        self.converter.conversion_started.connect(self._on_conversion_started)
        self.converter.conversion_finished.connect(self._on_conversion_finished)
        self.converter.conversion_cancelled.connect(self._on_conversion_cancelled)
        self.converter.error_occurred.connect(self._on_error_occurred)
    
    def start_conversion(self, 
                        md_files: List[str],
                        template_path: Optional[str] = None,
                        quality: ConversionQuality = ConversionQuality.STANDARD) -> bool:
        """Start conversion"""
        if self.is_converting:
            return False
        
        if not md_files:
            return False
        
        # Setup conversion parameters
        self.converter.setup_conversion(md_files, template_path, quality)
        
        # Start conversion thread
        self.converter.start()
        
        return True
    
    def stop_conversion(self):
        """Stop conversion"""
        if self.is_converting:
            self.converter.stop_conversion()
    
    
    def get_progress_tracker(self) -> ProgressTracker:
        """Get progress tracker"""
        return self.converter.progress_tracker
    
    def validate_files_and_template(self, 
                                  md_files: List[str], 
                                  template_path: Optional[str] = None) -> Tuple[bool, str]:
        """Validate files and template"""
        # Check pandoc
        if not pandoc.is_pandoc_available():
            return False, t("validation.pandoc_not_available")
        
        # Check input files
        if not md_files:
            return False, t("validation.no_files_selected")
        
        valid_files = []
        for file_path in md_files:
            path = Path(file_path)
            if path.exists() and path.suffix.lower() in {'.md', '.markdown'}:
                valid_files.append(file_path)
        
        if not valid_files:
            return False, t("validation.no_valid_files")
        
        # Check template file
        if template_path:
            template_file = Path(template_path)
            if not template_file.exists():
                return False, t("validation.template_not_exist", path=template_path)
            
            is_valid, error_msg = pandoc.validate_template(template_file)
            if not is_valid:
                return False, t("validation.template_invalid", error=error_msg)
        
        return True, t("validation.success", count=len(valid_files))
    
    # Signal handlers
    def _on_conversion_started(self):
        """Conversion started"""
        self.is_converting = True
    
    def _on_conversion_finished(self, summary):
        """Conversion finished"""
        self.is_converting = False
    
    def _on_conversion_cancelled(self):
        """Conversion cancelled"""
        self.is_converting = False
    
    def _on_error_occurred(self, error_message):
        """Error occurred"""
        self.is_converting = False

# Global conversion manager instance
conversion_manager = ConversionManager()