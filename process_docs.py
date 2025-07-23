#!/usr/bin/env python3
"""
Concurrent Markdown Document Processor using Claude Code SDK

This script processes markdown files concurrently using Claude AI to transform
them according to a provided template. It supports configurable concurrency
limits, comprehensive error handling, and detailed progress reporting.

Key Features:
- Concurrent processing with configurable limits
- Retry logic for transient failures
- Progress tracking with real-time updates
- Comprehensive error reporting
- Support for custom prompts

Requirements:
    - Python 3.10+
    - claude-code-sdk
    - Claude Code CLI installed and configured

Usage:
    python process_docs_concurrent.py <input_dir> <output_dir> <template_file> [options]

Examples:
    python process_docs_concurrent.py ./raw_docs ./formatted_docs ./template.md -c 10
    python process_docs_concurrent.py ./notes ./reports ./report_template.md --prompt "Convert to formal report"

Author: Claude Assistant
Version: 2.0.0
"""

import asyncio
import logging
import argparse
from pathlib import Path
import sys
import time
from typing import Optional, Tuple, List
from dataclasses import dataclass
from datetime import datetime

try:
    from claude_code_sdk import query, ClaudeCodeOptions, Message
except ImportError:
    print(
        "Error: claude-code-sdk not installed. Please run: pip install claude-code-sdk",
        file=sys.stderr,
    )
    sys.exit(1)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of processing a single file."""
    success: bool
    file_path: Path
    output_path: Optional[Path]
    error: Optional[str]
    processing_time: float
    retry_count: int


class ProgressTracker:
    """Tracks and displays processing progress."""
    
    def __init__(self, total_files: int):
        self.total = total_files
        self.completed = 0
        self.failed = 0
        self.lock = asyncio.Lock()
    
    async def increment(self, success: bool = True):
        """Increment the counter thread-safely."""
        async with self.lock:
            self.completed += 1
            if not success:
                self.failed += 1
    
    def get_status(self) -> str:
        """Get current progress status."""
        return f"{self.completed}/{self.total} completed ({self.failed} failed)"


async def process_markdown_file(
    input_path: Path,
    output_path: Path,
    template_content: str,
    semaphore: asyncio.Semaphore,
    progress: ProgressTracker,
    custom_prompt: Optional[str] = None,
    max_retries: int = 3,
) -> ProcessingResult:
    """
    Process a single markdown file using Claude with retry logic.

    Args:
        input_path: Path to the source markdown file
        output_path: Path to write the transformed file
        template_content: Content of the template file
        semaphore: Semaphore to limit concurrent API calls
        progress: Progress tracker instance
        custom_prompt: Optional custom prompt to override default
        max_retries: Maximum number of retry attempts

    Returns:
        ProcessingResult with status and details
    """
    start_time = time.time()
    retry_count = 0
    
    async with semaphore:
        for attempt in range(max_retries):
            try:
                logger.info(f"[{progress.get_status()}] Processing: {input_path.name}")
                
                # Read input file
                file_content = input_path.read_text(encoding="utf-8")
                
                # Get current date for "Last updated" field
                current_date = datetime.now().strftime("%B %d, %Y")
                
                # Construct prompt with date information
                if custom_prompt:
                    prompt = f"""{custom_prompt}

TEMPLATE TO FOLLOW:
{template_content}

DOCUMENT TO TRANSFORM:
{file_content}

IMPORTANT: Replace any "[Date]" placeholders with today's date: {current_date}

Please return only the transformed markdown content without any explanations or additional text."""
                else:
                    prompt = f"""Update the following markdown document using the provided template as guidance.

TEMPLATE:
{template_content}

DOCUMENT TO UPDATE:
{file_content}

IMPORTANT: Replace any "[Date]" placeholders with today's date: {current_date}

Please return only the updated markdown content without any explanations or additional text."""
                
                # Configure Claude options
                options = ClaudeCodeOptions(
                    max_turns=1,
                    system_prompt="You are a markdown document processor. Your response must be ONLY the processed markdown content. Do not use any tools, do not provide explanations, do not ask questions. Output only the formatted markdown document."
                )
                
                # Process with Claude
                messages = []
                async for message in query(prompt=prompt, options=options):
                    messages.append(message)
                
                # Extract content from messages
                response_content = None
                for message in reversed(messages):
                    if hasattr(message, 'result') and message.result:
                        response_content = message.result
                        break
                    elif hasattr(message, 'content') and message.content:
                        if isinstance(message.content, list):
                            for block in message.content:
                                if hasattr(block, 'text'):
                                    response_content = block.text
                                    break
                        elif isinstance(message.content, str):
                            response_content = message.content
                            break
                
                if not response_content:
                    raise ValueError("Received empty response from Claude")
                
                # Save output
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(response_content, encoding="utf-8")
                
                # Update progress and log success
                await progress.increment(success=True)
                processing_time = time.time() - start_time
                logger.info(
                    f"[{progress.get_status()}] ✓ Completed: {output_path.name} "
                    f"({processing_time:.1f}s)"
                )
                
                return ProcessingResult(
                    success=True,
                    file_path=input_path,
                    output_path=output_path,
                    error=None,
                    processing_time=processing_time,
                    retry_count=retry_count
                )
                
            except Exception as e:
                retry_count += 1
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(
                        f"[{progress.get_status()}] Retry {retry_count}/{max_retries-1} "
                        f"for {input_path.name} after error: {str(e)}. "
                        f"Waiting {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    # Final failure
                    await progress.increment(success=False)
                    processing_time = time.time() - start_time
                    logger.error(
                        f"[{progress.get_status()}] ✗ Failed: {input_path.name} "
                        f"after {retry_count} retries: {str(e)}"
                    )
                    
                    return ProcessingResult(
                        success=False,
                        file_path=input_path,
                        output_path=None,
                        error=str(e),
                        processing_time=processing_time,
                        retry_count=retry_count
                    )


def print_summary(results: List[ProcessingResult], total_time: float) -> None:
    """Print a detailed summary of processing results."""
    successes = [r for r in results if r.success]
    failures = [r for r in results if not r.success]
    
    print("\n" + "=" * 60)
    print(" " * 20 + "PROCESSING SUMMARY")
    print("=" * 60)
    print(f"Total files processed: {len(results)}")
    print(f"Successful: {len(successes)}")
    print(f"Failed: {len(failures)}")
    print(f"Total time: {total_time:.1f}s")
    
    if successes:
        avg_time = sum(r.processing_time for r in successes) / len(successes)
        print(f"Average processing time: {avg_time:.1f}s per file")
    
    print(f"Concurrent processing speedup: {sum(r.processing_time for r in results) / total_time:.1f}x")
    
    if failures:
        print("\n" + "-" * 60)
        print("FAILED FILES:")
        print("-" * 60)
        for result in failures:
            print(f"  • {result.file_path.name}")
            print(f"    Error: {result.error}")
            print(f"    Retries: {result.retry_count}")
    
    print("=" * 60)


async def main() -> None:
    """Main entry point for the concurrent processor."""
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
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.input_dir.is_dir():
        logger.error(f"Input directory not found: {args.input_dir}")
        sys.exit(1)
    
    if not args.template_file.is_file():
        logger.error(f"Template file not found: {args.template_file}")
        sys.exit(1)
    
    if args.concurrency < 1:
        logger.error("Concurrency must be at least 1")
        sys.exit(1)
    
    # Setup
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        template_content = args.template_file.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to read template file: {e}")
        sys.exit(1)
    
    # Find markdown files
    md_files = list(args.input_dir.glob("*.md"))
    if not md_files:
        logger.warning(f"No markdown files found in {args.input_dir}")
        return
    
    concurrency_mode = "sequential" if args.concurrency == 1 else f"concurrent (limit: {args.concurrency})"
    logger.info(f"Found {len(md_files)} markdown files. Starting {concurrency_mode} processing...")
    
    if len(md_files) <= 10:
        # Show file list for small batches
        logger.info(f"Files to process: {', '.join(f.name for f in md_files)}")
    else:
        # Just show first few for large batches
        logger.info(f"Files include: {', '.join(f.name for f in md_files[:3])}, ... and {len(md_files) - 3} more")
    
    # Process files concurrently
    start_time = time.time()
    semaphore = asyncio.Semaphore(args.concurrency)
    progress = ProgressTracker(len(md_files))
    
    tasks = [
        process_markdown_file(
            input_path=file_path,
            output_path=args.output_dir / file_path.name,
            template_content=template_content,
            semaphore=semaphore,
            progress=progress,
            custom_prompt=args.prompt,
            max_retries=args.max_retries,
        )
        for file_path in md_files
    ]
    
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    # Print summary
    print_summary(results, total_time)
    
    # Exit with error code if any failures
    if any(not r.success for r in results):
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nProcess interrupted by user")
        sys.exit(130)  # Standard exit code for SIGINT