# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from PySide6.QtCore import QObject, Signal
from utils.i18n_manager import t

class TaskStatus(Enum):
    """Task status"""
    PENDING = "pending"        # Pending
    PROCESSING = "processing"  # Processing
    COMPLETED = "completed"    # Completed
    FAILED = "failed"         # Failed
    CANCELLED = "cancelled"    # Cancelled

@dataclass
class ConversionTask:
    """Conversion task information"""
    id: str
    input_file: str
    output_file: str
    status: TaskStatus = TaskStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    file_size: int = 0  # bytes

@dataclass
class ProgressStats:
    """Progress statistics information"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    cancelled_tasks: int = 0
    start_time: Optional[datetime] = None
    estimated_end_time: Optional[datetime] = None
    average_time_per_task: float = 0.0  # seconds
    
    @property
    def progress_percentage(self) -> int:
        """Progress percentage"""
        if self.total_tasks == 0:
            return 0
        processed = self.completed_tasks + self.failed_tasks + self.cancelled_tasks
        return int((processed / self.total_tasks) * 100)
    
    @property
    def success_rate(self) -> float:
        """Success rate"""
        if self.completed_tasks + self.failed_tasks == 0:
            return 0.0
        return self.completed_tasks / (self.completed_tasks + self.failed_tasks)
    
    @property
    def is_completed(self) -> bool:
        """Check if completed"""
        return (self.completed_tasks + self.failed_tasks + self.cancelled_tasks) >= self.total_tasks
    
    @property
    def elapsed_time(self) -> timedelta:
        """Elapsed time"""
        if self.start_time is None:
            return timedelta()
        return datetime.now() - self.start_time

class ProgressTracker(QObject):
    """Progress tracker"""
    
    # Signal definitions
    progress_updated = Signal(int, str, object)  # Progress percentage, status message, stats object
    task_started = Signal(str, str)              # Task ID, filename
    task_completed = Signal(str, bool, str)      # Task ID, success flag, message
    batch_started = Signal(int)                  # Batch started, total tasks
    batch_completed = Signal(object)             # Batch completed, final stats
    time_estimated = Signal(str)                 # Remaining time estimate
    
    def __init__(self):
        super().__init__()
        self.tasks: Dict[str, ConversionTask] = {}
        self.stats = ProgressStats()
        self.is_cancelled = False
        
    def start_batch(self, tasks: List[ConversionTask]):
        """Start batch tasks"""
        self.tasks.clear()
        self.is_cancelled = False
        
        # Initialize task dictionary
        for task in tasks:
            self.tasks[task.id] = task
        
        # Initialize statistics
        self.stats = ProgressStats(
            total_tasks=len(tasks),
            start_time=datetime.now()
        )
        
        self.batch_started.emit(len(tasks))
        self._update_progress()
    
    def start_task(self, task_id: str) -> bool:
        """Start single task"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = TaskStatus.PROCESSING
        task.start_time = datetime.now()
        
        self.task_started.emit(task_id, task.input_file)
        self._update_progress()
        return True
    
    def complete_task(self, task_id: str, success: bool, message: str = ""):
        """Complete single task"""
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
        task.end_time = datetime.now()
        
        if not success:
            task.error_message = message
        
        # Update statistics
        if success:
            self.stats.completed_tasks += 1
        else:
            self.stats.failed_tasks += 1
        
        self.task_completed.emit(task_id, success, message)
        self._update_progress()
        self._update_time_estimation()
        
        # Check if all completed
        if self.stats.is_completed:
            self._finish_batch()
    
    def cancel_task(self, task_id: str):
        """Cancel single task"""
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        if task.status == TaskStatus.PROCESSING:
            task.status = TaskStatus.CANCELLED
            task.end_time = datetime.now()
            self.stats.cancelled_tasks += 1
            
            self._update_progress()
    
    def cancel_batch(self):
        """Cancel entire batch task"""
        self.is_cancelled = True
        
        # Cancel all unfinished tasks
        for task in self.tasks.values():
            if task.status in [TaskStatus.PENDING, TaskStatus.PROCESSING]:
                task.status = TaskStatus.CANCELLED
                task.end_time = datetime.now()
                self.stats.cancelled_tasks += 1
        
        self._update_progress()
        self._finish_batch()
    
    def _update_progress(self):
        """Update progress information"""
        progress = self.stats.progress_percentage
        
        # Generate status message
        if self.stats.total_tasks == 1:
            # Single file mode
            task = list(self.tasks.values())[0]
            if task.status == TaskStatus.PROCESSING:
                status_msg = t("progress.converting_file", file=task.input_file)
            elif task.status == TaskStatus.COMPLETED:
                status_msg = t("progress.completed")
            elif task.status == TaskStatus.FAILED:
                status_msg = t("progress.failed_with_error", error=task.error_message or "Unknown error")
            else:
                status_msg = t("progress.preparing")
        else:
            # Batch mode
            status_msg = t("progress.batch_progress", current=self.stats.completed_tasks + self.stats.failed_tasks + self.stats.cancelled_tasks, total=self.stats.total_tasks)
        
        self.progress_updated.emit(progress, status_msg, self.stats)
    
    def _update_time_estimation(self):
        """Update time estimation"""
        completed_count = self.stats.completed_tasks + self.stats.failed_tasks
        if completed_count == 0:
            return
        
        # Calculate average processing time
        total_time = 0
        count = 0
        
        for task in self.tasks.values():
            if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] and 
                task.start_time and task.end_time):
                duration = (task.end_time - task.start_time).total_seconds()
                total_time += duration
                count += 1
        
        if count == 0:
            return
        
        self.stats.average_time_per_task = total_time / count
        
        # Estimate remaining time
        remaining_tasks = self.stats.total_tasks - completed_count - self.stats.cancelled_tasks
        if remaining_tasks > 0:
            estimated_remaining_seconds = remaining_tasks * self.stats.average_time_per_task
            self.stats.estimated_end_time = datetime.now() + timedelta(seconds=estimated_remaining_seconds)
            
            # Format remaining time
            if estimated_remaining_seconds < 60:
                time_str = t("progress.time_seconds", seconds=int(estimated_remaining_seconds))
            elif estimated_remaining_seconds < 3600:
                minutes = int(estimated_remaining_seconds / 60)
                time_str = t("progress.time_minutes", minutes=minutes)
            else:
                hours = int(estimated_remaining_seconds / 3600)
                minutes = int((estimated_remaining_seconds % 3600) / 60)
                time_str = t("progress.time_hours", hours=hours, minutes=minutes)
            
            self.time_estimated.emit(t("progress.time_remaining", time=time_str))
    
    def _finish_batch(self):
        """Finish batch task"""
        self.batch_completed.emit(self.stats)
    
    def get_task_summary(self) -> Dict[str, Any]:
        """Get task summary"""
        successful_files = []
        failed_files = []
        
        for task in self.tasks.values():
            if task.status == TaskStatus.COMPLETED:
                successful_files.append(task.input_file)
            elif task.status == TaskStatus.FAILED:
                failed_files.append({
                    "file": task.input_file,
                    "error": task.error_message or "Unknown error"
                })
        
        return {
            "total_files": self.stats.total_tasks,
            "successful": self.stats.completed_tasks,
            "failed": self.stats.failed_tasks,
            "cancelled": self.stats.cancelled_tasks,
            "success_rate": f"{self.stats.success_rate * 100:.1f}%",
            "total_time": str(self.stats.elapsed_time).split('.')[0],  # Remove microseconds
            "successful_files": successful_files,
            "failed_files": failed_files
        }
    
    def get_current_task(self) -> Optional[ConversionTask]:
        """Get currently processing task"""
        for task in self.tasks.values():
            if task.status == TaskStatus.PROCESSING:
                return task
        return None
    
    def reset(self):
        """Reset tracker"""
        self.tasks.clear()
        self.stats = ProgressStats()
        self.is_cancelled = False

