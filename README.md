# Markdown Document Processor

A Python tool that uses the Claude Code SDK to automatically transform and standardize markdown documents using AI-powered processing.

## Overview

This tool processes markdown files by using Claude AI to transform them according to a provided template. It's perfect for:
- Standardizing documentation formats
- Converting informal notes into professional documents
- Batch processing multiple markdown files
- Maintaining consistent document structure across projects

## Features

- 🤖 **AI-Powered Processing**: Uses Claude AI to intelligently transform documents
- ⚡ **Concurrent Processing**: Process multiple files simultaneously with configurable limits
- 📁 **Batch Processing**: Process entire directories of markdown files at once
- 📝 **Template-Based**: Use custom templates to guide document transformation
- 🔧 **Customizable**: Support for custom prompts and processing instructions
- 📅 **Automatic Dating**: Automatically updates "[Date]" placeholders with current date
- 🔄 **Retry Logic**: Robust error handling with exponential backoff retry
- 📊 **Progress Tracking**: Real-time progress updates and performance metrics
- 📊 **Detailed Reporting**: Comprehensive summaries with processing statistics

## Requirements

- Python 3.10 or higher
- Node.js (for Claude Code CLI)
- Claude Code CLI installed and configured
- Active Claude API access

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd doc-parser
```

2. Create a virtual environment using uv:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
uv pip install -r requirements.txt
```

4. Ensure Claude Code CLI is installed:
```bash
npm install -g @anthropic-ai/claude-code
```

## Usage

### Basic Usage

```bash
python process_docs.py <input_directory> <output_directory> <template_file> [options]
```

### Examples

```bash
# Concurrent processing (default, recommended)
python process_docs.py ./raw_docs ./formatted_docs ./template.md

# Higher concurrency for faster processing
python process_docs.py ./raw_docs ./formatted_docs ./template.md -c 10

# Sequential processing (use -c 1 for conservative approach)
python process_docs.py ./raw_docs ./formatted_docs ./template.md -c 1

# With custom prompt
python process_docs.py ./input ./output ./template.md --prompt "Transform into technical specification"
```

### Command Line Arguments

- `input_dir`: Directory containing markdown files to process
- `output_dir`: Directory where processed files will be saved
- `template_file`: Template markdown file to guide the transformation
- `--prompt`: (Optional) Custom prompt to control processing behavior
- `-c, --concurrency`: (Optional) Number of files to process simultaneously (default: 5, use 1 for sequential)
- `--max-retries`: (Optional) Maximum retry attempts for failed files (default: 3)

## How It Works

1. **Template Loading**: The script loads your template file which defines the desired document structure
2. **File Discovery**: Scans the input directory for all `.md` files
3. **Concurrent Processing**: Files are processed with configurable concurrency (use `-c 1` for sequential processing)
4. **AI Processing**: Each file is sent to Claude along with the template and current date for transformation
5. **Retry Logic**: Failed requests are automatically retried with exponential backoff
6. **Output Generation**: Transformed documents are saved to the output directory with the same filenames
7. **Progress Reporting**: Real-time progress updates and final performance summary

## Example Templates

### Basic Document Template
```markdown
# Document Title

## Executive Summary
[Brief overview]

## Main Content
### Section 1
[Content]

## Conclusion
[Summary]
```

### Technical Report Template
```markdown
# Technical Report

## Abstract
[Technical summary]

## Methodology
[Approach description]

## Results
[Findings]

## References
[Citations]
```

## Directory Structure

```
doc-parser/
├── process_docs.py      # Main processing script (supports both concurrent and sequential)
├── template.md          # Example template
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── example_usage.md    # Detailed usage examples
├── input_docs/         # Your input markdown files
└── output_docs/        # Processed output files
```

## Error Handling

- The script continues processing even if individual files fail
- Failed files retain their original content in the output
- Detailed error messages are logged for troubleshooting
- Non-existent directories are reported before processing begins

## Performance Considerations

### Processing Options
- **Concurrent Processing** (default `-c 5`): Process multiple files simultaneously for significant speed improvements
- **Sequential Processing** (`-c 1`): Process files one at a time for more conservative approach  
- **Custom Concurrency** (`-c N`): Adjust concurrency level based on your needs and API limits
- Automatic retry logic with exponential backoff for failed requests
- Real-time progress tracking shows processing speedup (typically 2-4x faster with concurrency)

### General
- Large files may take longer to process regardless of concurrency setting
- Network connectivity is required for Claude API access
- Processing speed depends on Claude API response times

## Troubleshooting

### Common Issues

1. **Import Error**: claude-code-sdk not found
   - Solution: Run `uv pip install claude-code-sdk`

2. **Python Version Error**: Requires Python 3.10+
   - Solution: Use `uv venv --python 3.10` or higher

3. **No Output Generated**: Check logs for API errors
   - Ensure Claude Code CLI is properly configured
   - Verify API access is active

4. **Empty Output Files**: Template might be too complex
   - Simplify template structure
   - Use more specific prompts

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is provided as-is for educational and professional use.

## Acknowledgments

Built with the [Claude Code SDK](https://docs.anthropic.com/en/docs/claude-code/sdk) by Anthropic.