#!/usr/bin/env python3
"""Test OLLAMA with complex composition prompt."""

import asyncio
import ollama
import time

async def test_composition():
    """Test composition extraction timeout."""
    print("Testing OLLAMA with composition extraction prompt...")
    
    intro_text = """
    The Mg-Al-Zn alloy (AZ31) was provided in the form of rolled sheets with 0.5 mm thickness.
    According to the manufacturer, the nominal composition is: Mg-3.0Al-1.0Zn-0.2Mn (wt%).
    The material was received in an annealed condition with an initial grain size of 15 μm.
    For ZE10 (Mg-1.0Zn-0.1Ce+Y), similar properties were observed.
    """
    
    prompt = f"""
Extract alloy composition from this research paper section.
IMPORTANT: Look for composition data in TABLES and narrative sections.
Note the source section where this information was found.

CONTENT:
{intro_text}

Extract alloy compositions in format like:
- Al-Cu-Mg alloy
- Mg alloy with Zn and Al additions
- Steel with Carbon and Chromium

Return ONLY valid JSON:
{{
  "alloys": [
    {{
      "alloy_name": "AZ31",
      "composition_elements": ["Al", "Zn"],
      "composition_percent": {{"Al": "3%", "Zn": "1%"}},
      "confidence": 0.90,
      "source": "Introduction or Materials section",
      "evidence": "Alloy composition as specified in materials section"
    }}
  ]
}}
""".strip()
    
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
        print(f"Response: {response.get('response', '')[:200]}")
        return True
    except asyncio.TimeoutError:
        elapsed = time.time() - start
        print(f"❌ OLLAMA timeout after {elapsed:.2f}s")
        return False
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Error after {elapsed:.2f}s: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_composition())
    exit(0 if success else 1)
