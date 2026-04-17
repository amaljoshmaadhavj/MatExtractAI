"""Master consolidation agent for merging multi-agent extraction results."""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import uuid

from .conflict_resolver import ConflictResolver
from .data_normalizer import DataNormalizer

logger = logging.getLogger(__name__)


class ConsolidationAgent:
    """
    Master consolidation agent that merges output from 4 extraction agents
    into unified material records with conflict resolution and evidence tracking.
    """
    
    def __init__(self):
        """Initialize consolidation agent."""
        self.conflict_resolver = ConflictResolver()
        self.data_normalizer = DataNormalizer()
        logger.info("[CONSOLIDATION] Consolidation agent initialized with DataNormalizer")
    
    def consolidate(
        self,
        mechanical_data: Dict[str, Any],
        composition_data: Dict[str, Any],
        processing_data: Dict[str, Any],
        microstructure_data: Dict[str, Any],
        full_document_text: str = "",
        document_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Consolidate outputs from all 4 agents into unified MaterialRecord(s).
        
        Args:
            mechanical_data: Output from mechanical properties agent
            composition_data: Output from composition agent
            processing_data: Output from processing agent
            microstructure_data: Output from microstructure agent
            full_document_text: Full text of the document (for evidence verification)
            document_metadata: Optional metadata about the document
            
        Returns:
            Dictionary with consolidated material records and conflict information
        """
        logger.info("[CONSOLIDATION] Starting consolidation of agent outputs...")
        
        # Extract data from agent outputs
        mech_items = mechanical_data.get("extracted_data", [])
        comp_items = composition_data.get("extracted_data", [])
        proc_items = processing_data.get("extracted_data", [])
        micro_items = microstructure_data.get("extracted_data", [])
        
        logger.info(
            f"[CONSOLIDATION] Agent data summary: "
            f"mechanical={len(mech_items)}, composition={len(comp_items)}, "
            f"processing={len(proc_items)}, microstructure={len(micro_items)}"
        )
        
        # Check for conflicts
        logger.info("[CONSOLIDATION] Checking for conflicts...")
        conflict_report = self.conflict_resolver.check_for_conflicts(
            mechanical_data, composition_data, processing_data, microstructure_data
        )
        
        # Identify materials being studied
        logger.info("[CONSOLIDATION] Identifying materials...")
        material_names = self._identify_materials(comp_items, mech_items, micro_items)
        
        # Create material records
        material_records = []
        for material_name in material_names:
            logger.info(f"[CONSOLIDATION] Creating record for material: {material_name}")
            
            record = self._create_material_record(
                material_name,
                mech_items,
                comp_items,
                proc_items,
                micro_items,
                full_document_text,
                document_metadata
            )
            material_records.append(record)
        
        # If no specific materials identified, create default record
        if not material_records:
            logger.warning("[CONSOLIDATION] No specific materials identified, creating generic record")
            record = self._create_generic_material_record(
                mech_items, comp_items, proc_items, micro_items,
                full_document_text, document_metadata
            )
            material_records.append(record)
        
        logger.info(f"[CONSOLIDATION] Successfully created {len(material_records)} material record(s)")
        
        return {
            "consolidation_status": "success",
            "material_records": material_records,
            "total_materials": len(material_records),
            "conflict_report": conflict_report,
            "consolidation_timestamp": datetime.now().isoformat(),
            "agent_summary": {
                "mechanical_properties": mechanical_data.get("extraction_status", "unknown"),
                "composition": composition_data.get("extraction_status", "unknown"),
                "processing": processing_data.get("extraction_status", "unknown"),
                "microstructure": microstructure_data.get("extraction_status", "unknown")
            }
        }
    
    def _identify_materials(
        self,
        comp_items: List[Dict[str, Any]],
        mech_items: List[Dict[str, Any]],
        micro_items: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Identify unique material names from extracted data.
        
        Args:
            comp_items: Composition agent output
            mech_items: Mechanical properties agent output
            micro_items: Microstructure agent output
            
        Returns:
            List of unique material names
        """
        materials = set()
        
        # From composition
        for comp in comp_items:
            if "alloy_name" in comp and comp["alloy_name"]:
                materials.add(comp["alloy_name"].strip())
        
        # From mechanical properties
        for mech in mech_items:
            if "material" in mech and mech["material"]:
                materials.add(mech["material"].strip())
        
        # From microstructure
        for micro in micro_items:
            if "material" in micro and micro["material"]:
                materials.add(micro["material"].strip())
        
        # Filter out generic names
        materials = {m for m in materials if m and m.lower() not in ["unknown", "material", "alloy"]}
        
        logger.info(f"[CONSOLIDATION] Identified materials: {materials}")
        return sorted(list(materials))
    
    def _create_material_record(
        self,
        material_name: str,
        mech_items: List[Dict[str, Any]],
        comp_items: List[Dict[str, Any]],
        proc_items: List[Dict[str, Any]],
        micro_items: List[Dict[str, Any]],
        full_document_text: str,
        document_metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create a comprehensive MaterialRecord for a specific material.
        
        Args:
            material_name: Name of the material
            mech_items, comp_items, proc_items, micro_items: Agent outputs
            full_document_text: Full document text for evidence
            document_metadata: Document metadata
            
        Returns:
            Complete MaterialRecord dictionary
        """
        
        # Filter data for this specific material
        mech_for_material = self._filter_by_material(mech_items, material_name, ["material"])
        comp_for_material = self._filter_by_material(comp_items, material_name, ["alloy_name"])
        proc_for_material = self._filter_by_material(proc_items, material_name, [])
        micro_for_material = self._filter_by_material(micro_items, material_name, ["material"])
        
        # Extract composition
        composition_record = self._extract_composition_record(comp_for_material)
        
        # Extract processing
        processing_record = self._extract_processing_record(proc_for_material)
        
        # Extract microstructure
        microstructure_record = self._extract_microstructure_record(micro_for_material)
        
        # Extract mechanical properties
        properties_records = self._extract_properties_records(mech_for_material)
        
        # Build evidence chain
        evidence_chain = self._build_evidence_chain(
            mech_for_material, comp_for_material, proc_for_material, micro_for_material,
            full_document_text
        )
        
        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(
            mech_for_material, comp_for_material, proc_for_material, micro_for_material
        )
        
        # Create record
        record = {
            "record_id": str(uuid.uuid4()),
            "material_name": material_name,
            "material_variants": [material_name],  # Could be expanded if variants found
            
            "composition": composition_record,
            "processing": processing_record,
            "microstructure": microstructure_record,
            "properties": properties_records,
            
            "evidence_chain": evidence_chain,
            
            "extraction_confidence": overall_confidence,
            
            "consolidation_method": "master_agent_v1",
            "consolidation_timestamp": datetime.now().isoformat(),
            
            "document_metadata": document_metadata or {},
            "agent_contributions": {
                "mechanical_properties": len(mech_for_material),
                "composition": len(comp_for_material),
                "processing": len(proc_for_material),
                "microstructure": len(micro_for_material)
            }
        }
        
        # Normalize all properties in the record
        logger.info(f"[CONSOLIDATION] Normalizing data for {material_name}...")
        record = self.data_normalizer.normalize_all_properties(record)
        
        logger.info(f"[CONSOLIDATION] Created and normalized record for {material_name} with confidence {overall_confidence:.2f}")
        
        return record
    
    def _create_generic_material_record(
        self,
        mech_items: List[Dict[str, Any]],
        comp_items: List[Dict[str, Any]],
        proc_items: List[Dict[str, Any]],
        micro_items: List[Dict[str, Any]],
        full_document_text: str,
        document_metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create a generic material record when no specific name is identified."""
        return self._create_material_record(
            "Unidentified Material",
            mech_items, comp_items, proc_items, micro_items,
            full_document_text, document_metadata
        )
    
    def _filter_by_material(
        self,
        items: List[Dict[str, Any]],
        material_name: str,
        material_fields: List[str]
    ) -> List[Dict[str, Any]]:
        """Filter items by material name."""
        if not items or not material_name:
            return items
        
        if not material_fields:
            # If no specific fields, return all items
            return items
        
        filtered = []
        material_lower = material_name.lower()
        
        for item in items:
            for field in material_fields:
                item_value = item.get(field, "")
                if isinstance(item_value, str) and material_lower in item_value.lower():
                    filtered.append(item)
                    break
        
        # If no matches, return all items (might be single-material paper)
        return filtered if filtered else items
    
    def _extract_composition_record(self, comp_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract composition information into standardized format."""
        if not comp_items:
            return {"status": "not_found", "elements": []}
        
        # Use first item (or could merge multiple)
        comp = comp_items[0]
        
        elements = []
        comp_dict = comp.get("composition_percent", {})
        for element, percent_str in comp_dict.items():
            # Parse percentage
            try:
                if isinstance(percent_str, str):
                    percent_val = float(percent_str.rstrip('%'))
                else:
                    percent_val = float(percent_str)
            except (ValueError, AttributeError):
                percent_val = None
            
            if percent_val is not None:
                elements.append({
                    "element": element.strip(),
                    "percent": percent_val,
                    "unit": "wt%"  # Assume wt% unless otherwise specified
                })
        
        return {
            "primary_elements": sorted(elements, key=lambda x: x["percent"], reverse=True),
            "alloy_name": comp.get("alloy_name", ""),
            "source": comp.get("source", "composition agent"),
            "confidence": comp.get("confidence", 0.7),
            "evidence": comp.get("evidence", "")
        }
    
    def _extract_processing_record(self, proc_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract processing information into standardized format."""
        if not proc_items:
            return {"status": "not_found", "steps": []}
        
        proc = proc_items[0]
        
        steps = proc.get("processing_steps", [])
        if isinstance(steps, list) and steps:
            # Ensure each step has required fields
            processed_steps = []
            for step in steps:
                processed_step = {
                    "type": step.get("step", "unknown"),
                    "temperature_c": step.get("temperature_c"),
                    "duration_h": step.get("duration_h"),
                    "cooling_type": step.get("cooling_type"),
                    "other_parameters": {
                        k: v for k, v in step.items()
                        if k not in ["step", "temperature_c", "duration_h", "cooling_type"]
                    }
                }
                processed_steps.append(processed_step)
        else:
            processed_steps = []
        
        return {
            "steps": processed_steps,
            "material_form": proc.get("material_form", ""),
            "source": proc.get("source", "processing agent"),
            "confidence": proc.get("confidence", 0.7),
            "evidence": proc.get("evidence", "")
        }
    
    def _extract_microstructure_record(self, micro_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract microstructure information into standardized format."""
        if not micro_items:
            return {"status": "not_found"}
        
        micro = micro_items[0]
        
        return {
            "grain_size_um": micro.get("grain_size_um"),
            "phases": micro.get("phases", []) if isinstance(micro.get("phases"), list) else [],
            "texture": micro.get("texture", ""),
            "morphology": micro.get("morphology", ""),
            "recrystallized": micro.get("recrystallized"),
            "source": micro.get("source", "microstructure agent"),
            "confidence": micro.get("confidence", 0.7),
            "evidence": micro.get("evidence", "")
        }
    
    def _extract_properties_records(self, mech_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract mechanical properties into standardized format."""
        if not mech_items:
            return []
        
        properties = []
        for mech in mech_items:
            prop = {
                "yield_strength_mpa": mech.get("yield_strength_mpa"),
                "ultimate_tensile_strength_mpa": mech.get("ultimate_tensile_strength_mpa"),
                "elongation_percent": mech.get("elongation_percent"),
                "hardness": mech.get("hardness"),
                "elastic_modulus_gpa": mech.get("elastic_modulus_gpa"),
                "grain_size_um": mech.get("grain_size_um"),
                
                "test_condition": mech.get("test_condition", ""),
                "source": mech.get("source", "mechanical agent"),
                "confidence": mech.get("confidence", 0.7),
                "evidence": mech.get("evidence", "")
            }
            properties.append(prop)
        
        return properties
    
    def _build_evidence_chain(
        self,
        mech_items, comp_items, proc_items, micro_items,
        full_document_text: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Build complete evidence chain showing traceability."""
        return {
            "composition": [
                {"source": item.get("source", ""), "evidence": item.get("evidence", "")}
                for item in comp_items
            ],
            "processing": [
                {"source": item.get("source", ""), "evidence": item.get("evidence", "")}
                for item in proc_items
            ],
            "microstructure": [
                {"source": item.get("source", ""), "evidence": item.get("evidence", "")}
                for item in micro_items
            ],
            "properties": [
                {"source": item.get("source", ""), "evidence": item.get("evidence", "")}
                for item in mech_items
            ],
            "document_text_length": len(full_document_text)
        }
    
    def _calculate_overall_confidence(
        self,
        mech_items, comp_items, proc_items, micro_items
    ) -> float:
        """Calculate overall extraction confidence."""
        all_items = mech_items + comp_items + proc_items + micro_items
        
        if not all_items:
            return 0.5
        
        # Average confidence from all items
        confidences = [item.get("confidence", 0.7) for item in all_items]
        avg_confidence = sum(confidences) / len(confidences)
        
        # Adjust based on data richness
        richness_factor = min(1.0, len(all_items) / 10)  # More items = higher confidence
        agent_diversity = len({item.get("source", "") for item in all_items}) / 4  # Up to 4 agents
        
        # Weighted average
        final_confidence = (
            avg_confidence * 0.6 +
            richness_factor * 0.2 +
            agent_diversity * 0.2
        )
        
        return min(final_confidence, 0.95)
