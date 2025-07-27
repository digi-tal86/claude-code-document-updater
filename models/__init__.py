"""
Data models module for the document processor.

This module contains shared data structures used across the document processing pipeline,
including result containers and progress tracking utilities.
"""

from .processing_models import ProcessingResult, ProgressCounter

__all__ = ['ProcessingResult', 'ProgressCounter']