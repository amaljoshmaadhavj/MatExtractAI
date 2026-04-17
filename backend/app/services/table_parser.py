"""Advanced table parsing and structure extraction from PDF content."""

import logging
import re
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TableCell:
    """Represents a single cell in a table."""
    value: str
    row: int
    column: int
    is_header: bool = False
    is_merged: bool = False
    data_type: str = "string"  # string, numeric, unit, enum


@dataclass
class ExtractedTable:
    """Represents a fully parsed table."""
    table_id: str
    page_number: int
    caption: str
    headers: List[str]
    rows: List[Dict[str, Any]]
    column_types: Dict[str, str]
    cell_count: int
    row_count: int
    column_count: int
    confidence: float
    source: str
    extraction_method: str
    notes: List[str]


class TableParser:
    """
    Advanced table parsing from PDF content.
    Handles both structured and semi-structured tables.
    """
    
    # Materials science relevant keywords for column detection
    MECHANICAL_KEYWORDS = {
        r"yield.*strength|YS|σ_y|σy": "yield_strength",
        r"tensile.*strength|UTS|ultimate|σ_u|σu|σ_m": "ultimate_tensile_strength",
        r"elongation|EL|ductility|δ": "elongation",
        r"hardness|HV|HB|hardness.*value": "hardness",
        r"elastic.*modulus|young.*modulus|E\s*\(|modulus": "elastic_modulus",
        r"grain.*size|GS|μm|grain": "grain_size",
    }
    
    UNIT_PATTERNS = {
        r"MPa|GPa|Pa": "stress",
        r"%|percent|elongation": "percentage",
        r"μm|nm|mm|um": "length",
        r"°C|°F|K|kelvin": "temperature",
        r"h|hr|hours|minutes|s|sec": "time",
        r"wt%|at%|mol%|mole": "composition",
    }
    
    def __init__(self):
        """Initialize table parser."""
        logger.info("[TABLE-PARSER] Initialized")
    
    def parse_tables_from_text(self, text: str, page_number: int = 0) -> List[ExtractedTable]:
        """
        Parse tables from text content extracted from PDF.
        
        Args:
            text: Full text content from page or section
            page_number: Page number for attribution
            
        Returns:
            List of ExtractedTable objects
        """
        logger.info(f"[TABLE-PARSER] Parsing tables from text ({len(text)} chars)")
        
        tables = []
        
        # Strategy 1: Look for tabulated data (aligned columns)
        tabulated = self._parse_tabulated_data(text, page_number)
        tables.extend(tabulated)
        
        # Strategy 2: Look for comma/tab-separated values
        csv_like = self._parse_csv_like_data(text, page_number)
        tables.extend(csv_like)
        
        # Strategy 3: Look for pipe-delimited tables
        pipe_delim = self._parse_pipe_delimited(text, page_number)
        tables.extend(pipe_delim)
        
        # Strategy 4: Look for structured data patterns (e.g., "Property: Value" pairs)
        structured = self._parse_structured_pairs(text, page_number)
        tables.extend(structured)
        
        logger.info(f"[TABLE-PARSER] Found {len(tables)} table(s)")
        return tables
    
    def _parse_tabulated_data(self, text: str, page_number: int) -> List[ExtractedTable]:
        """
        Parse tables where rows are space/tab-aligned.
        Example:
            Material    YS (MPa)   UTS (MPa)
            AZ31        170        250
            AZ91        230        330
        """
        tables = []
        lines = text.split('\n')
        
        # Find lines that look like table rows (multiple space-separated values with numbers)
        table_blocks = self._find_table_blocks(lines)
        
        for block_idx, (start_idx, end_idx) in enumerate(table_blocks):
            block_lines = lines[start_idx:end_idx + 1]
            
            # Try to parse as table
            table = self._parse_block_as_table(block_lines, page_number, f"Table_{block_idx + 1}")
            if table and len(table.rows) > 0:
                table.extraction_method = "tabulated_alignment"
                tables.append(table)
                logger.info(f"[TABLE-PARSER] Parsed tabulated table with {table.row_count} rows, {table.column_count} cols")
        
        return tables
    
    def _find_table_blocks(self, lines: List[str]) -> List[Tuple[int, int]]:
        """Find contiguous blocks of lines that look like tables."""
        blocks = []
        current_block_start = None
        
        for idx, line in enumerate(lines):
            # Check if line looks like it contains tabular data
            if self._looks_like_table_row(line):
                if current_block_start is None:
                    current_block_start = idx
            else:
                if current_block_start is not None:
                    # End of block
                    if idx - current_block_start >= 2:  # At least 2 rows
                        blocks.append((current_block_start, idx - 1))
                    current_block_start = None
        
        # Don't forget last block
        if current_block_start is not None and len(lines) - current_block_start >= 2:
            blocks.append((current_block_start, len(lines) - 1))
        
        return blocks
    
    def _looks_like_table_row(self, line: str) -> bool:
        """Heuristic: does this line look like a table row?"""
        if not line or len(line.strip()) < 5:
            return False
        
        # Should have multiple space-separated parts
        parts = line.split()
        if len(parts) < 2:
            return False
        
        # Check if contains some numbers or material keywords
        has_number = any(re.search(r'\d+\.?\d*', part) for part in parts)
        has_material_keyword = any(
            re.search(keyword, line, re.IGNORECASE)
            for keyword in ['mg', 'al', 'zn', 'ti', 'fe', 'cu', 'ni', 'az', 'am', 'alloy', 'steel']
        )
        
        return has_number or has_material_keyword
    
    def _parse_csv_like_data(self, text: str, page_number: int) -> List[ExtractedTable]:
        """Parse comma or semicolon-separated table data."""
        tables = []
        lines = text.split('\n')
        
        table_blocks = []
        current_block = []
        
        for line in lines:
            # Check if line is CSV-like (comma or semicolon separated)
            if self._looks_like_csv_row(line):
                current_block.append(line)
            else:
                if len(current_block) >= 2:
                    table_blocks.append(current_block)
                current_block = []
        
        if len(current_block) >= 2:
            table_blocks.append(current_block)
        
        for block_idx, block_lines in enumerate(table_blocks):
            table = self._parse_csv_block(block_lines, page_number, f"Table_{block_idx + 1}")
            if table and len(table.rows) > 0:
                table.extraction_method = "csv_delimited"
                tables.append(table)
                logger.info(f"[TABLE-PARSER] Parsed CSV-like table with {table.row_count} rows")
        
        return tables
    
    def _looks_like_csv_row(self, line: str) -> bool:
        """Does this line look like CSV data?"""
        if not line:
            return False
        
        # Count separators
        commas = line.count(',')
        semicolons = line.count(';')
        separators = commas + semicolons
        
        # Should have multiple separators
        return separators >= 2
    
    def _parse_csv_block(self, lines: List[str], page_number: int, table_id: str) -> Optional[ExtractedTable]:
        """Parse a block of CSV-like lines into a table."""
        try:
            # Determine separator
            first_line = lines[0]
            separator = ',' if first_line.count(',') > first_line.count(';') else ';'
            
            # Parse all rows
            rows = []
            headers = None
            
            for row_idx, line in enumerate(lines):
                parts = [p.strip() for p in line.split(separator)]
                
                if row_idx == 0:
                    # Assume first row is header if it contains non-numeric values
                    if self._looks_like_header(parts):
                        headers = parts
                        continue
                
                # Parse as data row
                if headers:
                    row_dict = {h: p for h, p in zip(headers, parts)}
                else:
                    row_dict = {f"col_{i}": p for i, p in enumerate(parts)}
                
                rows.append(row_dict)
            
            if not headers:
                headers = list(rows[0].keys()) if rows else []
            
            if not rows or not headers:
                return None
            
            # Infer column types
            column_types = self._infer_column_types(rows, headers)
            
            return ExtractedTable(
                table_id=table_id,
                page_number=page_number,
                caption=table_id,
                headers=headers,
                rows=rows,
                column_types=column_types,
                cell_count=len(headers) * len(rows),
                row_count=len(rows),
                column_count=len(headers),
                confidence=0.75,
                source=f"Page {page_number}",
                extraction_method="csv_delimited",
                notes=["CSV-like format detected"]
            )
        
        except Exception as e:
            logger.warning(f"[TABLE-PARSER] Failed to parse CSV block: {e}")
            return None
    
    def _parse_pipe_delimited(self, text: str, page_number: int) -> List[ExtractedTable]:
        """Parse tables delimited with pipes (|)."""
        tables = []
        lines = text.split('\n')
        
        current_block = []
        for line in lines:
            if '|' in line:
                current_block.append(line)
            else:
                if len(current_block) >= 2:
                    table = self._parse_pipe_block(current_block, page_number, f"Table_{len(tables) + 1}")
                    if table and len(table.rows) > 0:
                        table.extraction_method = "pipe_delimited"
                        tables.append(table)
                current_block = []
        
        if len(current_block) >= 2:
            table = self._parse_pipe_block(current_block, page_number, f"Table_{len(tables) + 1}")
            if table and len(table.rows) > 0:
                table.extraction_method = "pipe_delimited"
                tables.append(table)
        
        return tables
    
    def _parse_pipe_block(self, lines: List[str], page_number: int, table_id: str) -> Optional[ExtractedTable]:
        """Parse pipe-delimited table block."""
        try:
            rows = []
            headers = None
            
            for row_idx, line in enumerate(lines):
                # Remove outer pipes and split
                clean_line = line.strip('|').strip()
                parts = [p.strip() for p in clean_line.split('|')]
                
                # Skip separator rows (all dashes)
                if all(re.match(r'^-+$', p) for p in parts):
                    continue
                
                if row_idx == 0 or headers is None:
                    if self._looks_like_header(parts):
                        headers = parts
                        continue
                
                if headers:
                    row_dict = {h: p for h, p in zip(headers, parts)}
                else:
                    row_dict = {f"col_{i}": p for i, p in enumerate(parts)}
                
                rows.append(row_dict)
            
            if not headers:
                headers = list(rows[0].keys()) if rows else []
            
            if not rows or not headers:
                return None
            
            column_types = self._infer_column_types(rows, headers)
            
            return ExtractedTable(
                table_id=table_id,
                page_number=page_number,
                caption=table_id,
                headers=headers,
                rows=rows,
                column_types=column_types,
                cell_count=len(headers) * len(rows),
                row_count=len(rows),
                column_count=len(headers),
                confidence=0.80,
                source=f"Page {page_number}",
                extraction_method="pipe_delimited",
                notes=["Pipe-delimited format"]
            )
        
        except Exception as e:
            logger.warning(f"[TABLE-PARSER] Failed to parse pipe block: {e}")
            return None
    
    def _parse_structured_pairs(self, text: str, page_number: int) -> List[ExtractedTable]:
        """Parse 'Property: Value' style data structures."""
        tables = []
        
        # Pattern: "Property: Value" or "Property = Value"
        pattern = r'([A-Za-z\s\d()]+?)[\s]*[:\=]\s*([^\n]+)'
        matches = re.findall(pattern, text)
        
        if len(matches) >= 3:  # At least 3 properties to form a "table"
            row_dict = {}
            for prop_name, prop_value in matches:
                prop_name = prop_name.strip()
                prop_value = prop_value.strip()
                if prop_name and prop_value:
                    row_dict[prop_name] = prop_value
            
            if row_dict:
                table = ExtractedTable(
                    table_id="Table_Structured",
                    page_number=page_number,
                    caption="Structured Property Table",
                    headers=list(row_dict.keys()),
                    rows=[row_dict],
                    column_types=self._infer_column_types([row_dict], list(row_dict.keys())),
                    cell_count=len(row_dict),
                    row_count=1,
                    column_count=len(row_dict),
                    confidence=0.65,
                    source=f"Page {page_number}",
                    extraction_method="structured_pairs",
                    notes=["Structured property pairs detected"]
                )
                tables.append(table)
        
        return tables
    
    def _parse_block_as_table(self, lines: List[str], page_number: int, table_id: str) -> Optional[ExtractedTable]:
        """Parse a block of lines as a table with space-aligned columns."""
        try:
            if len(lines) < 2:
                return None
            
            # Find column boundaries by analyzing whitespace
            col_boundaries = self._find_column_boundaries(lines)
            
            if len(col_boundaries) < 2:
                return None
            
            # Extract columns from each line
            rows = []
            headers = None
            
            for row_idx, line in enumerate(lines):
                values = self._extract_columns(line, col_boundaries)
                
                if row_idx == 0:
                    if self._looks_like_header(values):
                        headers = values
                        continue
                
                if headers:
                    row_dict = {h: v for h, v in zip(headers, values)}
                else:
                    row_dict = {f"col_{i}": v for i, v in enumerate(values)}
                
                rows.append(row_dict)
            
            if not headers and rows:
                headers = list(rows[0].keys())
            
            if not rows or not headers:
                return None
            
            column_types = self._infer_column_types(rows, headers)
            
            return ExtractedTable(
                table_id=table_id,
                page_number=page_number,
                caption=table_id,
                headers=headers,
                rows=rows,
                column_types=column_types,
                cell_count=len(headers) * len(rows),
                row_count=len(rows),
                column_count=len(headers),
                confidence=0.78,
                source=f"Page {page_number}",
                extraction_method="space_aligned",
                notes=[f"Detected {len(col_boundaries) - 1} columns"]
            )
        
        except Exception as e:
            logger.warning(f"[TABLE-PARSER] Failed to parse block as table: {e}")
            return None
    
    def _find_column_boundaries(self, lines: List[str]) -> List[int]:
        """Find column boundaries by finding consistent spacing patterns."""
        if not lines:
            return []
        
        # Analyze first few lines to find column boundaries
        sample_lines = lines[:min(3, len(lines))]
        
        # Find positions where most lines have space (column boundary)
        boundaries = {0}  # Start boundary
        
        for pos in range(1, max(len(line) for line in sample_lines)):
            space_count = sum(1 for line in sample_lines if pos < len(line) and line[pos] == ' ')
            if space_count >= len(sample_lines) * 0.7:  # 70% of sample has space
                boundaries.add(pos)
        
        boundaries.add(max(len(line) for line in sample_lines))
        
        return sorted(list(boundaries))
    
    def _extract_columns(self, line: str, boundaries: List[int]) -> List[str]:
        """Extract column values from a line using boundaries."""
        values = []
        for i in range(len(boundaries) - 1):
            start = boundaries[i]
            end = boundaries[i + 1]
            value = line[start:end].strip() if start < len(line) else ""
            if value:
                values.append(value)
        return values
    
    def _looks_like_header(self, values: List[str]) -> bool:
        """Heuristic: do these values look like table headers?"""
        if not values:
            return False
        
        # Headers are often:
        # - Short text (< 30 chars)
        # - Don't contain many numbers alone
        # - Contain known column name keywords
        
        short_count = sum(1 for v in values if len(v) < 30)
        numeric_count = sum(1 for v in values if re.match(r'^\d+\.?\d*$', v))
        keyword_count = sum(1 for v in values if any(
            keyword in v.lower() for keyword in 
            ['material', 'alloy', 'strength', 'modulus', 'hardness', 'grain', 'size', 'temp', 'time', 'test']
        ))
        
        # Likely header if: mostly short, some keywords, not mostly numbers
        return short_count >= len(values) * 0.7 or keyword_count > 0
    
    def _infer_column_types(self, rows: List[Dict[str, Any]], headers: List[str]) -> Dict[str, str]:
        """Infer data type for each column."""
        column_types = {}
        
        for header in headers:
            # Collect all values in this column
            values = [row.get(header, "") for row in rows]
            
            # Determine type
            col_type = self._infer_type(values, header)
            column_types[header] = col_type
        
        return column_types
    
    def _infer_type(self, values: List[str], header: str) -> str:
        """Infer type of a column based on values and header."""
        # Check header keywords first
        header_lower = header.lower()
        
        for pattern, unit_type in self.UNIT_PATTERNS.items():
            if re.search(pattern, header_lower):
                return f"numeric_{unit_type}"
        
        # Check value patterns
        numeric_count = 0
        for v in values:
            if v and re.match(r'^-?\d+\.?\d*\s*[A-Za-z%]*$', v):
                numeric_count += 1
        
        if numeric_count >= len(values) * 0.8:
            return "numeric"
        
        return "string"
