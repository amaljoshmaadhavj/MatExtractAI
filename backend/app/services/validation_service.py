"""Comprehensive validation service for extracted data with evidence tracking."""

import logging
import re
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ValidationService:
    """Service for validating extraction results with comprehensive quality scoring."""
    
    # Valid ranges for common material properties
    KNOWN_PROPERTY_RANGES = {
        "yield_strength_mpa": (5, 1500),  # MPa
        "ultimate_tensile_strength_mpa": (10, 2000),  # MPa
        "elongation_percent": (0.1, 100),  # %
        "grain_size_um": (0.001, 1000),  # micrometers
        "hardness": (20, 1000),  # HV/HB
        "elastic_modulus_gpa": (1, 500),  # GPa
        "temperature_c": (-50, 2000),  # Celsius
        "duration_h": (0.01, 500),  # Hours
    }
    
    def __init__(self):
        """Initialize validation service."""
        logger.info("[VALIDATION] Validation service initialized")
    
    def validate_results(self, all_results: Dict[str, Any], full_text: str = "") -> Dict[str, Any]:
        """
        Comprehensive validation of extraction results.
        
        Args:
            all_results: All extraction results from agents
            full_text: Full document text for evidence verification
            
        Returns:
            Detailed validation results with confidence scores
        """
        try:
            logger.info("[VALIDATION] Starting comprehensive validation...")
            
            # Validate each component
            mechanical_validation = self._validate_component(
                all_results.get("mechanical_properties", {}),
                "mechanical_properties",
                full_text
            )
            
            composition_validation = self._validate_component(
                all_results.get("composition", {}),
                "composition",
                full_text
            )
            
            processing_validation = self._validate_component(
                all_results.get("processing", {}),
                "processing",
                full_text
            )
            
            microstructure_validation = self._validate_component(
                all_results.get("microstructure", {}),
                "microstructure",
                full_text
            )
            
            tables_validation = self._validate_component(
                all_results.get("tables", {}),
                "tables",
                full_text
            )
            
            # Calculate cross-agent agreement
            cross_agent_agreement = self._calculate_cross_agent_agreement(all_results)
            
            # Compile validation results
            validation_results = {
                "validation_timestamp": datetime.now().isoformat(),
                "component_validation": {
                    "mechanical_properties": mechanical_validation,
                    "composition": composition_validation,
                    "processing": processing_validation,
                    "microstructure": microstructure_validation,
                    "tables": tables_validation
                },
                "cross_agent_agreement": cross_agent_agreement,
                "overall_quality_metrics": self._calculate_overall_metrics(
                    mechanical_validation,
                    composition_validation,
                    processing_validation,
                    microstructure_validation,
                    tables_validation
                ),
                "validation_status": "completed"
            }
            
            logger.info(f"[VALIDATION] Validation completed successfully")
            return validation_results
            
        except Exception as e:
            logger.error(f"[VALIDATION] Error during validation: {e}")
            return {
                "validation_status": "failed",
                "error": str(e),
                "component_validation": {},
                "overall_quality_metrics": {}
            }
    
    def _validate_component(self, component_data: Dict[str, Any], 
                           component_type: str, full_text: str = "") -> Dict[str, Any]:
        """
        Validate a single component (mechanical, composition, etc.).
        
        Args:
            component_data: Component data from agent
            component_type: Type of component
            full_text: Full document text for evidence verification
            
        Returns:
            Validation results for this component
        """
        try:
            extracted_items = component_data.get("extracted_data", [])
            
            if not extracted_items:
                return {
                    "status": "no_data",
                    "item_count": 0,
                    "extraction_confidence": 0.0,
                    "evidence_confidence": 0.0,
                    "overall_score": 0.0,
                    "items": []
                }
            
            # Validate each extracted item
            validated_items = []
            confidence_scores = []
            evidence_scores = []
            
            for item in extracted_items:
                if isinstance(item, dict):
                    item_validation = self._validate_item(item, component_type, full_text)
                    validated_items.append(item_validation)
                    confidence_scores.append(item_validation.get("extraction_confidence", 0))
                    evidence_scores.append(item_validation.get("evidence_confidence", 0))
            
            # Calculate component-level metrics
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            avg_evidence = sum(evidence_scores) / len(evidence_scores) if evidence_scores else 0
            overall_score = (avg_confidence * 0.6 + avg_evidence * 0.4)
            
            return {
                "status": "validated",
                "item_count": len(validated_items),
                "extraction_confidence": round(avg_confidence, 3),
                "evidence_confidence": round(avg_evidence, 3),
                "overall_score": round(overall_score, 3),
                "quality_assessment": self._get_quality_assessment(overall_score),
                "items": validated_items
            }
            
        except Exception as e:
            logger.warning(f"[VALIDATION] Error validating {component_type}: {e}")
            return {
                "status": "error",
                "item_count": 0,
                "extraction_confidence": 0.0,
                "error": str(e)
            }
    
    def _validate_item(self, item: Dict[str, Any], component_type: str, 
                      full_text: str = "") -> Dict[str, Any]:
        """
        Validate a single extracted item.
        
        Args:
            item: Item to validate
            component_type: Type of component
            full_text: Full document text
            
        Returns:
            Validated item with quality scores
        """
        try:
            extraction_confidence = item.get("confidence", 0.75)
            evidence_text = item.get("source", "") or item.get("evidence", "")
            
            # Verify evidence if available
            evidence_confidence = 1.0
            if evidence_text and full_text:
                evidence_confidence = self._verify_evidence(evidence_text, full_text)
            
            # Validate numeric ranges
            range_valid = self._validate_numeric_ranges(item, component_type)
            
            # Compile validation
            validated_item = {
                "original_data": item.copy(),
                "extraction_confidence": round(extraction_confidence, 3),
                "evidence_confidence": round(evidence_confidence, 3),
                "range_valid": range_valid,
                "quality_score": round((extraction_confidence * 0.5 + evidence_confidence * 0.3 + 
                                       (1.0 if range_valid else 0.3) * 0.2), 3),
                "validation_notes": self._generate_validation_notes(item, component_type, range_valid, evidence_confidence)
            }
            
            return validated_item
            
        except Exception as e:
            logger.warning(f"[VALIDATION] Error validating item: {e}")
            return {
                "original_data": item,
                "extraction_confidence": 0.0,
                "error": str(e)
            }
    
    def _verify_evidence(self, evidence_text: str, full_text: str) -> float:
        """
        Verify that evidence text appears in the full document.
        
        Args:
            evidence_text: Evidence reference text
            full_text: Full document text
            
        Returns:
            Confidence score (0-1) based on evidence verification
        """
        try:
            if not evidence_text or not full_text:
                return 0.6  # Neutral confidence if no evidence
            
            # Check if evidence source is mentioned
            evidence_lower = evidence_text.lower()
            text_lower = full_text.lower()
            
            # Look for exact match
            if evidence_lower in text_lower:
                return 1.0
            
            # Look for partial match (section names, page references)
            keywords = evidence_lower.split()
            match_ratio = sum(1 for kw in keywords if len(kw) > 3 and kw in text_lower) / max(len([k for k in keywords if len(k) > 3]), 1)
            
            return min(0.95, match_ratio + 0.3)  # Cap at 0.95
            
        except Exception as e:
            logger.debug(f"[VALIDATION] Error verifying evidence: {e}")
            return 0.6
    
    def _validate_numeric_ranges(self, item: Dict[str, Any], component_type: str) -> bool:
        """
        Validate that numeric values are within known ranges.
        
        Args:
            item: Item with potential numeric values
            component_type: Type of component
            
        Returns:
            True if all numeric values are within valid ranges
        """
        try:
            for key, value in item.items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    # Check if this key matches a known property
                    for prop_key, (min_val, max_val) in self.KNOWN_PROPERTY_RANGES.items():
                        if prop_key in key.lower():
                            if not (min_val <= value <= max_val):
                                logger.debug(f"[VALIDATION] Value {key}={value} outside range [{min_val}, {max_val}]")
                                return False
            
            return True
            
        except Exception as e:
            logger.debug(f"[VALIDATION] Error validating ranges: {e}")
            return True  # Default to valid if we can't check
    
    def _generate_validation_notes(self, item: Dict[str, Any], component_type: str, 
                                   range_valid: bool, evidence_confidence: float) -> str:
        """Generate human-readable validation notes."""
        notes = []
        
        if not range_valid:
            notes.append("⚠ Some values outside expected ranges")
        
        if evidence_confidence < 0.5:
            notes.append("⚠ Weak evidence linking")
        elif evidence_confidence >= 0.9:
            notes.append("✓ Strong evidence found")
        
        if item.get("confidence", 0) < 0.7:
            notes.append("⚠ Low extraction confidence")
        
        if not notes:
            notes.append("✓ Valid")
        
        return " | ".join(notes)
    
    def _calculate_cross_agent_agreement(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate agreement between different agents.
        
        Args:
            all_results: All extraction results
            
        Returns:
            Cross-agent agreement metrics
        """
        try:
            logger.info("[VALIDATION] Calculating cross-agent agreement...")
            
            # Extract material/alloy names from different agents
            mech_materials = self._extract_entities(all_results.get("mechanical_properties", {}))
            comp_materials = self._extract_entities(all_results.get("composition", {}))
            proc_materials = self._extract_entities(all_results.get("processing", {}))
            micro_materials = self._extract_entities(all_results.get("microstructure", {}))
            
            # Calculate agreement scores
            agreement_scores = {}
            all_materials = set(mech_materials + comp_materials + proc_materials + micro_materials)
            
            if all_materials:
                # Agreement = materials appearing in multiple agents
                agreement_counts = {}
                for mat in all_materials:
                    count = sum([
                        mat in mech_materials,
                        mat in comp_materials,
                        mat in proc_materials,
                        mat in micro_materials
                    ])
                    agreement_counts[mat] = count
                
                # Calculate average agreement
                avg_agreement = sum(agreement_counts.values()) / len(all_materials) / 4.0 if all_materials else 0
                agreement_scores["material_agreement"] = round(avg_agreement, 3)
                agreement_scores["consensus_level"] = "high" if avg_agreement >= 0.75 else "medium" if avg_agreement >= 0.5 else "low"
            else:
                agreement_scores["material_agreement"] = 0.0
                agreement_scores["consensus_level"] = "none"
            
            # Count how many agents found data
            agents_with_data = sum([
                len(all_results.get("mechanical_properties", {}).get("extracted_data", [])) > 0,
                len(all_results.get("composition", {}).get("extracted_data", [])) > 0,
                len(all_results.get("processing", {}).get("extracted_data", [])) > 0,
                len(all_results.get("microstructure", {}).get("extracted_data", [])) > 0
            ])
            
            agreement_scores["agents_with_data"] = agents_with_data
            agreement_scores["coverage_percentage"] = round((agents_with_data / 4.0) * 100, 1)
            
            logger.info(f"[VALIDATION] Cross-agent agreement: {agreement_scores}")
            return agreement_scores
            
        except Exception as e:
            logger.warning(f"[VALIDATION] Error calculating cross-agent agreement: {e}")
            return {
                "material_agreement": 0.0,
                "consensus_level": "unknown",
                "error": str(e)
            }
    
    def _extract_entities(self, component_data: Dict[str, Any]) -> List[str]:
        """Extract material/entity names from component data."""
        entities = []
        extracted_items = component_data.get("extracted_data", [])
        
        if isinstance(extracted_items, list):
            for item in extracted_items:
                if isinstance(item, dict):
                    # Look for common material identifier keys
                    for key in ["material", "alloy_name", "material_form", "name"]:
                        if key in item:
                            val = item[key]
                            if isinstance(val, str) and val.strip():
                                entities.append(val.lower().strip())
                                break
        
        return list(set(entities))  # Remove duplicates
    
    def _calculate_overall_metrics(self, *component_validations) -> Dict[str, Any]:
        """Calculate overall quality metrics across all components."""
        try:
            component_scores = []
            
            for comp_val in component_validations:
                if isinstance(comp_val, dict) and comp_val.get("status") == "validated":
                    component_scores.append(comp_val.get("overall_score", 0))
            
            if component_scores:
                overall_score = sum(component_scores) / len(component_scores)
                data_completeness = len([s for s in component_scores if s > 0]) / len(component_scores)
            else:
                overall_score = 0.0
                data_completeness = 0.0
            
            return {
                "overall_confidence": round(overall_score, 3),
                "quality_level": self._get_quality_assessment(overall_score),
                "data_completeness": round(data_completeness * 100, 1),
                "components_validated": len(component_scores),
                "recommendation": self._get_recommendation(overall_score, data_completeness)
            }
            
        except Exception as e:
            logger.warning(f"[VALIDATION] Error calculating overall metrics: {e}")
            return {
                "overall_confidence": 0.0,
                "error": str(e)
            }
    
    @staticmethod
    def _get_quality_assessment(score: float) -> str:
        """Get quality assessment label based on score."""
        if score >= 0.90:
            return "excellent"
        elif score >= 0.80:
            return "good"
        elif score >= 0.70:
            return "acceptable"
        elif score >= 0.60:
            return "fair"
        elif score > 0:
            return "poor"
        else:
            return "unknown"
    
    @staticmethod
    def _get_recommendation(score: float, completeness: float) -> str:
        """Get recommendation based on validation metrics."""
        if score >= 0.85 and completeness >= 0.75:
            return "Results are reliable and ready for use"
        elif score >= 0.75 and completeness >= 0.60:
            return "Results are usable with minor caveats"
        elif score >= 0.60:
            return "Results should be reviewed before use"
        else:
            return "Results require significant manual verification"
