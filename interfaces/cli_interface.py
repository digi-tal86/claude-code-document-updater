"""
Command-line interface module for the document processor.

This module provides the CLI handling functionality extracted from the main
process_docs.py file. It includes argument parsing, validation, and the main
CLI entry point while using the modular architecture.

Key Features:
- Complete CLI argument parsing with all existing options
- Enhanced cli_main() function with proper error handling
- Integration with core.processor for processing execution
- Backward compatibility with existing command-line usage
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

# Import from core modules
from core.processor import run_processing

# Configure logging
logger = logging.getLogger(__name__)


def parse_args():
    """
    Parse command line arguments.
    
    Extracted from process_docs.py lines 354-400 with all existing
    CLI arguments and validation.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Concurrently process markdown files using Claude AI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "input_dir",
        type=Path,
        help="Directory containing markdown files to process"
    )
    parser.add_argument(
        "output_dir",
        type=Path,
        help="Directory to save processed files"
    )
    parser.add_argument(
        "template_file",
        type=Path,
        help="Template markdown file for document structure"
    )
    parser.add_argument(
        "--quality-standards",
        type=Path,
        default=None,
        help="Optional quality standards file to verify processed documents against"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="Custom prompt to override the default processing instruction"
    )
    parser.add_argument(
        "-c", "--concurrency",
        type=int,
        default=5,
        help="Maximum number of files to process concurrently"
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retry attempts for failed files"
    )
    
    return parser.parse_args()


async def cli_main():
    """
    Enhanced CLI main function extracted and improved from process_docs.py.
    
    This function handles command-line interface mode with proper error handling
    and integration with the modular architecture. It maintains backward
    compatibility with existing command-line usage.
    
    Extracted from process_docs.py lines 321-325 and enhanced with better
    error handling and validation.
    """
    try:
        # Parse command line arguments
        args = parse_args()
        
        # Validate arguments
        if not _validate_cli_args(args):
            sys.exit(1)
        
        # Execute processing with the modular architecture
        await run_processing(args)
        
    except KeyboardInterrupt:
        logger.info("\nProcess interrupted by user")
        sys.exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        logger.error(f"CLI execution failed: {str(e)}")
        sys.exit(1)


def _validate_cli_args(args) -> bool:
    """
    Validate CLI arguments with proper error reporting.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        bool: True if validation passes, False otherwise
    """
    validation_errors = []
    
    # Validate input directory
    if not args.input_dir.exists():
        validation_errors.append(f"Input directory not found: {args.input_dir}")
    elif not args.input_dir.is_dir():
        validation_errors.append(f"Input path is not a directory: {args.input_dir}")
    
    # Validate template file
    if not args.template_file.exists():
        validation_errors.append(f"Template file not found: {args.template_file}")
    elif not args.template_file.is_file():
        validation_errors.append(f"Template path is not a file: {args.template_file}")
    
    # Validate quality standards file if provided
    if args.quality_standards:
        if not args.quality_standards.exists():
            validation_errors.append(f"Quality standards file not found: {args.quality_standards}")
        elif not args.quality_standards.is_file():
            validation_errors.append(f"Quality standards path is not a file: {args.quality_standards}")
    
    # Validate concurrency parameter
    if args.concurrency < 1:
        validation_errors.append("Concurrency must be at least 1")
    
    # Validate max retries parameter
    if args.max_retries < 0:
        validation_errors.append("Max retries must be 0 or greater")
    
    # Report validation errors
    if validation_errors:
        logger.error("CLI argument validation failed:")
        for error in validation_errors:
            logger.error(f"  - {error}")
        return False
    
    return True


def create_args_from_params(params: dict):
    """
    Create an argparse.Namespace object from parameters dictionary.
    
    This function is used for compatibility with interactive mode
    and other interfaces that need to create args objects programmatically.
    
    Args:
        params: Dictionary containing parameter values
        
    Returns:
        argparse.Namespace: Compatible args object for processing
    """
    # Create a simple namespace object with the required attributes
    class Args:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    return Args(
        input_dir=Path(params.get('input_dir', '.')),
        output_dir=Path(params.get('output_dir', './output')),
        template_file=Path(params.get('template_file', './template.md')),
        quality_standards=Path(params['quality_standards']) if params.get('quality_standards') else None,
        prompt=params.get('prompt'),
        concurrency=params.get('concurrency', 5),
        max_retries=params.get('max_retries', 3)
    )


def print_cli_help():
    """Print CLI help information."""
    parser = argparse.ArgumentParser(
        description="Concurrently process markdown files using Claude AI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("input_dir", type=Path, help="Directory containing markdown files to process")
    parser.add_argument("output_dir", type=Path, help="Directory to save processed files")
    parser.add_argument("template_file", type=Path, help="Template markdown file for document structure")
    parser.add_argument("--quality-standards", type=Path, help="Optional quality standards file")
    parser.add_argument("--prompt", type=str, help="Custom prompt to override default")
    parser.add_argument("-c", "--concurrency", type=int, default=5, help="Maximum concurrent files")
    parser.add_argument("--max-retries", type=int, default=3, help="Maximum retry attempts")
    
    parser.print_help()


# Entry point for CLI mode
if __name__ == "__main__":
    asyncio.run(cli_main())