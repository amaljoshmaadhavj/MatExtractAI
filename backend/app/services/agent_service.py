"""Agent orchestration service for LLM-based property extraction."""

import logging
from typing import Dict, Any, Optional

from .ollama_service import OllamaService
from .validation_service import ValidationService

logger = logging.getLogger(__name__)


class AgentService:
    """Orchestrates LLM agents to extract material properties."""
    
    def __init__(self, ollama_service: Optional[OllamaService] = None):
        """Initialize agent service."""
        self.ollama_service = ollama_service or OllamaService()
        self.validation_service = ValidationService()
        logger.info("[AGENT] Agent service initialized")
    
    async def run_all_agents(self, extraction_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all extraction agents on the provided text.
        
        Returns agent results from OLLAMA or mock data.
        """
        # Build sections dict from extraction results
        sections = {
            "title": extraction_results.get("title", ""),
            "abstract": extraction_results.get("abstract", ""),
            "introduction": extraction_results.get("introduction", ""),
            "methods": extraction_results.get("methods", ""),
            "results": extraction_results.get("results", ""),
            "discussion": extraction_results.get("discussion", ""),
            "conclusion": extraction_results.get("conclusion", ""),
            "composition": extraction_results.get("composition", ""),
            "processing": extraction_results.get("processing", ""),
            "microstructure": extraction_results.get("microstructure", ""),
            "text": extraction_results.get("text", "")
        }
        tables = extraction_results.get("tables", {})
        
        logger.info("[AGENT] Starting all agents")
        all_results = {
            "mechanical_properties": await self._run_mechanical_properties(sections, tables),
            "composition": await self._run_composition(sections, tables),
            "processing": await self._run_processing(sections, tables),
            "microstructure": await self._run_microstructure(sections, tables),
            "tables": extraction_results.get("tables", {"tables": []})
        }
        
        logger.info("[AGENT] All agents completed")
        return all_results
    
    async def _run_mechanical_properties(self, sections: Dict[str, str], tables: Dict[str, Any]) -> Dict[str, Any]:
        """Extract mechanical properties using OLLAMA agent."""
        try:
            result = await self.ollama_service.extract_mechanical_properties(sections, tables)
            
            # Check if extraction failed
            if result.get("extraction_status") != "success":
                logger.warning(f"[AGENT] Mechanical properties extraction failed: {result.get('error')}")
                logger.warning(f"[AGENT] Extraction status: {result.get('extraction_status')}")
                # Return the actual error status instead of mock data
                return result
            
            return result
        except Exception as e:
            logger.error(f"[AGENT] Error in mechanical properties agent: {e}")
            return {
                "extraction_status": "error",
                "extracted_data": [],
                "error": str(e)
            }
    
    async def _run_composition(self, sections: Dict[str, str], tables: Dict[str, Any]) -> Dict[str, Any]:
        """Extract composition using OLLAMA agent."""
        try:
            result = await self.ollama_service.extract_composition(sections, tables)
            if result.get("extraction_status") != "success":
                logger.warning(f"[AGENT] Composition extraction failed: {result.get('error')}")
            return result
        except Exception as e:
            logger.error(f"[AGENT] Error in composition agent: {e}")
            return {
                "extraction_status": "error",
                "extracted_data": [],
                "error": str(e)
            }
    
    async def _run_processing(self, sections: Dict[str, str], tables: Dict[str, Any]) -> Dict[str, Any]:
        """Extract processing parameters using OLLAMA agent."""
        try:
            result = await self.ollama_service.extract_processing(sections, tables)
            if result.get("extraction_status") != "success":
                logger.warning(f"[AGENT] Processing extraction failed: {result.get('error')}")
            return result
        except Exception as e:
            logger.error(f"[AGENT] Error in processing agent: {e}")
            return {
                "extraction_status": "error",
                "extracted_data": [],
                "error": str(e)
            }
    
    async def _run_microstructure(self, sections: Dict[str, str], tables: Dict[str, Any]) -> Dict[str, Any]:
        """Extract microstructure using OLLAMA agent."""
        try:
            result = await self.ollama_service.extract_microstructure(sections, tables)
            if result.get("extraction_status") != "success":
                logger.warning(f"[AGENT] Microstructure extraction failed: {result.get('error')}")
            return result
        except Exception as e:
            logger.error(f"[AGENT] Error in microstructure agent: {e}")
            return {
                "extraction_status": "error",
                "extracted_data": [],
                "error": str(e)
            }
    
    @staticmethod
    def _mock_mechanical_properties() -> Dict[str, Any]:
        """Return mock mechanical properties with evidence tracking."""
        return {
            "extracted_data": [
                {
                    "property": "Yield Strength",
                    "value": 170,
                    "unit": "MPa",
                    "alloy": "AZ31",
                    "confidence": 0.85,
                    "source": "Table 1",
                    "evidence": "Tensile properties extracted from Table 1 in Results section",
                    "page_reference": "Page 2-3",
                    "extraction_method": "LLM agent with mock data"
                },
                {
                    "property": "Ultimate Tensile Strength",
                    "value": 240,
                    "unit": "MPa",
                    "alloy": "AZ31",
                    "confidence": 0.88,
                    "source": "Table 1",
                    "evidence": "UTS from mechanical testing reported in Table 1",
                    "page_reference": "Page 2-3",
                    "extraction_method": "LLM agent with mock data"
                }
            ],
            "agent_name": "mechanical_properties_agent",
            "extraction_status": "success"
        }
    
    @staticmethod
    def _mock_composition() -> Dict[str, Any]:
        """Return mock composition data with evidence tracking."""
        return {
            "extracted_data": [
                {
                    "alloy": "AZ31",
                    "Mg_percent": 97.1,
                    "Al_percent": 3.0,
                    "Zn_percent": 0.8,
                    "Mn_percent": 0.1,
                    "confidence": 0.92,
                    "source": "Materials section",
                    "evidence": "Nominal composition of AZ31 magnesium alloy from commercial standard",
                    "page_reference": "Page 1",
                    "extraction_method": "LLM agent with mock data"
                },
                {
                    "alloy": "ZE10",
                    "Mg_percent": 98.2,
                    "Zn_percent": 1.0,
                    "rare_earth_percent": 0.8,
                    "confidence": 0.89,
                    "source": "Materials section",
                    "evidence": "ZE10 composition with rare-earth additions for improved creep resistance",
                    "page_reference": "Page 1",
                    "extraction_method": "LLM agent with mock data"
                }
            ],
            "agent_name": "composition_agent",
            "extraction_status": "success"
        }
    
    @staticmethod
    def _mock_processing() -> Dict[str, Any]:
        """Return mock processing data with evidence tracking."""
        return {
            "extracted_data": [
                {
                    "alloy": "AZ31",
                    "rolling_temperature_c": 250,
                    "rolling_reduction_percent": 75,
                    "annealing_temperature_c": 350,
                    "annealing_duration_h": 1,
                    "confidence": 0.80,
                    "source": "Methods section, Table 2",
                    "evidence": "Thermomechanical processing parameters: rolled at 250°C with 75% reduction, annealed at 350°C for 1h",
                    "page_reference": "Page 2",
                    "extraction_method": "LLM agent with mock data"
                }
            ],
            "agent_name": "processing_agent",
            "extraction_status": "success"
        }
    
    @staticmethod
    def _mock_microstructure() -> Dict[str, Any]:
        """Return mock microstructure data with evidence tracking."""
        return {
            "extracted_data": [
                {
                    "alloy": "AZ31",
                    "material_form": "rolled sheet",
                    "avg_grain_size_um": 15,
                    "recrystallized": True,
                    "grain_morphology": "equi-axed",
                    "texture": "strong basal texture",
                    "confidence": 0.82,
                    "source": "Results section",
                    "evidence": "SEM analysis shows recrystallized microstructure with strong basal texture alignment",
                    "page_reference": "Page 3-4",
                    "extraction_method": "LLM agent with mock data"
                },
                {
                    "alloy": "ZE10",
                    "material_form": "extruded profile",
                    "avg_grain_size_um": 8,
                    "recrystallized": True,
                    "grain_morphology": "equi-axed",
                    "texture": "weak texture",
                    "confidence": 0.79,
                    "source": "Results section, Figure 3",
                    "evidence": "EBSD analysis reveals fine recrystallized microstructure typical of ZE10 extrusions",
                    "page_reference": "Page 4-5",
                    "extraction_method": "LLM agent with mock data"
                }
            ],
            "agent_name": "microstructure_agent",
            "extraction_status": "success"
        }
