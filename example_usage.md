# Document Processor - Detailed Usage Guide

## Table of Contents
1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Basic Usage](#basic-usage)
4. [Advanced Usage](#advanced-usage)
5. [Template Creation](#template-creation)
6. [Real-World Examples](#real-world-examples)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Performance Tips](#performance-tips)

## Installation

### Prerequisites
- Python 3.10 or higher
- Node.js (for Claude Code CLI)
- Claude API access

### Step-by-Step Installation

1. **Install Claude Code CLI globally:**
```bash
npm install -g @anthropic-ai/claude-code
```

2. **Clone and setup the project:**
```bash
git clone <repository-url>
cd doc-parser
```

3. **Create virtual environment with uv:**
```bash
uv venv --python 3.10
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

4. **Install dependencies:**
```bash
uv pip install -r requirements.txt
```

## Quick Start

Transform a single directory of markdown files:

```bash
python process_docs.py ./my_notes ./formatted_docs ./template.md
```

## Basic Usage

### Command Structure
```bash
python process_docs.py <input_dir> <output_dir> <template_file> [options]
```

### Parameters
- `input_dir`: Directory containing your `.md` files
- `output_dir`: Where processed files will be saved
- `template_file`: Template that defines output structure
- `--prompt`: (Optional) Custom processing instructions

### Simple Example
```bash
# Process meeting notes into formal documents
python process_docs.py ./meeting_notes ./formal_reports ./report_template.md
```

## Advanced Usage

### Custom Prompts

Use custom prompts for specific transformations:

```bash
# Convert technical notes to user documentation
python process_docs.py ./tech_notes ./user_docs ./doc_template.md \
  --prompt "Convert technical jargon to user-friendly language. Add examples."

# Transform brainstorming into project proposals
python process_docs.py ./ideas ./proposals ./proposal_template.md \
  --prompt "Expand ideas into detailed project proposals with timelines and budgets."
```

### Batch Processing Different Document Types

```bash
# Process different document types with appropriate templates
for type in reports specs guides; do
    python process_docs.py ./raw_$type ./formatted_$type ./${type}_template.md
done
```

## Template Creation

### Basic Template Structure

```markdown
# [Document Type] Title

## Executive Summary
[High-level overview - 2-3 sentences]

## Background
[Context and motivation]

## Main Content

### Section 1: [Topic]
[Detailed content]

### Section 2: [Topic]
[Detailed content]

## Recommendations
1. [Action item 1]
2. [Action item 2]

## Next Steps
- [Immediate action]
- [Future consideration]

## Appendix
[Supporting information]
```

### Specialized Templates

#### Technical Specification Template
```markdown
# Technical Specification: [Component Name]

## Overview
[Purpose and scope]

## Technical Requirements
### Functional Requirements
- [Requirement 1]
- [Requirement 2]

### Non-Functional Requirements
- Performance: [Metrics]
- Security: [Standards]

## Architecture
[System design overview]

## Implementation Details
### Technologies
- [Tech stack]

### Dependencies
- [External dependencies]

## Testing Strategy
[Test approach]

## Deployment
[Deployment process]
```

#### Business Report Template
```markdown
# Business Report: [Title]

## Executive Summary
[Key findings and recommendations]

## Market Analysis
[Current market state]

## Financial Impact
[Cost-benefit analysis]

## Strategic Recommendations
1. [Primary recommendation]
2. [Secondary recommendation]

## Risk Assessment
[Potential risks and mitigation]

## Timeline
[Implementation schedule]
```

## Real-World Examples

### Example 1: Converting Research Notes

**Input** (`research_notes.md`):
```markdown
# AI Research thoughts

Been looking into transformer models. Really interesting stuff with attention mechanisms.

BERT seems good for our use case? Need to test.

GPT might be overkill but worth exploring.

TODO: benchmark different models
```

**Command**:
```bash
python process_docs.py ./research ./papers ./academic_template.md \
  --prompt "Convert informal research notes into academic paper sections"
```

**Output** (`research_notes.md` in output folder):
```markdown
# Comparative Analysis of Transformer Models for Natural Language Processing

## Abstract
This document examines the applicability of various transformer-based models...

## Introduction
Recent advances in transformer architectures have revolutionized...

## Methodology
We evaluate three primary transformer variants:
1. BERT (Bidirectional Encoder Representations from Transformers)
2. GPT (Generative Pre-trained Transformer)
3. [Additional models as needed]

## Proposed Approach
Initial analysis suggests BERT's bidirectional nature aligns well with our requirements...

## Future Work
- Comprehensive benchmarking of model performance
- Comparative analysis of computational requirements
```

### Example 2: Standardizing Documentation

**Input** (`api_notes.md`):
```markdown
# API stuff

POST /users - creates user
GET /users/:id - gets user info
PUT /users/:id - updates user

need to add:
- auth headers
- rate limiting
- error codes
```

**Command**:
```bash
python process_docs.py ./api_drafts ./api_docs ./api_doc_template.md
```

**Output**: Professional API documentation with proper formatting, examples, and error handling.

## Best Practices

### 1. Template Design
- Keep templates focused on structure, not content
- Use clear section headers
- Include placeholder text that guides content

### 2. Input Organization
- Group similar documents in the same directory
- Use descriptive filenames
- Keep files reasonably sized (< 10,000 words)

### 3. Custom Prompts
- Be specific about transformation goals
- Mention target audience
- Specify technical level required

### 4. Output Review
- Always review AI-generated content
- Check for factual accuracy
- Ensure consistency across documents

## Troubleshooting

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Import Error | Missing dependencies | Run `uv pip install -r requirements.txt` |
| Empty Output | API issues | Check Claude Code CLI configuration |
| Partial Processing | Rate limiting | Add delays or reduce batch size |
| Format Issues | Complex templates | Simplify template structure |
| Python Version Error | Wrong Python version | Use `uv venv --python 3.10` |

### Debug Mode

Enable detailed logging:
```python
# In process_docs.py, change:
logging.basicConfig(level=logging.DEBUG)
```

### Checking Logs

```bash
# Run with output redirection for analysis
python process_docs.py input output template.md 2> process.log
```

## Performance Tips

### 1. Optimize File Sizes
- Split very large documents (> 50KB)
- Process in smaller batches for better results

### 2. Template Efficiency
- Simpler templates process faster
- Avoid overly complex hierarchies

### 3. Network Considerations
- Ensure stable internet connection
- Consider retries for network failures

### 4. Parallel Processing
- Current version processes sequentially
- Future versions may support parallel processing

## Directory Structure

```
doc-parser/
├── process_docs.py      # Main script
├── README.md           # Project overview
├── requirements.txt    # Python dependencies
├── example_usage.md    # This file
├── templates/          # Template collection
│   ├── template.md     # Basic template
│   ├── report.md       # Report template
│   ├── technical.md    # Technical doc template
│   └── blog.md         # Blog post template
├── input_docs/         # Your input files
│   ├── notes.md
│   ├── ideas.md
│   └── draft.md
└── output_docs/        # Processed results
    ├── notes.md        # Transformed version
    ├── ideas.md        # Transformed version
    └── draft.md        # Transformed version
```

## Advanced Configuration

### Environment Variables
```bash
# Set custom timeout (in seconds)
export CLAUDE_TIMEOUT=60

# Set custom working directory
export CLAUDE_WORKDIR=/path/to/project
```

### Integration with CI/CD
```yaml
# Example GitHub Action
- name: Process Documentation
  run: |
    python process_docs.py ./docs/raw ./docs/processed ./docs/template.md
```

## Next Steps

1. Explore different template designs for your use case
2. Experiment with custom prompts
3. Build a library of templates for different document types
4. Consider automating the process with scripts or CI/CD

For more information, see the [README.md](README.md) or check the [Claude Code SDK documentation](https://docs.anthropic.com/en/docs/claude-code/sdk).