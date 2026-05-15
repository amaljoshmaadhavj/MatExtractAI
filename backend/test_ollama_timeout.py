#!/usr/bin/env python3
"""Quick test to verify OLLAMA connectivity and response times."""

import asyncio
import ollama
import time

async def test_ollama():
    """Test OLLAMA with timeout."""
    print("Testing OLLAMA connectivity and response...")
    
    prompt = "What is 2+2? Answer with just the number."
    
    start = time.time()
    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(
                ollama.generate,
                model="llama3.2:1b",
                prompt=prompt,
                stream=False,
                options={"temperature": 0.1}
            ),
            timeout=30.0
        )
        elapsed = time.time() - start
        print(f"✅ OLLAMA responded in {elapsed:.2f}s")
        print(f"Response: {response.get('response', '')}")
        return True
    except asyncio.TimeoutError:
        elapsed = time.time() - start
        print(f"❌ OLLAMA timeout after {elapsed:.2f}s")
        return False
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Error after {elapsed:.2f}s: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ollama())
    exit(0 if success else 1)
