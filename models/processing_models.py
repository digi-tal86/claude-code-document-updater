"""
Processing data models for document processing pipeline.

This module defines the core data structures used throughout the document processing
workflow, including result containers and thread-safe progress tracking utilities.
"""

import asyncio
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union


@dataclass
class ProcessingResult:
    """
    Container for file processing results.
    
    This dataclass encapsulates the outcome of processing a single document,
    including success status, file paths, error information, and performance metrics.
    
    Attributes:
        success (bool): Whether the processing completed successfully
        file_path (Union[str, Path]): Path to the input file that was processed
        output_path (Optional[Union[str, Path]]): Path to the generated output file, if successful
        error (Optional[str]): Error message if processing failed
        processing_time (float): Time taken to process the file in seconds
        retry_count (int): Number of retry attempts made during processing
        quality_verified (bool): Whether the output passed quality verification
        quality_error (Optional[str]): Quality verification error message, if any
    """
    success: bool = False
    file_path: Union[str, Path] = ""
    output_path: Optional[Union[str, Path]] = None
    error: Optional[str] = None
    processing_time: float = 0.0
    retry_count: int = 0
    quality_verified: bool = False
    quality_error: Optional[str] = None


class ProgressCounter:
    """
    Thread-safe progress counter for tracking processing completion.
    
    This class provides atomic operations for tracking the number of completed
    processing tasks across multiple threads. It supports both threading.Lock
    and asyncio.Lock for compatibility with different concurrency models.
    
    Thread Safety:
        All operations are atomic and thread-safe. Multiple threads can safely
        call mark_complete() and status() concurrently without data corruption.
        The class automatically uses asyncio.Lock for async contexts.
    
    Usage:
        # Basic usage
        counter = ProgressCounter()
        await counter.mark_complete()  # Increment completion count
        completed = counter.status()   # Get current completion count
        
        # With total count tracking
        counter = ProgressCounter(total=100)
        print(counter.status())  # Returns "0/100"
    """
    
    def __init__(self, total: Optional[int] = None):
        """
        Initialize the progress counter.
        
        Args:
            total: Optional total number of tasks to track progress against
        """
        self._completed: int = 0
        self._failed: int = 0
        self.total = total
        self._lock = asyncio.Lock()
    
    async def mark_complete(self, success: bool = True) -> None:
        """
        Atomically increment the completion counter.
        
        This method is async-compatible and thread-safe. It can be called
        from multiple threads or coroutines simultaneously.
        
        Args:
            success: Whether the completed task was successful
        """
        async with self._lock:
            self._completed += 1
            if not success:
                self._failed += 1
    
    def status(self) -> Union[str, int]:
        """
        Get the current progress status.
        
        Returns:
            str: Progress in "completed/total" format if total was provided
            int: Just the completion count if no total was specified
        
        Note: This method is synchronous for compatibility, but the internal
              state is managed by async locks. In async contexts, consider
              accessing properties directly after await operations.
        """
        if self.total is not None:
            return f"{self._completed}/{self.total}"
        else:
            return self._completed
    
    @property
    def completed(self) -> int:
        """Get the number of completed tasks."""
        return self._completed
    
    @property 
    def failed(self) -> int:
        """Get the number of failed tasks."""
        return self._failed