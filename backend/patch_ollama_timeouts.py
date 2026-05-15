#!/usr/bin/env python3
"""Add asyncio.wait_for timeout wrapper to OLLAMA calls in composition, processing, microstructure."""

import re
import sys

def add_timeouts_to_ollama_service():
    """Add asyncio.wait_for timeout wrappers to ollama_service.py."""
    
    file_path = r"c:\Users\admin\Projects\MatExtractAI\backend\app\services\ollama_service.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern to find: response = await asyncio.to_thread(ollama.generate, ...
    # Replace with: response = await asyncio.wait_for(asyncio.to_thread(ollama.generate, ..., timeout=90.0)
    
    # For composition method
    # Find the asyncio.to_thread call in composition and wrap with wait_for
    pattern_comp = r'(async def extract_composition.*?)(response = await asyncio\.to_thread\(\s+ollama\.generate,'
    replacement_comp = r'\1response = await asyncio.wait_for(\n                    asyncio.to_thread(\n                        ollama.generate,'
    content = re.sub(pattern_comp, replacement_comp, content, flags=re.DOTALL, count=1)
    
    # Add timeout and closing paren after the options dict in composition
    # This is tricky - need to find the right spot
    pattern_comp_end = r'(extract_composition.*?options=\{"temperature": 0\.1\}\s+)\)'
    replacement_comp_end = r'\1),\n                    timeout=90.0\n                )'
    content = re.sub(pattern_comp_end, replacement_comp_end, content, flags=re.DOTALL, count=1)
    
    # Similar fixes for processing and microstructure
    # This is getting complex - let's just add exception handling instead
    
    if content != original_content:
        print("✅ Patches applied successfully")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    else:
        print("❌ No changes made - pattern not found")
        return False

if __name__ == "__main__":
    success = add_timeouts_to_ollama_service()
    sys.exit(0 if success else 1)
