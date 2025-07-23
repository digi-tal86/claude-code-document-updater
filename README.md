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
- 📁 **Batch Processing**: Process entire directories of markdown files at once
- 📝 **Template-Based**: Use custom templates to guide document transformation
- 🔧 **Customizable**: Support for custom prompts and processing instructions
- 📊 **Robust Logging**: Detailed progress tracking and error reporting
- ⚡ **Async Processing**: Efficient processing using Python's asyncio

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
python process_docs.py <input_directory> <output_directory> <template_file>
```

Example:
```bash
python process_docs.py ./raw_docs ./formatted_docs ./template.md
```

### With Custom Prompt

```bash
python process_docs.py ./input ./output ./template.md --prompt "Transform into technical specification"
```

### Command Line Arguments

- `input_dir`: Directory containing markdown files to process
- `output_dir`: Directory where processed files will be saved
- `template_file`: Template markdown file to guide the transformation
- `--prompt`: (Optional) Custom prompt to control processing behavior

## How It Works

1. **Template Loading**: The script loads your template file which defines the desired document structure
2. **File Discovery**: Scans the input directory for all `.md` files
3. **AI Processing**: Each file is sent to Claude along with the template for transformation
4. **Output Generation**: Transformed documents are saved to the output directory with the same filenames

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
├── process_docs.py      # Main processing script
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

- Files are processed sequentially to avoid API rate limits
- Large files may take longer to process
- Network connectivity is required for Claude API access

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