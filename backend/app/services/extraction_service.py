"""Extraction service for PDF text and table extraction."""

import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class ExtractionService:
    """Service for PDF extraction and preprocessing."""
    
    SECTION_PATTERNS = {
        "abstract": r"(?i)^(abstract)",
        "introduction": r"(?i)^(introduction|background)",
        "methods": r"(?i)^(methods|methodology|experimental|materials and methods)",
        "results": r"(?i)^(results|findings)",
        "discussion": r"(?i)^(discussion)",
        "conclusion": r"(?i)^(conclusion|conclusions)",
        "references": r"(?i)^(references|bibliography)",
        "materials": r"(?i)^(materials|materials and microstructures)"
    }
    
    def __init__(self):
        """Initialize extraction service."""
        logger.info("[EXTRACTION] Extraction service initialized with PyMuPDF")
    
    def extract_text_and_sections(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract text and section information from PDF using PyMuPDF."""
        try:
            logger.info(f"[EXTRACTION] Starting text extraction from: {pdf_path}")
            
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF not found: {pdf_path}")
            
            logger.info("[EXTRACTION] Opening PDF with PyMuPDF...")
            doc = fitz.open(str(pdf_path))
            logger.info(f"[EXTRACTION] PDF opened: {len(doc)} pages")
            
            pages = []
            full_text = ""
            page_locations = []
            
            for page_num, page in enumerate(doc):
                text = page.get_text()
                pages.append({
                    "page_num": page_num + 1,
                    "text": text,
                    "page_index": page_num
                })
                
                page_start = len(full_text)
                full_text += f"\n--- Page {page_num + 1} ---\n{text}"
                page_locations.append({
                    "page_num": page_num + 1,
                    "start_pos": page_start,
                    "end_pos": len(full_text),
                    "text_length": len(text)
                })
            
            doc.close()
            
            logger.info("[EXTRACTION] Splitting text into sections...")
            sections = self._split_sections(full_text, page_locations)
            
            result = {
                "text": full_text,
                "pages": pages,
                "sections": sections,
                "page_count": len(pages),
                "page_locations": page_locations,
                "extraction_timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"[EXTRACTION] Text extraction completed: {len(sections)} sections found")
            return result
            
        except Exception as e:
            logger.error(f"[EXTRACTION] Error extracting text: {e}")
            raise
    
    def extract_tables(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract tables from PDF using PyMuPDF and text pattern analysis."""
        try:
            logger.info(f"[EXTRACTION] Starting table extraction from: {pdf_path}")
            
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF not found: {pdf_path}")
            
            doc = fitz.open(str(pdf_path))
            tables = []
            table_id = 1
            
            for page_num, page in enumerate(doc):
                text = page.get_text()
                detected_tables = self._detect_table_patterns(text, page_num + 1)
                
                for table_text, context in detected_tables:
                    parsed_table = self._parse_table_structure(table_text)
                    
                    if parsed_table and len(parsed_table) > 1:
                        tables.append({
                            "table_id": f"Table_{table_id}",
                            "page_num": page_num + 1,
                            "caption": f"Table {table_id}",
                            "headers": parsed_table[0] if parsed_table else [],
                            "rows": parsed_table[1:] if len(parsed_table) > 1 else [],
                            "row_count": len(parsed_table) - 1,
                            "column_count": len(parsed_table[0]) if parsed_table else 0,
                            "context": context[:100],
                            "source": f"Page {page_num + 1}",
                            "extraction_method": "text_pattern_analysis"
                        })
                        table_id += 1
            
            doc.close()
            
            logger.info(f"[EXTRACTION] Table extraction completed: {len(tables)} tables found")
            return {
                "tables": tables,
                "table_count": len(tables),
                "extraction_status": "success"
            }
            
        except Exception as e:
            logger.error(f"[EXTRACTION] Error extracting tables: {e}")
            return {
                "tables": [],
                "table_count": 0,
                "extraction_status": "error",
                "error": str(e)
            }
    
    def extract_all(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract all information from PDF (sections and tables)."""
        try:
            sections_result = self.extract_text_and_sections(pdf_path)
            tables_result = self.extract_tables(pdf_path)
            
            return {
                **sections_result,
                **tables_result,
                "extraction_status": "success"
            }
        except Exception as e:
            logger.error(f"[EXTRACTION] Error in complete extraction: {e}")
            return {
                "extraction_status": "failed",
                "error": str(e)
            }
    
    @staticmethod
    def _split_sections(text: str, page_locations: list = None) -> Dict[str, str]:
        """Split text into sections based on common headers."""
        sections = {}
        lines = text.split("\n")
        current_section = "preamble"
        current_text = []
        found_sections = set()
        
        for line in lines:
            section_found = False
            line_stripped = line.strip()
            
            # Try to match section headers
            for section_name, pattern in ExtractionService.SECTION_PATTERNS.items():
                # Use search instead of match to find patterns anywhere in the line
                if re.search(pattern, line_stripped) and len(line_stripped) < 100:  # Header lines are usually short
                    if current_section and current_text:
                        sections[current_section] = "\n".join(current_text).strip()
                    
                    current_section = section_name
                    found_sections.add(section_name)
                    current_text = []
                    section_found = True
                    logger.debug(f"[EXTRACTION] Found section header: '{line_stripped}' -> {section_name}")
                    break
            
            if not section_found and line_stripped:
                current_text.append(line)
        
        if current_section and current_text:
            sections[current_section] = "\n".join(current_text).strip()
        
        logger.info(f"[EXTRACTION] Sections found: {list(sections.keys())}")
        logger.info(f"[EXTRACTION] Section sizes: " + ", ".join([f"{k}:{len(v)} chars" for k, v in sections.items()]))
        
        # Fallback: if results section is empty, try to extract from full text
        if not sections.get("results") or len(sections.get("results", "")) < 50:
            # Look for common result indicators
            result_indicators = ["result", "finding", "outcome", "observation", "data", "experiment"]
            full_text_lower = text.lower()
            
            # Find positions of these indicators
            for indicator in result_indicators:
                idx = full_text_lower.find(indicator)
                if idx != -1:
                    # Extract content after this indicator
                    start_pos = max(0, idx)
                    # Find next section or end of text
                    next_section_idx = len(text)
                    for section_name in ["discussion", "conclusion", "references"]:
                        pattern = ExtractionService.SECTION_PATTERNS.get(section_name, "")
                        match = re.search(pattern, text[start_pos:].lower())
                        if match:
                            next_section_idx = min(next_section_idx, start_pos + match.start())
                    
                    potential_results = text[start_pos:next_section_idx].strip()
                    if len(potential_results) > len(sections.get("results", "")):
                        sections["results"] = potential_results
                        logger.info(f"[EXTRACTION] Fallback: Found results section using '{indicator}' indicator")
                        break
        
        return sections
    
    @staticmethod
    def _detect_table_patterns(text: str, page_num: int) -> List[Tuple[str, str]]:
        """Detect table-like patterns in text (multiple aligned columns)."""
        tables = []
        lines = text.split("\n")
        
        # Look for lines that contain table headers or numeric data patterns
        # Tables often have headers followed by rows of data
        potential_table_starts = []
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Table indicators: contains multiple words separated by spaces, 
            # or lines with numbers and units (MPa, μm, %, GPA, etc)
            has_multiple_fields = len(line_stripped.split()) >= 3
            has_numeric_pattern = bool(re.search(r'(\d+\.?\d*\s*(?:MPa|GPA|%|μm|HV|Mpa|°C|h|mm))', line_stripped, re.IGNORECASE))
            has_table_separators = bool(re.search(r'[\|\-\+]{2,}', line))
            looks_like_header = any(keyword in line_stripped.lower() for keyword in 
                                   ['material', 'stress', 'strain', 'strength', 'yield', 
                                    'tensile', 'hardness', 'temperature', 'cycles', 'elongation',
                                    'parameter', 'property', 'value', 'result', 'data'])
            
            if (has_multiple_fields and (has_numeric_pattern or has_table_separators or looks_like_header)):
                potential_table_starts.append((i, line_stripped))
        
        if potential_table_starts:
            current_table_lines = []
            last_idx = -5
            
            for idx, line in potential_table_starts:
                if idx - last_idx <= 3:  # Lines are close together (same table)
                    current_table_lines.append(line)
                else:  # Gap found - save current table and start new one
                    if len(current_table_lines) >= 2:
                        table_text = "\n".join(current_table_lines)
                        context_idx = max(0, potential_table_starts[0][0] - 2)
                        context = "\n".join(lines[context_idx:context_idx+2])
                        tables.append((table_text, context))
                        logger.info(f"[EXTRACTION] Detected table: {len(current_table_lines)} rows")
                    current_table_lines = [line]
                last_idx = idx
            
            # Don't forget the last table
            if len(current_table_lines) >= 2:
                table_text = "\n".join(current_table_lines)
                context_idx = max(0, potential_table_starts[-1][0] - 2)
                context = "\n".join(lines[context_idx:min(context_idx+2, len(lines))])
                tables.append((table_text, context))
                logger.info(f"[EXTRACTION] Detected final table: {len(current_table_lines)} rows")
        
        logger.info(f"[EXTRACTION] Found {len(tables)} table(s)")
        return tables
    
    @staticmethod
    def _parse_table_structure(table_text: str) -> List[List[str]]:
        """Parse table text into structured rows and columns."""
        rows = []
        lines = table_text.strip().split("\n")
        
        for line in lines:
            if line.strip():
                columns = re.split(r'\s{2,}', line.strip())
                columns = [col.strip() for col in columns if col.strip()]
                if columns:
                    rows.append(columns)
        
        return rows
