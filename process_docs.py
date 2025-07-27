#!/usr/bin/env python3
"""
Concurrent Markdown Document Processor using Claude Code SDK

This script processes markdown files concurrently using Claude AI to transform
them according to a provided template. It supports configurable concurrency
limits, comprehensive error handling, and detailed progress reporting.

Key Features:
- Concurrent processing with configurable limits
- Quality standards verification for processed documents
- Retry logic for transient failures
- Progress tracking with real-time updates
- Comprehensive error reporting
- Support for custom prompts

Requirements:
    - Python 3.10+
    - claude-code-sdk
    - Claude Code CLI installed and configured

Usage:
    python process_docs.py <input_dir> <output_dir> <template_file> [options]

Examples:
    python process_docs.py ./raw_docs ./formatted_docs ./template.md -c 10
    python process_docs.py ./notes ./reports ./report_template.md --quality-standards ./standards.md
    python process_docs.py ./notes ./reports ./report_template.md --prompt "Convert to formal report"

Author: Claude Assistant
Version: 2.0.0
"""

import asyncio
import logging
import sys
from pathlib import Path

# Import from new modular architecture
from interfaces.cli_interface import cli_main, parse_args, create_args_from_params
from core.processor import run_processing

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def main():
    """Main function to orchestrate the document processing."""
    # Check if interactive mode should be used (no command line arguments provided)
    if len(sys.argv) == 1:
        interactive_main()
    else:
        # Use the new modular CLI interface
        asyncio.run(cli_main())


def interactive_main():
    """Interactive mode with guided input collection - delegates to modular interface"""
    from interfaces.interactive_interface import interactive_main as modular_interactive_main
    asyncio.run(modular_interactive_main())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nProcess interrupted by user")
        sys.exit(130)  # Standard exit code for SIGINT