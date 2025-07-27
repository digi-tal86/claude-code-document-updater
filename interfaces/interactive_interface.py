#!/usr/bin/env python3
"""
Interactive Interface Module

Provides a comprehensive interactive mode for document processing with enhanced UX,
guided workflows, input validation, and integration with the modular architecture.
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from interfaces.cli_interface import create_args_from_params
from core.processor import run_processing
from utils.file_operations import (
    discover_markdown_files, 
    safe_read_file,
    safe_write_file,
    ensure_directory_exists,
    validate_path
)


async def interactive_main() -> None:
    """
    Main interactive mode entry point.
    
    Provides a complete guided workflow for document processing with:
    - Welcome screen and instructions
    - Step-by-step parameter collection
    - Configuration confirmation
    - Processing execution with progress feedback
    """
    try:
        print_welcome()
        
        # Collect all parameters through guided workflow
        params = collect_interactive_parameters()
        
        if not params:
            print("\n❌ Interactive mode cancelled.")
            return
        
        # Convert to args object for processing
        args = create_args_from_interactive_params(params)
        
        # Confirm configuration before processing
        if not confirm_configuration(params, args):
            print("\n❌ Processing cancelled.")
            return
        
        print("\n🚀 Starting document processing...")
        print("=" * 60)
        
        # Execute processing using the modular architecture
        success = await run_processing(args)
        
        if success:
            print("\n✅ Document processing completed successfully!")
            print(f"📁 Output directory: {args.output_dir}")
        else:
            print("\n❌ Document processing failed. Check the logs above for details.")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Interactive mode interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error in interactive mode: {str(e)}")
        print("Please check your inputs and try again.")


def print_welcome() -> None:
    """
    Display welcome screen and instructions for interactive mode.
    """
    print("\n" + "=" * 60)
    print("🤖 CLAUDE DOCUMENT PROCESSOR - INTERACTIVE MODE")
    print("=" * 60)
    print("""
Welcome to the interactive document processing workflow!

This guided process will help you:
• Select input directories containing Markdown files
• Choose output location for processed documents  
• Configure template files and processing options
• Set quality standards and concurrency settings
• Review configuration before processing

You can press Ctrl+C at any time to exit.
""")
    print("=" * 60)


def collect_interactive_parameters() -> Optional[Dict[str, Any]]:
    """
    Comprehensive parameter collection workflow with validation and guidance.
    
    Returns:
        Dictionary of parameters for processing, or None if cancelled
    """
    params = {}
    
    try:
        # Step 1: Input Directory Selection
        print("\n📂 STEP 1: Input Directory Selection")
        print("-" * 40)
        input_dir = get_input_directory()
        if not input_dir:
            return None
        params['input_dir'] = input_dir
        
        # Step 2: Output Directory Selection  
        print("\n📤 STEP 2: Output Directory Selection")
        print("-" * 40)
        output_dir = get_output_directory()
        if not output_dir:
            return None
        params['output_dir'] = output_dir
        
        # Step 3: Template File Selection
        print("\n📋 STEP 3: Template File Selection")
        print("-" * 40)
        template_file = get_template_file()
        if not template_file:
            return None
        params['template_file'] = template_file
        
        # Step 4: Optional Parameters
        print("\n⚙️  STEP 4: Optional Parameters")
        print("-" * 40)
        optional_params = get_optional_parameters()
        params.update(optional_params)
        
        return params
        
    except KeyboardInterrupt:
        return None


def create_args_from_interactive_params(params: Dict[str, Any]) -> Any:
    """
    Convert interactive parameters to args object using CLI interface.
    
    This delegates to the existing CLI interface function to maintain consistency
    and avoid code duplication in the modular architecture.
    
    Args:
        params: Dictionary of parameters collected interactively
        
    Returns:
        Args object compatible with the processor
    """
    # Use the existing CLI interface function to maintain consistency
    return create_args_from_params(params)


def confirm_configuration(params: Dict[str, Any], args: Any) -> bool:
    """
    Display configuration summary and get user confirmation.
    
    Args:
        params: Raw parameters collected interactively
        args: Processed args object for execution
        
    Returns:
        True if user confirms, False otherwise
    """
    print("\n📋 CONFIGURATION SUMMARY")
    print("=" * 50)
    
    # Display input directory info
    input_files = discover_markdown_files(params['input_dir'])
    print(f"📂 Input Directory: {params['input_dir']}")
    print(f"   Found {len(input_files)} Markdown files")
    
    # Display output directory info
    print(f"📤 Output Directory: {params['output_dir']}")
    if not os.path.exists(params['output_dir']):
        print("   (Directory will be created)")
    
    # Display template info
    template_path = params['template_file']
    template_size = get_file_size_mb(template_path)
    print(f"📋 Template File: {template_path}")
    print(f"   Size: {template_size:.2f} MB")
    
    # Display processing options
    print(f"🔄 Concurrency: {params.get('max_concurrent', 3)} files")
    print(f"⭐ Quality Standard: {params.get('quality_standard', 'standard')}")
    
    if params.get('custom_prompt'):
        print(f"💬 Custom Prompt: Yes")
    
    if params.get('skip_processed'):
        print(f"⏭️  Skip Processed: Yes")
    
    print("\n" + "=" * 50)
    
    while True:
        response = input("\n❓ Proceed with this configuration? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")


def get_input_directory() -> Optional[str]:
    """
    Interactive input directory selection with validation and browsing support.
    
    Returns:
        Valid input directory path, or None if cancelled
    """
    print("Select the directory containing Markdown files to process.")
    print("💡 Tip: You can browse directories or enter a path directly.")
    
    while True:
        print(f"\nCurrent directory: {os.getcwd()}")
        choice = input("\nChoose an option:\n"
                      "  1. Enter directory path directly\n"
                      "  2. Browse directories from current location\n"
                      "  3. Browse directories from home\n"
                      "  4. Cancel\n"
                      "Enter choice (1-4): ").strip()
        
        if choice == '1':
            path = input("Enter input directory path: ").strip()
            if not path:
                continue
            result = validate_input_directory(path)
            if result:
                return result
                
        elif choice == '2':
            result = browse_directories(os.getcwd(), "Select input directory")
            if result:
                validated = validate_input_directory(result)
                if validated:
                    return validated
                    
        elif choice == '3':
            result = browse_directories(str(Path.home()), "Select input directory")
            if result:
                validated = validate_input_directory(result)
                if validated:
                    return validated
                    
        elif choice == '4':
            return None
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")


def get_output_directory() -> Optional[str]:
    """
    Interactive output directory selection with creation support.
    
    Returns:
        Valid output directory path, or None if cancelled
    """
    print("Select the output directory for processed files.")
    print("💡 Tip: Directory will be created if it doesn't exist.")
    
    while True:
        print(f"\nCurrent directory: {os.getcwd()}")
        choice = input("\nChoose an option:\n"
                      "  1. Enter directory path directly\n"
                      "  2. Browse directories from current location\n"
                      "  3. Browse directories from home\n"
                      "  4. Cancel\n"
                      "Enter choice (1-4): ").strip()
        
        if choice == '1':
            path = input("Enter output directory path: ").strip()
            if not path:
                continue
            
            # Expand path and validate
            expanded_path = os.path.expanduser(path)
            abs_path = os.path.abspath(expanded_path)
            
            if os.path.exists(abs_path):
                if not os.path.isdir(abs_path):
                    print(f"❌ Path exists but is not a directory: {abs_path}")
                    continue
                print(f"✅ Using existing directory: {abs_path}")
            else:
                confirm = input(f"📁 Directory doesn't exist. Create '{abs_path}'? (y/n): ").lower().strip()
                if confirm not in ['y', 'yes']:
                    continue
                try:
                    create_directory_if_not_exists(abs_path)
                    print(f"✅ Created directory: {abs_path}")
                except Exception as e:
                    print(f"❌ Failed to create directory: {str(e)}")
                    continue
            
            return abs_path
            
        elif choice == '2':
            result = browse_directories(os.getcwd(), "Select output directory")
            if result:
                return result
                
        elif choice == '3':
            result = browse_directories(str(Path.home()), "Select output directory")
            if result:
                return result
                
        elif choice == '4':
            return None
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")


def get_template_file() -> Optional[str]:
    """
    Interactive template file selection with validation and browsing support.
    
    Returns:
        Valid template file path, or None if cancelled
    """
    print("Select the template file for document processing.")
    print("💡 Tip: Template should be a Markdown (.md) file with processing instructions.")
    
    while True:
        print(f"\nCurrent directory: {os.getcwd()}")
        choice = input("\nChoose an option:\n"
                      "  1. Enter file path directly\n"
                      "  2. Browse files from current location\n"
                      "  3. Browse files from home\n"
                      "  4. Cancel\n"
                      "Enter choice (1-4): ").strip()
        
        if choice == '1':
            path = input("Enter template file path: ").strip()
            if not path:
                continue
            result = validate_template_file(path)
            if result:
                print(f"✅ Template file validated: {result}")
                return result
                
        elif choice == '2':
            result = browse_files(os.getcwd(), "Select template file", "*.md")
            if result:
                validated = validate_template_file(result)
                if validated:
                    return validated
                    
        elif choice == '3':
            result = browse_files(str(Path.home()), "Select template file", "*.md")
            if result:
                validated = validate_template_file(result)
                if validated:
                    return validated
                    
        elif choice == '4':
            return None
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")


def get_optional_parameters() -> Dict[str, Any]:
    """
    Collect optional parameters with guided input and validation.
    
    Returns:
        Dictionary of optional parameters
    """
    params = {}
    
    print("Configure optional processing parameters.")
    print("💡 Tip: Press Enter to use default values shown in brackets.")
    
    # Quality Standard
    print("\n⭐ Quality Standard:")
    print("  - minimal: Basic processing with minimal quality checks")
    print("  - standard: Balanced processing with standard quality (default)")
    print("  - high: Thorough processing with comprehensive quality checks")
    
    while True:
        quality = input("Quality standard [standard]: ").strip().lower()
        if not quality:
            quality = 'standard'
        if quality in ['minimal', 'standard', 'high']:
            params['quality_standard'] = quality
            break
        print("❌ Invalid quality standard. Choose: minimal, standard, or high")
    
    # Concurrency
    print("\n🔄 Concurrency Settings:")
    print("  Controls how many files are processed simultaneously (1-10)")
    
    while True:
        concurrent = input("Max concurrent files [3]: ").strip()
        if not concurrent:
            params['max_concurrent'] = 3
            break
        try:
            concurrent_int = int(concurrent)
            if 1 <= concurrent_int <= 10:
                params['max_concurrent'] = concurrent_int
                break
            else:
                print("❌ Concurrency must be between 1 and 10")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Custom Prompt
    print("\n💬 Custom Prompt:")
    print("  Add additional instructions for document processing")
    custom_prompt = input("Custom prompt (optional): ").strip()
    if custom_prompt:
        params['custom_prompt'] = custom_prompt
    
    # Skip Processed Files
    print("\n⏭️  Skip Processing:")
    skip_processed = input("Skip already processed files? (y/n) [n]: ").strip().lower()
    if skip_processed in ['y', 'yes']:
        params['skip_processed'] = True
    
    return params


def browse_directories(start_path: str, prompt: str) -> Optional[str]:
    """
    Interactive directory browser with navigation support.
    
    Args:
        start_path: Starting directory for browsing
        prompt: Description of what's being selected
        
    Returns:
        Selected directory path, or None if cancelled
    """
    current_path = os.path.abspath(start_path)
    
    while True:
        print(f"\n📂 {prompt}")
        print(f"Current location: {current_path}")
        print("-" * 50)
        
        try:
            items = []
            # Add parent directory option (except for root)
            if current_path != os.path.dirname(current_path):
                items.append(("📁 ..", os.path.dirname(current_path), "directory"))
            
            # List directories
            for item in sorted(os.listdir(current_path)):
                item_path = os.path.join(current_path, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    items.append((f"📁 {item}", item_path, "directory"))
            
            if not items:
                print("No directories found in this location.")
            else:
                for idx, (display_name, _, _) in enumerate(items, 1):
                    print(f"  {idx:2}. {display_name}")
            
            print(f"\n  s. Select current directory: {current_path}")
            print(f"  c. Cancel")
            
            choice = input(f"\nEnter choice: ").strip().lower()
            
            if choice == 's':
                return current_path
            elif choice == 'c':
                return None
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(items):
                        _, new_path, item_type = items[idx] 
                        if item_type == "directory":
                            current_path = new_path
                        continue
                    else:
                        print("❌ Invalid selection number")
                except ValueError:
                    print("❌ Please enter a number, 's', or 'c'")
                    
        except PermissionError:
            print(f"❌ Permission denied accessing {current_path}")
            current_path = os.path.dirname(current_path)
        except Exception as e:
            print(f"❌ Error browsing directory: {str(e)}")
            return None


def browse_files(start_path: str, prompt: str, pattern: str = "*") -> Optional[str]:
    """
    Interactive file browser with filtering support.
    
    Args:
        start_path: Starting directory for browsing
        prompt: Description of what's being selected
        pattern: File pattern to filter (e.g., "*.md")
        
    Returns:
        Selected file path, or None if cancelled
    """
    import fnmatch
    
    current_path = os.path.abspath(start_path)
    
    while True:
        print(f"\n📄 {prompt}")
        print(f"Current location: {current_path}")
        print(f"File filter: {pattern}")
        print("-" * 50)
        
        try:
            items = []
            # Add parent directory option (except for root)
            if current_path != os.path.dirname(current_path):
                items.append(("📁 ..", os.path.dirname(current_path), "directory"))
            
            # List directories first
            for item in sorted(os.listdir(current_path)):
                item_path = os.path.join(current_path, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    items.append((f"📁 {item}", item_path, "directory"))
            
            # List matching files
            for item in sorted(os.listdir(current_path)):
                item_path = os.path.join(current_path, item)
                if os.path.isfile(item_path) and fnmatch.fnmatch(item, pattern):
                    file_size = get_file_size_mb(item_path)
                    items.append((f"📄 {item} ({file_size:.2f} MB)", item_path, "file"))
            
            if not items:
                print("No directories or matching files found in this location.")
            else:
                for idx, (display_name, _, item_type) in enumerate(items, 1):
                    print(f"  {idx:2}. {display_name}")
            
            print(f"\n  c. Cancel")
            
            choice = input(f"\nEnter choice: ").strip().lower()
            
            if choice == 'c':
                return None
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(items):
                        _, selected_path, item_type = items[idx]
                        if item_type == "directory":
                            current_path = selected_path
                        elif item_type == "file":
                            return selected_path
                        continue
                    else:
                        print("❌ Invalid selection number")
                except ValueError:
                    print("❌ Please enter a number or 'c'")
                    
        except PermissionError:
            print(f"❌ Permission denied accessing {current_path}")
            current_path = os.path.dirname(current_path)
        except Exception as e:
            print(f"❌ Error browsing files: {str(e)}")
            return None


def validate_input_directory(path: str) -> Optional[str]:
    """
    Validate input directory and check for Markdown files.
    
    Args:
        path: Directory path to validate
        
    Returns:
        Validated absolute path, or None if invalid  
    """
    if not path:
        print("❌ Please provide a directory path")
        return None
    
    # Expand user path and make absolute
    expanded_path = os.path.expanduser(path)
    abs_path = os.path.abspath(expanded_path)
    
    if not os.path.exists(abs_path):
        print(f"❌ Directory does not exist: {abs_path}")
        return None
    
    if not os.path.isdir(abs_path):
        print(f"❌ Path is not a directory: {abs_path}")
        return None
    
    # Check for Markdown files
    markdown_files = discover_markdown_files(abs_path)
    if not markdown_files:
        print(f"❌ No Markdown files found in directory: {abs_path}")
        print("💡 Tip: Make sure the directory contains .md files")
        return None
    
    print(f"✅ Found {len(markdown_files)} Markdown files in: {abs_path}")
    return abs_path


def validate_template_file(path: str) -> Optional[str]:
    """
    Validate template file exists and is readable.
    
    Args:
        path: Template file path to validate
        
    Returns:
        Validated absolute path, or None if invalid
    """
    if not path:
        print("❌ Please provide a template file path")
        return None
    
    # Expand user path and make absolute
    expanded_path = os.path.expanduser(path)
    abs_path = os.path.abspath(expanded_path)
    
    if not validate_path(abs_path, must_exist=True, must_be_file=True):
        print(f"❌ Template file does not exist or is not accessible: {abs_path}")
        return None
    
    return abs_path


def create_directory_if_not_exists(path: str) -> bool:
    """
    Create directory if it doesn't exist.
    
    Args:
        path: Directory path to create
        
    Returns:
        True if successful, False otherwise
    """
    return ensure_directory_exists(path)


def get_file_size_mb(path: str) -> float:
    """
    Get file size in megabytes.
    
    Args:
        path: File path to get size for
        
    Returns:
        File size in MB
    """
    try:
        size_bytes = os.path.getsize(path)
        return size_bytes / (1024 * 1024)
    except (OSError, FileNotFoundError):
        return 0.0


if __name__ == "__main__":
    asyncio.run(interactive_main())