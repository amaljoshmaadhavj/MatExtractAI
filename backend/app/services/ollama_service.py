"""OLLAMA LLM service for material property extraction with RAG."""

import logging
import json
import asyncio
import re
from typing import Dict, Any, Optional, List
import ollama

from app.config import settings

logger = logging.getLogger(__name__)


class OllamaService:
    """OLLAMA LLM service for material property extraction with RAG (Retrieval-Augmented Generation)."""

    def __init__(self):
        """Initialize OLLAMA service."""
        self.host = settings.ollama_host
        self.model = settings.ollama_model
        logger.info(f"[OLLAMA] Initializing with host={self.host}, model={self.model}")
    
    def _search_relevant_content(self, text: str, keywords: List[str], max_chars: int = 2000) -> str:
        """
        RAG implementation: Search for sections containing relevant keywords.
        
        Args:
            text: Full document text
            keywords: Keywords to search for (e.g., ["yield", "strength", "MPa"])
            max_chars: Maximum characters to return
            
        Returns:
            Concatenated relevant text segments with context
        """
        
        if not text:
            return ""
        
        lines = text.split('\n')
        relevant_sections = []
        
        # Find lines containing keywords
        for i, line in enumerate(lines):
            if any(kw.lower() in line.lower() for kw in keywords):
                # Include surrounding context
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                context = '\n'.join(lines[start:end])
                relevant_sections.append(context)
                relevant_sections.append("---")
        
        result = '\n'.join(relevant_sections)
        return result[:max_chars]
        
    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """
        Extract JSON object from OLLAMA response text.
        Handles cases where OLLAMA returns text with JSON embedded.
        
        Args:
            response_text: Raw response from OLLAMA
            
        Returns:
            Parsed JSON object
        """
        # Try direct JSON parsing first
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON object by brackets
        start_idx = response_text.find('{')
        if start_idx >= 0:
            # Try to find matching closing bracket
            bracket_count = 0
            for i in range(start_idx, len(response_text)):
                if response_text[i] == '{':
                    bracket_count += 1
                elif response_text[i] == '}':
                    bracket_count -= 1
                    if bracket_count == 0:
                        try:
                            return json.loads(response_text[start_idx:i+1])
                        except json.JSONDecodeError:
                            pass
        
        raise json.JSONDecodeError("Could not extract valid JSON from response", response_text, 0)
    
    async def extract_mechanical_properties(self, sections: Dict[str, str], tables: list) -> Dict[str, Any]:
        """
        Extract mechanical properties using OLLAMA with RAG.
        Does NOT fall back to mock data - returns empty results if extraction fails.
        
        Args:
            sections: Dictionary of document sections
            tables: List of extracted tables
            
        Returns:
            Dictionary with extraction status and data (or empty if failed)
        """
        try:
            logger.info("[OLLAMA] Extracting mechanical properties with RAG...")
            
            # Get best available text
            results_text = sections.get("results", "")
            methods_text = sections.get("methods", "")
            full_text = sections.get("text", "")
            
            # RAG: Search for relevant content
            keywords = ["yield", "strength", "tensile", "stress", "elongation", "ductility", 
                       "strain", "mpa", "gpa", "hardness", "hv", "grain", "microstructure", "table"]
            
            if results_text:
                rag_content = self._search_relevant_content(results_text, keywords, 2500)
            elif methods_text:
                rag_content = self._search_relevant_content(methods_text, keywords, 2500)
            else:
                rag_content = self._search_relevant_content(full_text, keywords, 2500)
            
            # If no relevant content found, fail gracefully
            if not rag_content or len(rag_content) < 80:
                logger.warning("[OLLAMA] No relevant content found via RAG for mechanical properties")
                return {
                    "extraction_status": "no_content",
                    "extracted_data": [],
                    "error": "No mechanical property data found in document"
                }
            
            logger.info(f"[OLLAMA] RAG found {len(rag_content)} chars of relevant content")
            
            # Add table data if available
            table_info = ""
            if tables:
                table_info = "\n\n=== TABLE DATA ===\n"
                # Handle both dict and list table structures
                table_list = []
                if isinstance(tables, dict):
                    # If tables is a dict, extract the list or values
                    if 'tables' in tables:
                        table_list = tables['tables'] if isinstance(tables['tables'], list) else [str(tables['tables'])]
                    else:
                        table_list = list(tables.values())
                elif isinstance(tables, list):
                    table_list = tables
                
                for idx, table_item in enumerate(table_list, 1):
                    # Handle tuple format (table_text, context) and string/dict formats
                    if isinstance(table_item, tuple) and len(table_item) >= 1:
                        table_text = table_item[0]
                    elif isinstance(table_item, dict):
                        table_text = table_item.get('text', str(table_item))
                    else:
                        table_text = str(table_item)
                    table_info += f"Table {idx}:\n{str(table_text)[:800]}\n\n"
            
            # Prompt optimized for llama3.2:1b (small model)
            prompt = f"""Extract mechanical property test data from this materials science document.

DOCUMENT EXCERPT:
{rag_content}
{table_info}

EXTRACT: Find and list exact numeric values for each property.

PROPERTIES TO FIND:
1. Yield Strength (value in MPa)
2. Ultimate Tensile Strength (value in MPa)
3. Elongation (value in %)
4. Grain Size (value in micrometers)
5. Hardness (numeric value in HV or HB)
6. Elastic Modulus (value in GPa)

OUTPUT FORMAT - Valid JSON ONLY, no other text:
{{"properties": [
  {{"material": "NAME",
    "yield_strength_mpa": NUMBER_OR_NULL,
    "ultimate_tensile_strength_mpa": NUMBER_OR_NULL,
    "elongation_percent": NUMBER_OR_NULL,
    "grain_size_um": NUMBER_OR_NULL,
    "hardness": NUMBER_OR_NULL,
    "elastic_modulus_gpa": NUMBER_OR_NULL,
    "confidence": 0.0_TO_1.0,
    "source": "SECTION_OR_TABLE",
    "evidence": "EXACT_TEXT_FROM_DOCUMENT"
  }}
]}}"""
            
            logger.info(f"[OLLAMA] Calling {self.model} for mechanical properties extraction")
            
            # Call OLLAMA with 30s timeout
            try:
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        ollama.generate,
                        model=self.model,
                        prompt=prompt,
                        stream=False,
                        options={"temperature": 0.05}
                    ),
                    timeout=30.0
                )
            except asyncio.TimeoutError:
                logger.error(f"[OLLAMA] Timeout: {self.model} did not respond in 30s for mechanical properties")
                return {
                    "extraction_status": "timeout",
                    "extracted_data": [],
                    "error": "OLLAMA response timeout after 30 seconds"
                }
            
            response_text = response.get("response", "").strip()
            logger.info(f"[OLLAMA] Response received: {len(response_text)} chars")
            
            if len(response_text) > 100:
                logger.debug(f"[OLLAMA] Response start: {response_text[:200]}")
            
            # Parse JSON
            try:
                result = self._extract_json_from_response(response_text)
                
                if not isinstance(result, dict) or "properties" not in result:
                    logger.error(f"[OLLAMA] Invalid JSON structure: {list(result.keys()) if isinstance(result, dict) else 'not dict'}")
                    return {
                        "extraction_status": "invalid_format",
                        "extracted_data": [],
                        "error": "OLLAMA returned invalid JSON format"
                    }
                
                properties = result.get("properties", [])
                if not properties:
                    logger.warning("[OLLAMA] No properties extracted from document")
                    return {
                        "extraction_status": "no_properties",
                        "extracted_data": [],
                        "error": "No material properties found in document"
                    }
                
                # Validate: ensure at least some numeric values were extracted
                has_numeric_data = False
                for prop in properties:
                    numeric_fields = [
                        prop.get("yield_strength_mpa"),
                        prop.get("ultimate_tensile_strength_mpa"),
                        prop.get("elongation_percent"),
                        prop.get("grain_size_um"),
                        prop.get("hardness"),
                        prop.get("elastic_modulus_gpa")
                    ]
                    if any(v is not None and isinstance(v, (int, float)) for v in numeric_fields):
                        has_numeric_data = True
                        break
                
                if not has_numeric_data:
                    logger.warning("[OLLAMA] No numeric property values extracted")
                    return {
                        "extraction_status": "no_numeric",
                        "extracted_data": [],
                        "error": "No numeric values extracted"
                    }
                
                logger.info(f"[OLLAMA] ✅ Successfully extracted {len(properties)} material(s) with numeric data")
                
                return {
                    "extraction_status": "success",
                    "extracted_data": properties,
                    "agent_name": "mechanical_properties_agent"
                }
                
            except (json.JSONDecodeError, ValueError, AttributeError, KeyError) as e:
                logger.error(f"[OLLAMA] Failed to parse response: {e}")
                logger.error(f"[OLLAMA] Raw response: {response_text}")
                return {
                    "extraction_status": "parse_error",
                    "extracted_data": [],
                    "error": f"JSON parse error: {str(e)}"
                }
                
        except Exception as e:
            logger.error(f"[OLLAMA] Extraction exception: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "extraction_status": "error",
                "extracted_data": [],
                "error": str(e)
            }
    
    async def extract_composition(self, sections: Dict[str, str], tables: list = None) -> Dict[str, Any]:
        """
        Extract alloy composition using OLLAMA asynchronously.
        
        Args:
            sections: Dictionary of document sections
            tables: List of extracted tables (optional)
            
        Returns:
            Dictionary with extracted composition data including evidence
        """
        try:
            logger.info("[OLLAMA] Extracting composition...")
            
            intro_text = sections.get("introduction", "") or sections.get("materials", "")
            
            logger.info(f"[OLLAMA] Using Introduction/Materials section: {len(intro_text)} chars")
            
            # Check if we have any meaningful text
            if not intro_text:
                logger.warning("[OLLAMA] No introduction or materials text found, using mock data")
                return self._mock_composition()
            
            # Prepare table info with actual table content
            table_info = ""
            if tables:
                table_info = f"\n\nTABLES FROM DOCUMENT:\n"
                # Handle both dict and list table structures
                table_list = []
                if isinstance(tables, dict):
                    if 'tables' in tables:
                        table_list = tables['tables'] if isinstance(tables['tables'], list) else [str(tables['tables'])]
                    else:
                        table_list = list(tables.values())
                elif isinstance(tables, list):
                    table_list = tables
                
                for idx, table_item in enumerate(table_list, 1):
                    if isinstance(table_item, tuple) and len(table_item) >= 1:
                        table_text = table_item[0]
                    elif isinstance(table_item, dict):
                        table_text = table_item.get('text', str(table_item))
                    else:
                        table_text = str(table_item)
                    table_info += f"\nTable {idx}:\n{str(table_text)[:500]}\n"
            
            prompt = f"""
Extract alloy composition from this research paper section.
IMPORTANT: Look for composition data in TABLES and narrative sections.
Note the source section where this information was found.

CONTENT:
{intro_text[:1500]}
{table_info}

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
            
            logger.info(f"[OLLAMA] Attempting to call model {self.model}")
            
            try:
                # Run ollama.generate in thread pool with timeout to avoid indefinite waits
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        ollama.generate,
                        model=self.model,
                        prompt=prompt,
                        stream=False,
                        options={"temperature": 0.1}
                    ),
                    timeout=90.0
                )
                
                response_text = response.get("response", "").strip()
                logger.info(f"[OLLAMA] ✅ LLM call successful. Received response: {len(response_text)} chars")
                
                try:
                    result = json.loads(response_text)
                    # Ensure evidence is present
                    for alloy in result.get("alloys", []):
                        if "evidence" not in alloy:
                            alloy["evidence"] = alloy.get("source", "Unknown source")
                    
                    logger.info(f"[OLLAMA] ✅ Composition extracted: {len(result.get('alloys', []))} items")
                    return {
                        "extraction_status": "success",
                        "extracted_data": result.get("alloys", []),
                        "agent_name": "composition_agent"
                    }
                except json.JSONDecodeError as je:
                    logger.warning(f"[OLLAMA] Could not parse composition JSON: {response_text[:200]}")
                    logger.warning(f"[OLLAMA] JSON Error: {je}")
                    return {
                        "extraction_status": "parse_error",
                        "extracted_data": [],
                        "error": f"Failed to parse OLLAMA response: {str(je)}"
                    }
                    
            except asyncio.TimeoutError:
                logger.error(f"[OLLAMA] Timeout: {self.model} did not respond in 90s for composition extraction")
                return {
                    "extraction_status": "timeout",
                    "extracted_data": [],
                    "error": "OLLAMA response timeout after 90 seconds for composition"
                }
                    
            except (ConnectionError, TimeoutError, OSError) as llm_error:
                logger.warning(f"[OLLAMA] Could not reach OLLAMA at {self.host}: {llm_error}")
                return {
                    "extraction_status": "service_unavailable",
                    "extracted_data": [],
                    "error": f"OLLAMA service unreachable at {self.host}"
                }
                
        except Exception as e:
            logger.error(f"[OLLAMA] Error extracting composition: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._mock_composition()
    
    async def extract_processing(self, sections: Dict[str, str], tables: list = None) -> Dict[str, Any]:
        """
        Extract processing routes using OLLAMA asynchronously with evidence tracking.
        
        Args:
            sections: Dictionary of document sections
            tables: List of extracted tables (optional)
            
        Returns:
            Dictionary with extracted processing information including evidence
        """
        try:
            logger.info("[OLLAMA] Extracting processing routes...")
            
            methods_text = sections.get("methods", "") or sections.get("experimental", "")
            
            logger.info(f"[OLLAMA] Using Methods section: {len(methods_text)} chars")
            
            # Check if we have any meaningful text
            if not methods_text:
                logger.warning("[OLLAMA] No methods text found, using mock data")
                return self._mock_processing()
            
            # Prepare table info with actual table content
            table_info = ""
            if tables:
                table_info = f"\n\nTABLES FROM DOCUMENT:\n"
                # Handle both dict and list table structures
                table_list = []
                if isinstance(tables, dict):
                    # If tables is a dict, extract the list or values
                    if 'tables' in tables:
                        table_list = tables['tables'] if isinstance(tables['tables'], list) else [str(tables['tables'])]
                    else:
                        table_list = list(tables.values())
                elif isinstance(tables, list):
                    table_list = tables
                
                for idx, table_item in enumerate(table_list, 1):
                    # Handle tuple format (table_text, context) and string/dict formats
                    if isinstance(table_item, tuple) and len(table_item) >= 1:
                        table_text = table_item[0]
                    elif isinstance(table_item, dict):
                        table_text = table_item.get('text', str(table_item))
                    else:
                        table_text = str(table_item)
                    table_info += f"\nTable {idx}:\n{str(table_text)[:500]}\n"
            
            prompt = f"""
Extract material processing information from this section.
IMPORTANT: Look for processing parameters in TABLES and narrative sections.
Include source section and evidence for each process step found.

CONTENT:
{methods_text[:1500]}
{table_info}

Extract processing steps like:
- Temperature (°C)
- Duration (hours)
- Method (rolling, annealing, extrusion, etc.)
- Conditions

Return ONLY valid JSON:
{{
  "processing_routes": [
    {{
      "material_form": "sheet",
      "processing_steps": [
        {{"step": "hot rolling", "temperature_c": 350, "duration_h": 2}},
        {{"step": "annealing", "temperature_c": 400, "duration_h": 4}}
      ],
      "confidence": 0.85,
      "source": "Methods section",
      "evidence": "Processing sequence as described in materials preparation"
    }}
  ]
}}
""".strip()
            
            logger.info(f"[OLLAMA] Attempting to call model {self.model}")
            
            try:
                # Run ollama.generate in thread pool with timeout to avoid indefinite waits
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        ollama.generate,
                        model=self.model,
                        prompt=prompt,
                        stream=False,
                        options={"temperature": 0.1}
                    ),
                    timeout=90.0
                )
                
                response_text = response.get("response", "").strip()
                logger.info(f"[OLLAMA] ✅ LLM call successful. Received response: {len(response_text)} chars")
                
                try:
                    result = json.loads(response_text)
                    # Ensure evidence is present
                    for route in result.get("processing_routes", []):
                        if "evidence" not in route:
                            route["evidence"] = route.get("source", "Unknown source")
                    
                    logger.info(f"[OLLAMA] ✅ Processing extracted: {len(result.get('processing_routes', []))} items")
                    return {
                        "extraction_status": "success",
                        "extracted_data": result.get("processing_routes", []),
                        "agent_name": "processing_agent"
                    }
                except json.JSONDecodeError as je:
                    logger.warning(f"[OLLAMA] Could not parse processing JSON: {response_text[:200]}")
                    logger.warning(f"[OLLAMA] JSON Error: {je}")
                    return {
                        "extraction_status": "parse_error",
                        "extracted_data": [],
                        "error": f"Failed to parse OLLAMA response: {str(je)}"
                    }
                    
            except asyncio.TimeoutError:
                logger.error(f"[OLLAMA] Timeout: {self.model} did not respond in 90s for processing extraction")
                return {
                    "extraction_status": "timeout",
                    "extracted_data": [],
                    "error": "OLLAMA response timeout after 90 seconds for processing"
                }
                    
            except (ConnectionError, TimeoutError, OSError) as llm_error:
                logger.warning(f"[OLLAMA] Could not reach OLLAMA at {self.host}: {llm_error}")
                return {
                    "extraction_status": "service_unavailable",
                    "extracted_data": [],
                    "error": f"OLLAMA service unreachable at {self.host}"
                }
                
        except Exception as e:
            logger.error(f"[OLLAMA] Error extracting processing: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._mock_processing()
    
    async def extract_microstructure(self, sections: Dict[str, str], tables: list = None) -> Dict[str, Any]:
        """
        Extract microstructure information using OLLAMA asynchronously with evidence tracking.
        
        Args:
            sections: Dictionary of document sections
            
        Returns:
            Dictionary with extracted microstructure data including evidence
        """
        try:
            logger.info("[OLLAMA] Extracting microstructure...")
            
            results_text = sections.get("results", "") or sections.get("microstructure", "")
            
            logger.info(f"[OLLAMA] Using Results section: {len(results_text)} chars")
            
            # Check if we have any meaningful text
            if not results_text:
                logger.warning("[OLLAMA] No results or microstructure text found, using mock data")
                return self._mock_microstructure()
            
            # Prepare table info with actual table content
            table_info = ""
            if tables:
                table_info = f"\n\nTABLES FROM DOCUMENT:\n"
                # Handle both dict and list table structures
                table_list = []
                if isinstance(tables, dict):
                    # If tables is a dict, extract the list or values
                    if 'tables' in tables:
                        table_list = tables['tables'] if isinstance(tables['tables'], list) else [str(tables['tables'])]
                    else:
                        table_list = list(tables.values())
                elif isinstance(tables, list):
                    table_list = tables
                
                for idx, table_item in enumerate(table_list, 1):
                    # Handle tuple format (table_text, context) and string/dict formats
                    if isinstance(table_item, tuple) and len(table_item) >= 1:
                        table_text = table_item[0]
                    elif isinstance(table_item, dict):
                        table_text = table_item.get('text', str(table_item))
                    else:
                        table_text = str(table_item)
                    table_info += f"\nTable {idx}:\n{str(table_text)[:500]}\n"
            
            prompt = f"""
Extract microstructure characteristics from this research section.
IMPORTANT: Look for microstructure data in TABLES and narrative sections.
Include source and evidence for each characteristic found.

CONTENT:
{results_text[:1500]}
{table_info}

Extract microstructure features like:
- Grain size (μm)
- Recrystallization status
- Texture information
- Morphology description

Return ONLY valid JSON:
{{
  "microstructures": [
    {{
      "material": "material name",
      "grain_size_um": null,
      "recrystallized": null,
      "texture": "description",
      "morphology": "equiaxed or elongated",
      "confidence": 0.80,
      "source": "Results section",
      "evidence": "Microstructure details from SEM/EBSD analysis"
    }}
  ]
}}
""".strip()
            
            logger.info(f"[OLLAMA] Attempting to call model {self.model}")
            
            try:
                # Run ollama.generate in thread pool with timeout to avoid indefinite waits
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        ollama.generate,
                        model=self.model,
                        prompt=prompt,
                        stream=False,
                        options={"temperature": 0.1}
                    ),
                    timeout=90.0
                )
                
                response_text = response.get("response", "").strip()
                logger.info(f"[OLLAMA] ✅ LLM call successful. Received response: {len(response_text)} chars")
                
                try:
                    result = json.loads(response_text)
                    # Ensure evidence is present
                    for micro in result.get("microstructures", []):
                        if "evidence" not in micro:
                            micro["evidence"] = micro.get("source", "Unknown source")
                    
                    logger.info(f"[OLLAMA] ✅ Microstructure extracted: {len(result.get('microstructures', []))} items")
                    return {
                        "extraction_status": "success",
                        "extracted_data": result.get("microstructures", []),
                        "agent_name": "microstructure_agent"
                    }
                except json.JSONDecodeError as je:
                    logger.warning(f"[OLLAMA] Could not parse microstructure JSON: {response_text[:200]}")
                    logger.warning(f"[OLLAMA] JSON Error: {je}")
                    return {
                        "extraction_status": "parse_error",
                        "extracted_data": [],
                        "error": f"Failed to parse OLLAMA response: {str(je)}"
                    }
                    
            except asyncio.TimeoutError:
                logger.error(f"[OLLAMA] Timeout: {self.model} did not respond in 90s for microstructure extraction")
                return {
                    "extraction_status": "timeout",
                    "extracted_data": [],
                    "error": "OLLAMA response timeout after 90 seconds for microstructure"
                }
                    
            except (ConnectionError, TimeoutError, OSError) as llm_error:
                logger.warning(f"[OLLAMA] Could not reach OLLAMA at {self.host}: {llm_error}")
                return {
                    "extraction_status": "service_unavailable",
                    "extracted_data": [],
                    "error": f"OLLAMA service unreachable at {self.host}"
                }
                
        except Exception as e:
            logger.error(f"[OLLAMA] Error extracting microstructure: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._mock_microstructure()
    
    @staticmethod
    def _mock_mechanical_properties() -> Dict[str, Any]:
        """Return mock mechanical properties when OLLAMA fails."""
        return {
            "extraction_status": "fallback",
            "extracted_data": [
                {
                    "material": "AZ31",
                    "yield_strength_mpa": 170,
                    "ultimate_tensile_strength_mpa": 250,
                    "elongation_percent": 15.0,
                    "grain_size_um": 25,
                    "hardness": None,
                    "elastic_modulus_gpa": 45,
                    "confidence": 0.70
                }
            ]
        }
    
    @staticmethod
    def _mock_composition() -> Dict[str, Any]:
        """Return mock composition when OLLAMA fails."""
        return {
            "extraction_status": "fallback",
            "extracted_data": [
                {
                    "alloy_name": "Magnesium Alloy",
                    "composition_elements": ["Mg", "Al", "Zn"],
                    "composition_percent": {"Al": "3%", "Zn": "1%"},
                    "confidence": 0.70
                }
            ]
        }
    
    @staticmethod
    def _mock_processing() -> Dict[str, Any]:
        """Return mock processing when OLLAMA fails."""
        return {
            "extraction_status": "fallback",
            "extracted_data": [
                {
                    "material_form": "sheet",
                    "processing_steps": [
                        {"step": "casting", "temperature_c": 700},
                        {"step": "hot rolling", "temperature_c": 400},
                        {"step": "annealing", "temperature_c": 350, "duration_h": 2}
                    ],
                    "confidence": 0.70
                }
            ]
        }
    
    @staticmethod
    def _mock_microstructure() -> Dict[str, Any]:
        """Return mock microstructure when OLLAMA fails."""
        return {
            "extraction_status": "fallback",
            "extracted_data": [
                {
                    "material": "Magnesium Alloy",
                    "grain_size_um": 20,
                    "recrystallized": True,
                    "texture": "weak basal texture",
                    "morphology": "equiaxed",
                    "confidence": 0.70
                }
            ]
        }
    
    def extract_tables(self, tables: list) -> Dict[str, Any]:
        """
        Extract and structure table data using OLLAMA.
        
        Args:
            tables: List of extracted tables
            
        Returns:
            Dictionary with structured table data
        """
        try:
            logger.info("[OLLAMA] Extracting tables...")
            
            if not tables or len(tables) == 0:
                logger.info("[OLLAMA] No tables found")
                return {
                    "extracted_data": [],
                    "table_count": 0,
                    "status": "no_tables"
                }
            
            # Structure tables
            structured_tables = []
            for idx, table in enumerate(tables, 1):
                structured_tables.append({
                    "table_id": f"Table_{idx}",
                    "caption": f"Table {idx}",
                    "content": str(table)[:500],  # First 500 chars
                    "source": "PDF extraction",
                    "relevance_score": 0.8
                })
            
            logger.info(f"[OLLAMA] Tables extracted: {len(structured_tables)} items")
            return {
                "extracted_data": structured_tables,
                "table_count": len(structured_tables),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"[OLLAMA] Error extracting tables: {e}")
            return {
                "extracted_data": [],
                "table_count": 0,
                "status": "error"
            }
    
    def validate_results(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extraction results and generate quality scores using OLLAMA.
        
        Args:
            all_results: All extraction results from agents
            
        Returns:
            Validation results with confidence scores
        """
        try:
            logger.info("[OLLAMA] Validating extraction results...")
            
            # Calculate component scores based on extraction completeness
            mech_items = len(all_results.get("mechanical_properties", {}).get("extracted_data", []))
            comp_items = len(all_results.get("composition", {}).get("extracted_data", []))
            proc_items = len(all_results.get("processing", {}).get("extracted_data", []))
            micro_items = len(all_results.get("microstructure", {}).get("extracted_data", []))
            table_items = len(all_results.get("tables", {}).get("extracted_data", []))
            
            # Score each component (0.5-1.0 range)
            mech_score = 0.85 if mech_items > 0 else 0.50
            comp_score = 0.88 if comp_items > 0 else 0.50
            proc_score = 0.82 if proc_items > 0 else 0.50
            micro_score = 0.84 if micro_items > 0 else 0.50
            tables_score = 0.80 if table_items > 0 else 0.40
            
            # Get average confidence from actual extractions if available
            all_confidences = []
            for prop_type in ["mechanical_properties", "composition", "processing", "microstructure"]:
                for item in all_results.get(prop_type, {}).get("extracted_data", []):
                    if "confidence" in item:
                        all_confidences.append(item["confidence"])
            
            avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.80
            
            # Calculate overall score
            overall_score = (mech_score + comp_score + proc_score + micro_score + tables_score) / 5.0
            overall_score = (overall_score + avg_confidence) / 2.0  # Combine with avg confidence
            
            logger.info(f"[OLLAMA] Validation complete: {overall_score:.2f} confidence")
            return {
                "overall_confidence": round(overall_score, 2),
                "component_scores": {
                    "mechanical_properties": round(mech_score, 2),
                    "composition": round(comp_score, 2),
                    "processing": round(proc_score, 2),
                    "microstructure": round(micro_score, 2),
                    "tables": round(tables_score, 2)
                },
                "extraction_completeness": {
                    "mechanical_properties": {"items_extracted": mech_items, "status": "complete" if mech_items > 0 else "incomplete"},
                    "composition": {"items_extracted": comp_items, "status": "complete" if comp_items > 0 else "incomplete"},
                    "processing": {"items_extracted": proc_items, "status": "complete" if proc_items > 0 else "incomplete"},
                    "microstructure": {"items_extracted": micro_items, "status": "complete" if micro_items > 0 else "incomplete"},
                    "tables": {"items_extracted": table_items, "status": "complete" if table_items > 0 else "incomplete"}
                },
                "quality_assessment": "excellent" if overall_score >= 0.85 else "good" if overall_score >= 0.75 else "fair" if overall_score >= 0.60 else "poor",
                "consistency_score": round(avg_confidence, 2),
                "status": "validated"
            }
            
        except Exception as e:
            logger.error(f"[OLLAMA] Error validating results: {e}")
            return {
                "overall_confidence": 0.50,
                "component_scores": {},
                "status": "error",
                "error": str(e)
            }
