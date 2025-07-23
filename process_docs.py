#!/usr/bin/env python3
"""
Markdown Document Processor using Claude Code SDK

This script processes markdown files by using Claude AI to transform them
according to a provided template. It reads all .md files from an input
directory, processes them through Claude with the template as guidance,
and saves the transformed documents to an output directory.

Requirements:
    - Python 3.10+
    - claude-code-sdk
    - Claude Code CLI installed and configured

Usage:
    python process_docs.py <input_dir> <output_dir> <template_file> [--prompt "custom prompt"]

Example:
    python process_docs.py ./raw_docs ./formatted_docs ./template.md
    python process_docs.py ./notes ./reports ./report_template.md --prompt "Convert to formal report"

Author: Claude Assistant
Version: 1.0.0
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional, List
import sys

try:
    from claude_code_sdk import query, ClaudeCodeOptions, Message
except ImportError:
    print("Error: claude-code-sdk not installed. Please run: pip install claude-code-sdk")
    sys.exit(1)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MarkdownProcessor:
    """
    A processor for transforming markdown documents using Claude AI.
    
    This class handles the batch processing of markdown files, using a template
    to guide Claude in transforming documents into a consistent format.
    
    Attributes:
        input_dir (Path): Directory containing markdown files to process
        output_dir (Path): Directory where processed files will be saved
        template_file (Path): Template markdown file used as guidance
        template_content (str): Content of the template file
    """
    
    def __init__(self, input_dir: str, output_dir: str, template_file: str):
        """
        Initialize the MarkdownProcessor with directories and template.
        
        Args:
            input_dir: Path to directory containing .md files to process
            output_dir: Path to directory where processed files will be saved
            template_file: Path to template .md file for document structure
            
        Raises:
            ValueError: If input_dir or template_file doesn't exist
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.template_file = Path(template_file)
        
        if not self.input_dir.exists():
            raise ValueError(f"Input directory '{input_dir}' does not exist")
        
        if not self.template_file.exists():
            raise ValueError(f"Template file '{template_file}' does not exist")
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(self.template_file, 'r', encoding='utf-8') as f:
            self.template_content = f.read()
    
    async def process_file(self, file_path: Path, custom_prompt: Optional[str] = None) -> str:
        """
        Process a single markdown file using Claude AI.
        
        Args:
            file_path: Path to the markdown file to process
            custom_prompt: Optional custom prompt to override the default
            
        Returns:
            str: The processed markdown content
            
        Note:
            If processing fails, returns the original file content
        """
        logger.info(f"Processing: {file_path.name}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        if custom_prompt:
            # Include document and template in custom prompt
            prompt = f"""{custom_prompt}

TEMPLATE TO FOLLOW:
{self.template_content}

DOCUMENT TO TRANSFORM:
{file_content}

Please return only the transformed markdown content without any explanations or additional text."""
        else:
            # Use default prompt
            prompt = f"""Update the following markdown document using the provided template as guidance.

TEMPLATE:
{self.template_content}

DOCUMENT TO UPDATE:
{file_content}

Please return only the updated markdown content without any explanations or additional text."""
        
        messages: list[Message] = []
        
        options = ClaudeCodeOptions(
            max_turns=1,
            system_prompt="You are a markdown document processor. Return only the processed markdown content without any explanations.",
            allowed_tools=[]  # Disable tools to ensure direct response
        )
        
        try:
            async for message in query(prompt=prompt, options=options):
                messages.append(message)
                logger.debug(f"Message type: {type(message)}, Message: {message}")
            
            # Extract text content from messages
            if messages:
                # Look for ResultMessage with result content
                for message in reversed(messages):
                    if hasattr(message, 'result') and message.result:
                        return message.result
                    elif hasattr(message, 'content') and message.content:
                        # Handle AssistantMessage with TextBlock
                        if isinstance(message.content, list):
                            for block in message.content:
                                if hasattr(block, 'text'):
                                    return block.text
                        elif isinstance(message.content, str):
                            return message.content
                
                logger.error(f"No valid content found in messages for {file_path.name}")
                return file_content
            else:
                logger.error(f"No messages received for {file_path.name}")
                return file_content
                
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {str(e)}")
            return file_content
    
    async def process_all_files(self, custom_prompt: Optional[str] = None) -> None:
        """
        Process all markdown files in the input directory.
        
        This method finds all .md files in the input directory, processes each
        one through Claude using the template, and saves the results to the
        output directory. Processing continues even if individual files fail.
        
        Args:
            custom_prompt: Optional custom prompt to use for all files
            
        Note:
            Files are processed sequentially to avoid rate limiting.
            Failed files will retain their original content in the output.
        """
        md_files = list(self.input_dir.glob("*.md"))
        
        if not md_files:
            logger.warning(f"No markdown files found in {self.input_dir}")
            return
        
        logger.info(f"Found {len(md_files)} markdown file(s) to process")
        
        for file_path in md_files:
            try:
                updated_content = await self.process_file(file_path, custom_prompt)
                
                output_path = self.output_dir / file_path.name
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                logger.info(f"Saved updated file: {output_path}")
                
            except Exception as e:
                logger.error(f"Failed to process {file_path.name}: {str(e)}")
                continue
        
        logger.info("Processing complete!")


async def main() -> None:
    """
    Main entry point for the markdown processor script.
    
    Parses command-line arguments, initializes the processor, and runs
    the batch processing operation. Handles errors gracefully with
    appropriate exit codes.
    
    Exit codes:
        0: Success
        1: Configuration or runtime error
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Process markdown files using Claude Code SDK")
    parser.add_argument("input_dir", help="Directory containing markdown files to process")
    parser.add_argument("output_dir", help="Directory to save processed files")
    parser.add_argument("template_file", help="Template markdown file to use as guidance")
    parser.add_argument("--prompt", help="Custom prompt to use (optional)", default=None)
    
    args = parser.parse_args()
    
    try:
        processor = MarkdownProcessor(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            template_file=args.template_file
        )
        
        await processor.process_all_files(custom_prompt=args.prompt)
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())