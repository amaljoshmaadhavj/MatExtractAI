"""Conflict resolution service for handling contradictory extracted values."""

import logging
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ConflictResolution:
    """Represents the resolution of a conflict between values."""
    
    property_name: str
    conflicting_values: List[Dict[str, Any]]  # Each: {value, source, confidence}
    resolution_method: str  # "average", "highest_confidence", "most_recent", "manual_review"
    resolved_value: Optional[float]
    resolved_confidence: float
    tolerance_percent: float
    within_tolerance: bool
    notes: str


class ConflictResolver:
    """Resolves conflicts between values extracted from different agents/sources."""
    
    # Default tolerance for considering values "close enough" (in percent)
    DEFAULT_TOLERANCE = 5.0
    
    # Tolerance overrides for specific properties
    PROPERTY_TOLERANCES = {
        "yield_strength_mpa": 5.0,  # 5% difference acceptable
        "ultimate_tensile_strength_mpa": 5.0,
        "elongation_percent": 10.0,  # 10% for elongation (more variable)
        "grain_size_um": 15.0,  # 15% for grain size (more variable)
        "hardness": 5.0,
        "elastic_modulus_gpa": 5.0,
        "temperature_c": 10.0,  # Absolute diff: 10°C
        "time_h": 10.0,  # Absolute diff: 10% for time
        "reduction_percent": 5.0,
        "composition_percent": 2.0,  # 2% for composition
    }
    
    def __init__(self):
        """Initialize conflict resolver."""
        logger.info("[RESOLVER] Conflict resolver initialized")
    
    def check_for_conflicts(
        self,
        mechanical_data: Dict[str, Any],
        composition_data: Dict[str, Any],
        processing_data: Dict[str, Any],
        microstructure_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check all extracted data for conflicts.
        
        Args:
            mechanical_data: Output from mechanical properties agent
            composition_data: Output from composition agent
            processing_data: Output from processing agent
            microstructure_data: Output from microstructure agent
            
        Returns:
            Dictionary with conflict detection results and recommendations
        """
        conflicts = []
        
        # Extract actual data lists
        mech_items = mechanical_data.get("extracted_data", [])
        comp_items = composition_data.get("extracted_data", [])
        proc_items = processing_data.get("extracted_data", [])
        micro_items = microstructure_data.get("extracted_data", [])
        
        # Check within-agent conflicts (same property, different values)
        logger.info("[RESOLVER] Checking for within-agent conflicts...")
        conflicts.extend(self._check_within_agent_conflicts(mech_items, "mechanical"))
        conflicts.extend(self._check_within_agent_conflicts(comp_items, "composition"))
        conflicts.extend(self._check_within_agent_conflicts(proc_items, "processing"))
        conflicts.extend(self._check_within_agent_conflicts(micro_items, "microstructure"))
        
        # Check cross-agent conflicts
        logger.info("[RESOLVER] Checking for cross-agent conflicts...")
        conflicts.extend(self._check_cross_agent_conflicts(
            mech_items, comp_items, proc_items, micro_items
        ))
        
        logger.info(f"[RESOLVER] Found {len(conflicts)} potential conflicts")
        
        return {
            "conflict_count": len(conflicts),
            "conflicts": conflicts,
            "resolution_required": len(conflicts) > 0
        }
    
    def _check_within_agent_conflicts(
        self,
        items: List[Dict[str, Any]],
        agent_name: str
    ) -> List[ConflictResolution]:
        """Check for conflicts within a single agent's results."""
        conflicts = []
        
        if len(items) <= 1:
            return conflicts
        
        # Group items by material name if available
        by_material = {}
        for item in items:
            material = item.get("material") or item.get("alloy_name") or item.get("material_form", "unknown")
            if material not in by_material:
                by_material[material] = []
            by_material[material].append(item)
        
        # Check for property conflicts within same material
        for material, material_items in by_material.items():
            if len(material_items) <= 1:
                continue
            
            # Get all numeric properties
            numeric_props = self._get_numeric_properties(material_items[0])
            
            for prop_name in numeric_props:
                values_with_sources = [
                    {
                        "value": item.get(prop_name),
                        "source": item.get("source", "unknown"),
                        "confidence": item.get("confidence", 0.5)
                    }
                    for item in material_items
                    if item.get(prop_name) is not None
                ]
                
                if len(values_with_sources) > 1:
                    conflict = self._analyze_value_conflict(
                        prop_name,
                        values_with_sources,
                        f"{agent_name} agent"
                    )
                    if conflict:
                        conflicts.append(conflict)
        
        return conflicts
    
    def _check_cross_agent_conflicts(
        self,
        mech_items: List[Dict[str, Any]],
        comp_items: List[Dict[str, Any]],
        proc_items: List[Dict[str, Any]],
        micro_items: List[Dict[str, Any]]
    ) -> List[ConflictResolution]:
        """Check for conflicts between different agents."""
        conflicts = []
        
        # Check if grain size from microstructure conflicts with grain size from mechanical
        mech_grain_sizes = [
            {"value": item.get("grain_size_um"), "source": "mechanical"}
            for item in mech_items
            if item.get("grain_size_um") is not None
        ]
        micro_grain_sizes = [
            {"value": item.get("grain_size_um"), "source": "microstructure"}
            for item in micro_items
            if item.get("grain_size_um") is not None
        ]
        
        if mech_grain_sizes and micro_grain_sizes:
            combined = mech_grain_sizes + micro_grain_sizes
            if len(combined) > 1:
                conflict = self._analyze_value_conflict(
                    "grain_size_um",
                    combined,
                    "cross-agent (mechanical vs microstructure)"
                )
                if conflict:
                    conflicts.append(conflict)
        
        # Check if composition percentages are consistent
        # Example: if composition shows 97% Mg, but other elements add up differently
        for comp_item in comp_items:
            comp_dict = comp_item.get("composition_percent", {})
            if comp_dict:
                total_percent = sum(
                    float(str(v).rstrip('%')) 
                    for v in comp_dict.values() 
                    if isinstance(v, (int, float, str))
                )
                if 95 < total_percent < 101:
                    # Composition is reasonable
                    pass
                elif total_percent > 0:
                    # Composition adds up incorrectly
                    logger.warning(
                        f"[RESOLVER] Composition percentages sum to {total_percent}% "
                        f"(expected ~100%): {comp_dict}"
                    )
        
        return conflicts
    
    def _analyze_value_conflict(
        self,
        property_name: str,
        values_with_sources: List[Dict[str, Any]],
        context: str
    ) -> Optional[ConflictResolution]:
        """
        Analyze a conflict between multiple values for the same property.
        
        Args:
            property_name: Name of the property with conflicting values
            values_with_sources: List of {value, source, confidence} dicts
            context: Description of the context (agent, source, etc.)
            
        Returns:
            ConflictResolution object or None if no conflict
        """
        if len(values_with_sources) < 2:
            return None
        
        # Extract numeric values
        values = [v["value"] for v in values_with_sources if v["value"] is not None]
        if len(values) < 2:
            return None
        
        # Check if values are within tolerance
        min_val = min(values)
        max_val = max(values)
        
        # Determine tolerance
        tolerance = self.PROPERTY_TOLERANCES.get(property_name, self.DEFAULT_TOLERANCE)
        
        # Calculate percent difference
        if min_val != 0:
            percent_diff = ((max_val - min_val) / min_val) * 100
        else:
            percent_diff = max_val * 100  # If min is 0
        
        within_tolerance = percent_diff <= tolerance
        
        # Determine resolution method
        if within_tolerance:
            # Average values weighted by confidence
            resolution_method = "weighted_average"
            total_weight = sum(v.get("confidence", 0.5) for v in values_with_sources)
            weighted_sum = sum(
                v["value"] * v.get("confidence", 0.5)
                for v in values_with_sources
            )
            resolved_value = weighted_sum / total_weight if total_weight > 0 else None
            resolved_confidence = min(
                (c := sum(v.get("confidence", 0.5) for v in values_with_sources) / len(values_with_sources)),
                0.95  # Cap at 0.95 since there's uncertainty
            )
            notes = f"Values within {tolerance}% tolerance. Averaged: {resolved_value:.2f}"
        else:
            # Use highest confidence value
            resolution_method = "highest_confidence"
            best = max(values_with_sources, key=lambda x: x.get("confidence", 0.5))
            resolved_value = best["value"]
            resolved_confidence = best.get("confidence", 0.5) * 0.9  # Reduce confidence due to conflict
            notes = f"Values exceed {tolerance}% tolerance (diff: {percent_diff:.1f}%). Using highest confidence source."
        
        logger.warning(
            f"[RESOLVER] Conflict detected in {property_name} ({context}): "
            f"values {values}, percent_diff={percent_diff:.1f}%, "
            f"resolution={resolution_method}"
        )
        
        return ConflictResolution(
            property_name=property_name,
            conflicting_values=values_with_sources,
            resolution_method=resolution_method,
            resolved_value=resolved_value,
            resolved_confidence=resolved_confidence,
            tolerance_percent=tolerance,
            within_tolerance=within_tolerance,
            notes=notes
        )
    
    def resolve_conflicts(
        self,
        conflicts: List[ConflictResolution]
    ) -> Dict[str, Any]:
        """
        Apply conflict resolutions to produce final values.
        
        Args:
            conflicts: List of ConflictResolution objects
            
        Returns:
            Dictionary with resolved values and conflict notes
        """
        resolved_data = {}
        conflict_notes = []
        
        for conflict in conflicts:
            resolved_data[conflict.property_name] = {
                "value": conflict.resolved_value,
                "confidence": conflict.resolved_confidence,
                "resolution_method": conflict.resolution_method,
                "conflicting_sources": [
                    {
                        "source": v.get("source", "unknown"),
                        "value": v.get("value"),
                        "confidence": v.get("confidence", 0.5)
                    }
                    for v in conflict.conflicting_values
                ],
                "notes": conflict.notes
            }
            
            conflict_notes.append({
                "property": conflict.property_name,
                "resolution": conflict.resolution_method,
                "resolved_value": conflict.resolved_value,
                "confidence": conflict.resolved_confidence,
                "note": conflict.notes
            })
        
        logger.info(f"[RESOLVER] Resolved {len(conflicts)} conflicts")
        
        return {
            "resolved_count": len(conflicts),
            "resolved_data": resolved_data,
            "conflict_notes": conflict_notes
        }
    
    def _get_numeric_properties(self, item: Dict[str, Any]) -> List[str]:
        """Get all numeric property names from an item."""
        numeric_props = []
        for key, value in item.items():
            if isinstance(value, (int, float)) and not key.startswith("_"):
                numeric_props.append(key)
        return numeric_props
