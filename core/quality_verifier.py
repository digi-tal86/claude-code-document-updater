"""
Quality verification module for document processing.

This module provides quality verification functionality using the centralized
Claude client to ensure processed documents meet specified quality standards.
"""

import logging
from typing import Optional, Tuple

# Import centralized Claude client
from utils.claude_client import claude_verify_quality

# Configure logging
logger = logging.getLogger(__name__)


async def verify_quality_standards(content: str, quality_standards: str, file_name: str) -> Tuple[bool, Optional[str]]:
    """
    Verify that processed content meets quality standards using Claude.
    
    This function uses the centralized Claude client to analyze the processed document
    and verify it meets quality standards including structure, completeness,
    and formatting requirements.
    
    Args:
        content: The processed markdown content to verify
        quality_standards: The quality standards to check against
        file_name: Name of the file being verified (for logging)
        
    Returns:
        Tuple[bool, Optional[str]]: (success, error_message)
        - success: True if document meets quality standards, False otherwise
        - error_message: Error description if verification fails, None if successful
        
    Raises:
        Exception: Re-raises any unexpected errors during verification
    """
    # Use the centralized Claude client for quality verification
    return await claude_verify_quality(content, quality_standards, file_name)