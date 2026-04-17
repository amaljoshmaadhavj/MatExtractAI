"""Data normalization and standardization service for extracted materials data."""

import logging
import re
from typing import Dict, Any, Tuple, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class NormalizationResult:
    """Result of normalizing a value."""
    original_value: Any
    normalized_value: Any
    original_unit: Optional[str]
    normalized_unit: Optional[str]
    conversion_factor: float = 1.0
    was_normalized: bool = False
    warnings: List[str] = None


class DataNormalizer:
    """
    Normalizes and standardizes all extracted materials data.
    Handles units, formats, material names, and semantic validation.
    """
    
    # Standard units for materials properties
    STANDARD_UNITS = {
        "stress": "MPa",
        "strain": "%",
        "length": "μm",
        "temperature": "°C",
        "time": "h",
        "composition": "wt%",
        "hardness": "HV",
        "modulus": "GPa",
    }
    
    # Unit conversion maps: from_unit -> (to_unit, conversion_factor)
    UNIT_CONVERSIONS = {
        # Stress/Pressure
        "gpa": ("MPa", 1000.0),
        "kpa": ("MPa", 0.001),
        "pa": ("MPa", 0.000001),
        "psi": ("MPa", 0.00689476),
        
        # Length
        "nm": ("μm", 0.001),
        "mm": ("μm", 1000.0),
        "cm": ("μm", 10000.0),
        "in": ("μm", 25400.0),
        
        # Temperature
        "f": ("°C", lambda x: (x - 32) * 5/9),  # Fahrenheit to Celsius
        "k": ("°C", lambda x: x - 273.15),       # Kelvin to Celsius
        
        # Time
        "min": ("h", lambda x: x / 60.0),
        "minute": ("h", lambda x: x / 60.0),
        "s": ("h", lambda x: x / 3600.0),
        "sec": ("h", lambda x: x / 3600.0),
        "second": ("h", lambda x: x / 3600.0),
        
        # Composition
        "at%": ("wt%", None),  # Can't convert without atomic masses
        "mol%": ("wt%", None),
    }
    
    # Material name normalization patterns
    MATERIAL_PATTERNS = {
        # Magnesium alloys
        r"az[-\s]*31[a-z]*": "AZ31",
        r"az[-\s]*91[a-z]*": "AZ91",
        r"az[-\s]*63[a-z]*": "AZ63",
        r"am[-\s]*\d+": lambda m: m.group(0).replace(" ", "").replace("-", "").upper(),
        
        # Aluminum alloys
        r"al[-\s]*(?:7075|2024|6061|5083)": lambda m: "Al" + re.sub(r'[-\s]', '', m.group(0).split('al')[1]).upper(),
        
        # Titanium alloys
        r"ti[-\s]*6[-\s]*al[-\s]*4[-\s]*v": "Ti-6Al-4V",
        r"ti[-\s]*5[-\s]*al[-\s]*2\.5[\s\-]*sn": "Ti-5Al-2.5Sn",
        
        # Steel
        r"aisi\s*(\d+)": lambda m: "AISI" + m.group(1),
        r"ss\s*(\d+)": lambda m: "SS" + m.group(1),
    }
    
    # Element symbol standardization
    ELEMENT_MAP = {
        "aluminum": "Al",
        "magnesium": "Mg",
        "zinc": "Zn",
        "manganese": "Mn",
        "copper": "Cu",
        "titanium": "Ti",
        "iron": "Fe",
        "nickel": "Ni",
        "chromium": "Cr",
        "molybdenum": "Mo",
        "silicon": "Si",
        "carbon": "C",
        "nitrogen": "N",
        "oxygen": "O",
        "sulfur": "S",
        "phosphorus": "P",
        "cobalt": "Co",
        "tungsten": "W",
        "tantalum": "Ta",
        "vanadium": "V",
        "cerium": "Ce",
        "lanthanum": "La",
        "yttrium": "Y",
    }
    
    # Valid ranges for properties (min, max) - for semantic validation
    PROPERTY_RANGES = {
        "yield_strength_mpa": (0.1, 2500),
        "ultimate_tensile_strength_mpa": (1, 3000),
        "elongation_percent": (0.05, 1000),
        "grain_size_um": (0.001, 1000),
        "hardness_hv": (5, 1500),
        "elastic_modulus_gpa": (1, 500),
        "density_g_per_cm3": (1, 25),
        "melting_temperature_c": (100, 4000),
        "composition_percent": (0, 100),
    }
    
    def __init__(self):
        """Initialize data normalizer."""
        logger.info("[NORMALIZER] Initialized")
    
    def normalize_value(
        self,
        value: Any,
        property_name: str,
        current_unit: Optional[str] = None
    ) -> NormalizationResult:
        """
        Normalize a single value with optional unit conversion.
        
        Args:
            value: The value to normalize
            property_name: Name of the property (for context)
            current_unit: Current unit if known
            
        Returns:
            NormalizationResult with normalized value and metadata
        """
        warnings = []
        
        # Handle None/empty values
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return NormalizationResult(value, None, current_unit, None, warnings=warnings)
        
        # Parse numeric value from string if needed
        if isinstance(value, str):
            parsed = self._parse_numeric_with_unit(value)
            if parsed:
                numeric_val, unit = parsed
                value = numeric_val
                if current_unit is None:
                    current_unit = unit
            else:
                # Can't parse as numeric
                return NormalizationResult(value, value, current_unit, None, warnings=warnings)
        
        # Convert to float if possible
        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            return NormalizationResult(value, value, current_unit, None, warnings=warnings)
        
        # Validate semantic range
        prop_key = property_name.lower()
        if prop_key in self.PROPERTY_RANGES:
            min_val, max_val = self.PROPERTY_RANGES[prop_key]
            if numeric_value < min_val or numeric_value > max_val:
                warnings.append(
                    f"Value {numeric_value} outside expected range [{min_val}, {max_val}] for {property_name}"
                )
        
        # Convert unit if needed
        target_unit = self._get_standard_unit(property_name)
        normalized_unit = current_unit
        conversion_factor = 1.0
        
        if current_unit and target_unit and current_unit.lower() != target_unit:
            conversion_result = self._convert_unit(numeric_value, current_unit, target_unit)
            if conversion_result:
                numeric_value, conversion_factor, normalized_unit = conversion_result
            else:
                warnings.append(f"Could not convert {current_unit} to {target_unit}")
        elif target_unit:
            normalized_unit = target_unit
        
        # Round to reasonable precision
        if 1 <= numeric_value <= 1000:
            normalized_value = round(numeric_value, 2)
        else:
            normalized_value = round(numeric_value, 3)
        
        return NormalizationResult(
            original_value=value,
            normalized_value=normalized_value,
            original_unit=current_unit,
            normalized_unit=normalized_unit,
            conversion_factor=conversion_factor,
            was_normalized=normalized_unit != current_unit or normalized_value != value,
            warnings=warnings
        )
    
    def normalize_material_name(self, name: str) -> str:
        """
        Normalize material name to standard format.
        
        Examples:
            "AZ-31B" -> "AZ31B"
            "AZ 31 B" -> "AZ31B"
            "Magnesium Alloy AZ31" -> "AZ31"
            "aluminum 7075" -> "Al7075"
        """
        if not name or not isinstance(name, str):
            return str(name)
        
        name = name.strip()
        original = name
        
        # Try pattern matching for known alloys
        for pattern, replacement in self.MATERIAL_PATTERNS.items():
            if re.search(pattern, name, re.IGNORECASE):
                if callable(replacement):
                    match = re.search(pattern, name, re.IGNORECASE)
                    name = replacement(match) if match else name
                else:
                    name = re.sub(pattern, replacement, name, flags=re.IGNORECASE)
                
                logger.info(f"[NORMALIZER] Normalized material name: '{original}' -> '{name}'")
                return name
        
        # Generic replacements
        name = re.sub(r'[-\s]+', '', name)  # Remove hyphens and spaces
        name = name.upper()
        
        logger.info(f"[NORMALIZER] Normalized material name: '{original}' -> '{name}'")
        return name
    
    def normalize_element_symbol(self, element: str) -> str:
        """
        Normalize element name to standard symbol.
        
        Examples:
            "aluminum" -> "Al"
            "ALUMINUM" -> "Al"
            "Al" -> "Al"
            "13" -> "Al" (atomic number)
        """
        if not element or not isinstance(element, str):
            return str(element)
        
        element = element.strip()
        original = element
        
        # Already a symbol (2 chars, first upper, second lower)?
        if len(element) == 2 and element[0].isupper() and element[1].islower():
            return element
        
        # Single uppercase letter with optional number?
        if len(element) <= 3 and element[0].isupper():
            if re.match(r'^[A-Z]+$', element):
                return element
        
        # Check element name map
        for full_name, symbol in self.ELEMENT_MAP.items():
            if element.lower() == full_name.lower():
                logger.info(f"[NORMALIZER] Normalized element: '{original}' -> '{symbol}'")
                return symbol
        
        # Try atomic number lookup
        try:
            atomic_num = int(element)
            # Simple atomic number to symbol map (limited)
            symbol_map = {1: "H", 6: "C", 7: "N", 8: "O", 13: "Al", 14: "Si", 15: "P", 16: "S",
                         12: "Mg", 30: "Zn", 26: "Fe", 25: "Mn", 29: "Cu", 22: "Ti", 24: "Cr",
                         28: "Ni", 42: "Mo", 74: "W", 23: "V", 27: "Co"}
            if atomic_num in symbol_map:
                symbol = symbol_map[atomic_num]
                logger.info(f"[NORMALIZER] Normalized atomic number: '{original}' -> '{symbol}'")
                return symbol
        except ValueError:
            pass
        
        # Return as-is if can't match
        logger.info(f"[NORMALIZER] Could not normalize element: '{original}'")
        return element
    
    def normalize_composition(self, composition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize entire composition dictionary.
        
        Args:
            composition: {element_symbol: percent_values}
            
        Returns:
            Normalized composition with standardized symbols and percentages
        """
        normalized = {}
        
        for element, percent in composition.items():
            # Normalize element symbol
            std_element = self.normalize_element_symbol(element)
            
            # Normalize percent value
            if isinstance(percent, str):
                # Remove % sign if present
                percent_str = percent.strip().rstrip('%')
                try:
                    percent_val = float(percent_str)
                except ValueError:
                    logger.warning(f"[NORMALIZER] Could not parse composition percent: '{percent}'")
                    continue
            else:
                percent_val = float(percent)
            
            # Validate range
            if percent_val < 0 or percent_val > 100:
                logger.warning(
                    f"[NORMALIZER] Composition percent out of range: {std_element}={percent_val}%"
                )
                continue
            
            normalized[std_element] = round(percent_val, 2)
        
        # Warn if doesn't sum to ~100%
        total = sum(normalized.values())
        if total > 0 and (total < 90 or total > 110):
            logger.warning(
                f"[NORMALIZER] Composition percentages sum to {total}% (expected ~100%)"
            )
        
        return normalized
    
    def normalize_all_properties(self, material_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize all properties in a material record.
        
        Args:
            material_record: Complete material record from consolidation agent
            
        Returns:
            Normalized material record
        """
        logger.info("[NORMALIZER] Normalizing all properties in material record")
        
        normalized = material_record.copy()
        
        # Normalize material name
        if "material_name" in normalized:
            normalized["material_name"] = self.normalize_material_name(normalized["material_name"])
        
        # Normalize composition
        if "composition" in normalized:
            comp = normalized["composition"]
            if isinstance(comp, dict) and "primary_elements" in comp:
                comp_dict = {}
                for elem_data in comp.get("primary_elements", []):
                    elem = elem_data.get("element", "")
                    pct = elem_data.get("percent")
                    std_elem = self.normalize_element_symbol(elem)
                    comp_dict[std_elem] = pct
                
                normalized_comp_dict = self.normalize_composition(comp_dict)
                comp["primary_elements"] = [
                    {"element": elem, "percent": pct, "unit": "wt%"}
                    for elem, pct in normalized_comp_dict.items()
                ]
        
        # Normalize properties
        if "properties" in normalized and isinstance(normalized["properties"], list):
            for prop_dict in normalized["properties"]:
                prop_names = [
                    "yield_strength_mpa", "ultimate_tensile_strength_mpa",
                    "elongation_percent", "grain_size_um", "hardness",
                    "elastic_modulus_gpa"
                ]
                
                for prop_name in prop_names:
                    if prop_name in prop_dict and prop_dict[prop_name] is not None:
                        result = self.normalize_value(
                            prop_dict[prop_name],
                            prop_name
                        )
                        prop_dict[prop_name] = result.normalized_value
        
        logger.info("[NORMALIZER] Normalization complete")
        return normalized
    
    def _parse_numeric_with_unit(self, value_str: str) -> Optional[Tuple[float, Optional[str]]]:
        """
        Parse a string like "170 MPa" into (170, "MPa").
        
        Returns:
            (numeric_value, unit) or None
        """
        # Pattern: optional sign, digits, optional decimal, optional space, optional unit
        match = re.match(r'^(-?\d+\.?\d*)\s*([A-Za-z%μ/°]*?)$', value_str.strip())
        
        if match:
            try:
                numeric = float(match.group(1))
                unit = match.group(2) or None
                return (numeric, unit)
            except ValueError:
                return None
        
        return None
    
    def _get_standard_unit(self, property_name: str) -> Optional[str]:
        """Get standard unit for a property."""
        prop_lower = property_name.lower()
        
        if "stress" in prop_lower or "strength" in prop_lower:
            return "MPa"
        elif "elongation" in prop_lower or "strain" in prop_lower:
            return "%"
        elif "grain" in prop_lower or "size" in prop_lower or "diameter" in prop_lower:
            return "μm"
        elif "modulus" in prop_lower:
            return "GPa"
        elif "hardness" in prop_lower:
            return "HV"
        elif "temp" in prop_lower:
            return "°C"
        elif "time" in prop_lower or "duration" in prop_lower:
            return "h"
        elif "composition" in prop_lower or "percent" in prop_lower:
            return "wt%"
        
        return None
    
    def _convert_unit(
        self,
        value: float,
        from_unit: str,
        to_unit: str
    ) -> Optional[Tuple[float, float, str]]:
        """
        Convert value from one unit to another.
        
        Returns:
            (converted_value, conversion_factor, target_unit) or None
        """
        if from_unit.lower() == to_unit.lower():
            return (value, 1.0, to_unit)
        
        from_key = from_unit.lower().replace("μ", "u").replace("°", "")
        
        if from_key in self.UNIT_CONVERSIONS:
            target, factor_or_func = self.UNIT_CONVERSIONS[from_key]
            
            if target.lower() == to_unit.lower():
                if callable(factor_or_func):
                    converted = factor_or_func(value)
                    return (converted, converted / value if value != 0 else 1.0, target)
                else:
                    converted = value * factor_or_func
                    return (converted, factor_or_func, target)
        
        logger.warning(f"[NORMALIZER] Could not convert {from_unit} to {to_unit}")
        return None
