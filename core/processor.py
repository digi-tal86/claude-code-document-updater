"""
Core document processing module for markdown files using Claude AI.

This module contains the essential functions for processing markdown documents
with Claude AI, including prompt building, file processing with retry logic,
batch orchestration, and results summarization.

Key Features:
- Async file processing with configurable concurrency
- Quality standards verification
- Retry logic with exponential backoff
- Progress tracking and comprehensive error handling
- Batch processing orchestration

Dependencies:
- claude_code_sdk for AI processing
- Future modules (placeholder imports with comments)
"""

import asyncio
import logging
import time
import os
import glob
import sys
from pathlib import Path
from typing import Optional, Tuple, List
from datetime import datetime

# Import centralized Claude client
from utils.claude_client import claude_query

# Import from data models module
from models.processing_models import ProcessingResult, ProgressCounter

# Import from quality verifier module
from core.quality_verifier import verify_quality_standards

# Configure logging
logger = logging.getLogger(__name__)


def build_prompt(template_content: str, file_content: str, current_date: str, quality_standards: Optional[str] = None, custom_instruction: Optional[str] = None) -> str:
    """Build processing prompt with template, content, date, and quality standards."""
    instruction = custom_instruction or "Update the following markdown document using the provided template as guidance."
    
    quality_section = ""
    if quality_standards:
        quality_section = f"""

QUALITY STANDARDS:
{quality_standards}

IMPORTANT: Ensure the processed document meets all the quality standards specified above."""
    
    return f"""{instruction}

TEMPLATE:
{template_content}{quality_section}

DOCUMENT TO UPDATE:
{file_content}

IMPORTANT: Replace any "[Date]" placeholders with today's date: {current_date}

Please return only the updated markdown content without any explanations or additional text."""


async def process_markdown_file(
    input_path: Path,
    output_path: Path,
    template_content: str,
    quality_standards: Optional[str],
    semaphore: asyncio.Semaphore,
    progress: ProgressCounter,
    custom_prompt: Optional[str] = None,
    max_retries: int = 3,
) -> ProcessingResult:
    """
    Process a single markdown file using Claude with retry logic and quality verification.

    Args:
        input_path: Path to the source markdown file
        output_path: Path to write the transformed file
        template_content: Content of the template file
        quality_standards: Optional quality standards for verification
        semaphore: Semaphore to limit concurrent API calls
        progress: Progress counter instance
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
                logger.info(f"[{progress.status()}] Processing: {input_path.name}")
                
                # Read input file
                file_content = input_path.read_text(encoding="utf-8")
                
                # Get current date for "Last updated" field
                current_date = datetime.now().strftime("%B %d, %Y")
                
                # Build prompt
                prompt = build_prompt(template_content, file_content, current_date, quality_standards, custom_prompt)
                
                # Process with Claude using centralized client
                response_content = await claude_query(
                    prompt=prompt,
                    operation_name="document_processing"
                )
                
                # Verify quality standards if provided
                quality_verified = True
                quality_error = None
                
                if quality_standards:
                    quality_verified, quality_error = await verify_quality_standards(
                        response_content, quality_standards, input_path.name
                    )
                    
                    if not quality_verified:
                        logger.warning(f"Quality verification failed for {input_path.name}: {quality_error}")
                        # If quality verification fails, treat it as a processing failure to trigger retry
                        raise ValueError(f"Quality verification failed: {quality_error}")
                
                # Save output only if quality verification passed (or no quality standards provided)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(response_content, encoding="utf-8")
                
                # Update progress and log success
                await progress.mark_complete(success=True)
                processing_time = time.time() - start_time
                logger.info(f"✓ {output_path.name} ({processing_time:.1f}s)")
                
                return ProcessingResult(
                    success=True,
                    file_path=input_path,
                    output_path=output_path,
                    error=None,
                    processing_time=processing_time,
                    retry_count=retry_count,
                    quality_verified=quality_verified,
                    quality_error=quality_error
                )
                
            except Exception as e:
                retry_count += 1
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(
                        f"Retry {retry_count}/{max_retries-1} for {input_path.name}: {str(e)}. "
                        f"Waiting {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    # Final failure
                    await progress.mark_complete(success=False)
                    processing_time = time.time() - start_time
                    logger.error(f"✗ {input_path.name} failed after {retry_count} retries: {str(e)}")
                    
                    return ProcessingResult(
                        success=False,
                        file_path=input_path,
                        output_path=None,
                        error=str(e),
                        processing_time=processing_time,
                        retry_count=retry_count,
                        quality_verified=False,
                        quality_error=None
                    )


def print_summary(results: List[ProcessingResult], total_time: float) -> None:
    """Print a detailed summary of processing results."""
    successes = [r for r in results if r.success]
    failures = [r for r in results if not r.success]
    quality_verified = [r for r in successes if r.quality_verified]
    quality_failed = [r for r in successes if not r.quality_verified]
    
    print("\n" + "=" * 60)
    print(" " * 20 + "PROCESSING SUMMARY")
    print("=" * 60)
    print(f"Total files processed: {len(results)}")
    print(f"Successful: {len(successes)}")
    print(f"Failed: {len(failures)}")
    print(f"Total time: {total_time:.1f}s")
    
    # Quality verification summary
    if any(hasattr(r, 'quality_verified') for r in results):
        print(f"\nQuality Verification:")
        print(f"  Passed: {len(quality_verified)}")
        print(f"  Failed: {len(quality_failed)}")
    
    if successes:
        avg_time = sum(r.processing_time for r in successes) / len(successes)
        print(f"Average processing time: {avg_time:.1f}s per file")
        
        # Show theoretical vs actual time (not a "speedup" metric)
        total_sequential_time = sum(r.processing_time for r in results)
        efficiency = (total_sequential_time / total_time) if total_time > 0 else 0
        print(f"Parallelization efficiency: {efficiency:.1f}x (theoretical max: concurrency level)")
    
    if failures:
        print("\n" + "-" * 60)
        print("FAILED FILES:")
        print("-" * 60)
        for result in failures:
            print(f"  • {result.file_path.name}")
            print(f"    Error: {result.error}")
            print(f"    Retries: {result.retry_count}")
    
    if quality_failed:
        print("\n" + "-" * 60)
        print("QUALITY VERIFICATION FAILED:")
        print("-" * 60)
        for result in quality_failed:
            print(f"  • {result.file_path.name}")
            print(f"    Reason: {result.quality_error}")
    
    print("=" * 60)


async def run_processing(args):
    """Execute the document processing with given arguments."""
    
    # Validate inputs
    if not args.input_dir.is_dir():
        logger.error(f"Input directory not found: {args.input_dir}")
        sys.exit(1)
    
    if not args.template_file.is_file():
        logger.error(f"Template file not found: {args.template_file}")
        sys.exit(1)
    
    if args.quality_standards and not args.quality_standards.is_file():
        logger.error(f"Quality standards file not found: {args.quality_standards}")
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
    
    # Read quality standards if provided
    quality_standards = None
    if args.quality_standards:
        try:
            quality_standards = args.quality_standards.read_text(encoding="utf-8")
            logger.info(f"Loaded quality standards from: {args.quality_standards}")
        except Exception as e:
            logger.error(f"Failed to read quality standards file: {e}")
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
    progress = ProgressCounter(len(md_files))
    
    tasks = [
        process_markdown_file(
            input_path=file_path,
            output_path=args.output_dir / file_path.name,
            template_content=template_content,
            quality_standards=quality_standards,
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