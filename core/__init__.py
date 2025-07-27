"""
Core document processing module.

This module contains the essential functions for processing markdown documents
using Claude AI. It provides the core functionality that can be reused across
different implementations and interfaces.
"""

from .processor import (
    build_prompt,
    process_markdown_file,
    run_processing,
    print_summary,
    ProcessingResult,
    ProgressCounter
)

__all__ = [
    'build_prompt',
    'process_markdown_file', 
    'run_processing',
    'print_summary',
    'ProcessingResult',
    'ProgressCounter'
]