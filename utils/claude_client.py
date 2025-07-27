"""
Centralized Claude SDK client for document processing.

This module provides a unified interface for all Claude SDK interactions,
including query execution, response parsing, and error handling.
"""

import asyncio
import logging
from typing import Optional, List
from claude_code_sdk import query, ClaudeCodeOptions, Message

logger = logging.getLogger(__name__)


class ClaudeClientError(Exception):
    """Custom exception for Claude client errors."""
    pass


async def claude_query(
    prompt: str,
    operation_name: str = "query",
    system_prompt: Optional[str] = None,
    max_turns: int = 1
) -> str:
    """
    Execute a Claude query and return the parsed response content.
    
    Args:
        prompt: The prompt to send to Claude
        operation_name: Name of the operation for logging purposes
        system_prompt: Optional custom system prompt
        max_turns: Maximum number of conversation turns
        
    Returns:
        str: The extracted content from Claude's response
        
    Raises:
        ClaudeClientError: If the query fails or returns empty content
    """
    if system_prompt is None:
        system_prompt = "You are a markdown document processor. Your response must be ONLY the processed markdown content. Do not use any tools, do not provide explanations, do not ask questions. Output only the formatted markdown document."
    
    options = ClaudeCodeOptions(
        max_turns=max_turns,
        system_prompt=system_prompt
    )
    
    try:
        logger.debug(f"Starting Claude {operation_name} with prompt length: {len(prompt)}")
        
        # Execute Claude query
        messages = []
        async for message in query(prompt=prompt, options=options):
            messages.append(message)
        
        if not messages:
            raise ClaudeClientError(f"No messages received from Claude for {operation_name}")
        
        # Parse response content
        response_content = _extract_content_from_messages(messages)
        
        if not response_content:
            raise ClaudeClientError(f"Received empty response from Claude for {operation_name}")
        
        logger.debug(f"Claude {operation_name} completed successfully, response length: {len(response_content)}")
        return response_content
        
    except Exception as e:
        logger.error(f"Claude {operation_name} failed: {str(e)}")
        if isinstance(e, ClaudeClientError):
            raise
        else:
            raise ClaudeClientError(f"Claude SDK error during {operation_name}: {str(e)}") from e


def _extract_content_from_messages(messages: List[Message]) -> str:
    """
    Extract content from Claude response messages.
    
    This function handles the various response formats that Claude can return,
    including message.result, message.content with text blocks, and string content.
    """
    response_parts = []
    
    # Process messages in reverse order to get the latest response first
    for message in reversed(messages):
        # Check for result attribute first (preferred format)
        if hasattr(message, 'result') and message.result:
            response_parts = [message.result]
            break
        
        # Check for content attribute
        elif hasattr(message, 'content') and message.content:
            if isinstance(message.content, list):
                # Handle list of content blocks
                for block in message.content:
                    if hasattr(block, 'text'):
                        response_parts.append(block.text)
            elif isinstance(message.content, str):
                # Handle string content
                response_parts = [message.content]
            break
    
    return "".join(response_parts)


def create_processing_options(system_prompt: Optional[str] = None, max_turns: int = 1) -> ClaudeCodeOptions:
    """
    Create Claude options for document processing operations.
    
    Args:
        system_prompt: Optional custom system prompt
        max_turns: Maximum number of conversation turns
        
    Returns:
        ClaudeCodeOptions: Configured options for Claude query
    """
    if system_prompt is None:
        system_prompt = "You are a markdown document processor. Your response must be ONLY the processed markdown content. Do not use any tools, do not provide explanations, do not ask questions. Output only the formatted markdown document."
    
    return ClaudeCodeOptions(
        max_turns=max_turns,
        system_prompt=system_prompt
    )


def create_verification_options() -> ClaudeCodeOptions:
    """
    Create Claude options for quality verification operations.
    
    Returns:
        ClaudeCodeOptions: Configured options for quality verification
    """
    return ClaudeCodeOptions(
        max_turns=1,
        system_prompt="You are a quality assurance validator. Your response must be ONLY 'PASS' or 'FAIL: [reason]'. Do not use any tools, do not provide explanations, do not ask questions."
    )


async def claude_verify_quality(content: str, quality_standards: str, file_name: str) -> tuple[bool, Optional[str]]:
    """
    Verify that processed content meets quality standards using Claude.
    
    Args:
        content: The processed markdown content to verify
        quality_standards: The quality standards to check against
        file_name: Name of the file being verified (for logging)
        
    Returns:
        Tuple[bool, Optional[str]]: (success, error_message)
    """
    verification_prompt = f"""Please verify if the following markdown document meets the specified quality standards.

QUALITY STANDARDS:
{quality_standards}

DOCUMENT TO VERIFY:
{content}

Please respond with ONLY one of the following:
- "PASS" if the document meets all quality standards
- "FAIL: [specific reason]" if the document fails to meet any standard

Do not provide explanations or additional text."""

    try:
        verification_result = await claude_query(
            prompt=verification_prompt,
            operation_name="quality_verification",
            system_prompt="You are a quality assurance validator. Your response must be ONLY 'PASS' or 'FAIL: [reason]'. Do not use any tools, do not provide explanations, do not ask questions."
        )
        
        verification_result = verification_result.strip()
        
        if verification_result.upper() == "PASS":
            return True, None
        elif verification_result.upper().startswith("FAIL"):
            reason = verification_result[5:].strip()  # Remove "FAIL:" prefix
            return False, reason if reason else "Quality standards not met"
        else:
            return False, f"Unexpected verification response: {verification_result}"
            
    except Exception as e:
        logger.warning(f"Quality verification failed for {file_name}: {str(e)}")
        return False, f"Verification error: {str(e)}"