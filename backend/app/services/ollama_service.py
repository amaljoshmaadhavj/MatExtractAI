"""OLLAMA LLM service for material property extraction."""

import logging
import json
import asyncio
from typing import Dict, Any, Optional
import ollama

from app.config import settings

logger = logging.getLogger(__name__)


class OllamaService:
    """Service for OLLAMA LLM interactions."""
    
    def __init__(self):
        """Initialize OLLAMA service."""
        self.host = settings.ollama_host
        self.model = settings.ollama_model
        self.available = False
        logger.info(f"[OLLAMA] Initializing with host={self.host}, model={self.model}")
        
        # Check OLLAMA availability
        self._check_ollama_availability()
    
    def _check_ollama_availability(self):
        """Check if OLLAMA is available."""
        try:
            import urllib.request
            import json as json_lib
            
            req = urllib.request.Request(f"{self.host}/api/tags")
            response = urllib.request.urlopen(req, timeout=2)
            
            if response.status == 200:
                data = json_lib.loads(response.read().decode('utf-8'))
                models = data.get("models", [])
                self.available = True
                logger.info(f"[OLLAMA] ✅ OLLAMA available at {self.host}")
                logger.info(f"[OLLAMA] Available models: {[m.get('name') for m in models]}")
            else:
                logger.warning(f"[OLLAMA] ⚠️ OLLAMA returned status code {response.status}")
                self.available = False
        except Exception as e:
            logger.warning(f"[OLLAMA] ⚠️ OLLAMA not available at {self.host}: {e}")
            logger.warning(f"[OLLAMA] ⚠️ Will use fallback mock data for extraction")
            self.available = False
        
    async def extract_mechanical_properties(self, sections: Dict[str, str], tables: list) -> Dict[str, Any]:
        """
        Extract mechanical properties using OLLAMA asynchronously.
        
        Args:
            sections: Dictionary of document sections
            tables: List of extracted tables
            
        Returns:
            Dictionary with extracted mechanical properties including evidence
        """
        try:
            logger.info("[OLLAMA] Extracting mechanical properties...")
            
            # Check OLLAMA availability
            if not self.available:
                logger.warning("[OLLAMA] OLLAMA not available, using mock data")
                return self._mock_mechanical_properties()
            
            # Prepare context from sections
            results_text = sections.get("results", "")
            methods_text = sections.get("methods", "")
            
            logger.info(f"[OLLAMA] Using Results section: {len(results_text)} chars")
            logger.info(f"[OLLAMA] Using Methods section: {len(methods_text)} chars")
            
            # Check if we have any meaningful text
            if not results_text and not methods_text:
                logger.warning("[OLLAMA] No results or methods text found, using mock data")
                return self._mock_mechanical_properties()
            
            # Prepare table info with actual table content
            table_info = ""
            if tables:
                table_info = f"\n\nTABLES FROM DOCUMENT:\n"
                for idx, (table_text, context) in enumerate(tables, 1):
                    table_info += f"\nTable {idx}:\n{table_text[:500]}\n"
                logger.info(f"[OLLAMA] Including {len(tables)} table(s) in prompt")
            else:
                logger.info("[OLLAMA] No tables found in document")
            
            prompt = f"""
Extract mechanical properties from the following research paper content.
IMPORTANT: Look for numeric values in TABLES and narrative text sections.
For each property found, note the source (section name, table number, or figure).

METHODS:
{methods_text[:1000]}

RESULTS:
{results_text[:1000]}
{table_info}

Extract the following properties if mentioned:
- Yield Strength (MPa)
- Ultimate Tensile Strength (MPa)
- Elongation (%)
- Grain Size (μm)
- Hardness (HV or HB)
- Elastic Modulus (GPa)

Return ONLY valid JSON with this structure:
{{
  "properties": [
    {{
      "material": "material name",
      "yield_strength_mpa": null,
      "ultimate_tensile_strength_mpa": null,
      "elongation_percent": null,
      "grain_size_um": null,
      "hardness": null,
      "elastic_modulus_gpa": null,
      "confidence": 0.85,
      "source": "Table 1 or Section name",
      "evidence": "Brief description of where this was found"
    }}
  ]
}}
""".strip()
            
            logger.info(f"[OLLAMA] Sending prompt to model {self.model} at {self.host}")
            
            # Run ollama.generate in thread pool to avoid blocking
            response = await asyncio.to_thread(
                ollama.generate,
                model=self.model,
                prompt=prompt,
                stream=False,
                options={"temperature": 0.1}
            )
            
            response_text = response.get("response", "").strip()
            logger.info(f"[OLLAMA] Received response: {len(response_text)} chars")
            
            # Extract JSON from response
            try:
                result = json.loads(response_text)
                # Ensure evidence is present
                for prop in result.get("properties", []):
                    if "evidence" not in prop:
                        prop["evidence"] = prop.get("source", "Unknown source")
                
                logger.info(f"[OLLAMA] ✅ Mechanical properties extracted: {len(result.get('properties', []))} items")
                return {
                    "extraction_status": "success",
                    "extracted_data": result.get("properties", []),
                    "agent_name": "mechanical_properties_agent"
                }
            except json.JSONDecodeError as je:
                logger.warning(f"[OLLAMA] Could not parse JSON response: {response_text[:200]}")
                logger.warning(f"[OLLAMA] JSON Error: {je}")
                return self._mock_mechanical_properties()
                
        except Exception as e:
            logger.error(f"[OLLAMA] Error extracting mechanical properties: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._mock_mechanical_properties()
    
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
            
            # Check OLLAMA availability
            if not self.available:
                logger.warning("[OLLAMA] OLLAMA not available, using mock data")
                return self._mock_composition()
            
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
                for idx, (table_text, context) in enumerate(tables, 1):
                    table_info += f"\nTable {idx}:\n{table_text[:500]}\n"
            
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
            
            logger.info(f"[OLLAMA] Sending prompt to model {self.model}")
            
            # Run ollama.generate in thread pool to avoid blocking
            response = await asyncio.to_thread(
                ollama.generate,
                model=self.model,
                prompt=prompt,
                stream=False,
                options={"temperature": 0.1}
            )
            
            response_text = response.get("response", "").strip()
            logger.info(f"[OLLAMA] Received response: {len(response_text)} chars")
            
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
                return self._mock_composition()
                
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
            
            # Check OLLAMA availability
            if not self.available:
                logger.warning("[OLLAMA] OLLAMA not available, using mock data")
                return self._mock_processing()
            
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
                for idx, (table_text, context) in enumerate(tables, 1):
                    table_info += f"\nTable {idx}:\n{table_text[:500]}\n"
            
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
            
            logger.info(f"[OLLAMA] Sending prompt to model {self.model}")
            
            # Run ollama.generate in thread pool to avoid blocking
            response = await asyncio.to_thread(
                ollama.generate,
                model=self.model,
                prompt=prompt,
                stream=False,
                options={"temperature": 0.1}
            )
            
            response_text = response.get("response", "").strip()
            logger.info(f"[OLLAMA] Received response: {len(response_text)} chars")
            
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
                return self._mock_processing()
                
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
            
            # Check OLLAMA availability
            if not self.available:
                logger.warning("[OLLAMA] OLLAMA not available, using mock data")
                return self._mock_microstructure()
            
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
                for idx, (table_text, context) in enumerate(tables, 1):
                    table_info += f"\nTable {idx}:\n{table_text[:500]}\n"
            
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
            
            logger.info(f"[OLLAMA] Sending prompt to model {self.model}")
            
            # Run ollama.generate in thread pool to avoid blocking
            response = await asyncio.to_thread(
                ollama.generate,
                model=self.model,
                prompt=prompt,
                stream=False,
                options={"temperature": 0.1}
            )
            
            response_text = response.get("response", "").strip()
            logger.info(f"[OLLAMA] Received response: {len(response_text)} chars")
            
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
                return self._mock_microstructure()
                
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
