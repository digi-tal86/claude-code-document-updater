"""
File operations utility module for document processing.

This module provides safe file reading/writing functions, markdown file
discovery, path validation, and directory creation helpers used throughout
the document processing pipeline.
"""

import os
import glob
from pathlib import Path
from typing import List, Optional, Union


def safe_read_file(file_path: Union[str, Path]) -> Optional[str]:
    """
    Safely read a file with proper error handling.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        File content as string, or None if reading fails
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If lacking read permissions
        UnicodeDecodeError: If file encoding is incompatible
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        raise
    except PermissionError:
        print(f"Error: Permission denied reading file: {file_path}")
        raise
    except UnicodeDecodeError as e:
        print(f"Error: Unable to decode file {file_path}: {e}")
        raise
    except Exception as e:
        print(f"Error: Unexpected error reading file {file_path}: {e}")
        raise


def safe_write_file(file_path: Union[str, Path], content: str, create_dirs: bool = True) -> bool:
    """
    Safely write content to a file with proper error handling.
    
    Args:
        file_path: Path to the file to write
        content: Content to write to the file
        create_dirs: Whether to create parent directories if they don't exist
        
    Returns:
        True if write was successful, False otherwise
        
    Raises:
        PermissionError: If lacking write permissions
        OSError: If unable to create directories or write file
    """
    try:
        file_path = Path(file_path)
        
        # Create parent directories if requested and they don't exist
        if create_dirs and not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return True
        
    except PermissionError:
        print(f"Error: Permission denied writing to file: {file_path}")
        raise
    except OSError as e:
        print(f"Error: OS error writing to file {file_path}: {e}")
        raise
    except Exception as e:
        print(f"Error: Unexpected error writing to file {file_path}: {e}")
        raise


def discover_markdown_files(directory: Union[str, Path], recursive: bool = True) -> List[str]:
    """
    Discover markdown files in a directory using glob patterns.
    
    Args:
        directory: Directory to search for markdown files
        recursive: Whether to search recursively in subdirectories
        
    Returns:
        List of markdown file paths found
        
    Raises:
        OSError: If directory doesn't exist or can't be accessed
    """
    try:
        directory = Path(directory)
        
        if not directory.exists():
            raise OSError(f"Directory does not exist: {directory}")
            
        if not directory.is_dir():
            raise OSError(f"Path is not a directory: {directory}")
        
        # Use glob patterns to find markdown files
        pattern = "**/*.md" if recursive else "*.md"
        markdown_files = list(directory.glob(pattern))
        
        # Convert to strings and sort for consistent ordering
        return sorted([str(file) for file in markdown_files])
        
    except OSError:
        raise
    except Exception as e:
        print(f"Error: Unexpected error discovering markdown files in {directory}: {e}")
        raise


def validate_path(path: Union[str, Path], must_exist: bool = False, must_be_file: bool = False) -> bool:
    """
    Validate a file or directory path.
    
    Args:
        path: Path to validate
        must_exist: Whether the path must exist
        must_be_file: Whether the path must be a file (only checked if must_exist=True)
        
    Returns:
        True if path is valid according to criteria, False otherwise
    """
    try:
        path = Path(path)
        
        if must_exist:
            if not path.exists():
                return False
                
            if must_be_file and not path.is_file():
                return False
                
        return True
        
    except Exception as e:
        print(f"Error: Invalid path {path}: {e}")
        return False


def ensure_directory_exists(directory: Union[str, Path]) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path to ensure exists
        
    Returns:
        True if directory exists or was created successfully, False otherwise
        
    Raises:
        PermissionError: If lacking permissions to create directory
        OSError: If unable to create directory for other reasons
    """
    try:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        return True
        
    except PermissionError:
        print(f"Error: Permission denied creating directory: {directory}")
        raise
    except OSError as e:
        print(f"Error: OS error creating directory {directory}: {e}")
        raise
    except Exception as e:
        print(f"Error: Unexpected error creating directory {directory}: {e}")
        raise


def get_file_extension(file_path: Union[str, Path]) -> str:
    """
    Get the file extension from a file path.
    
    Args:
        file_path: Path to get extension from
        
    Returns:
        File extension (including the dot), or empty string if no extension
    """
    return Path(file_path).suffix


def get_filename_without_extension(file_path: Union[str, Path]) -> str:
    """
    Get the filename without extension from a file path.
    
    Args:
        file_path: Path to get filename from
        
    Returns:
        Filename without extension
    """
    return Path(file_path).stem