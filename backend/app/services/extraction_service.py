"""Extraction service for PDF text and table extraction."""

import logging
import re
from pathlib import Path
from typing import Dict, Any, List

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class ExtractionService:
    """Service for PDF extraction and preprocessing."""
    
    # Common section headers in research papers
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
        """
        Extract text and section information from PDF using PyMuPDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extracted sections and text
        """
        try:
            logger.info(f"[EXTRACTION] Starting text extraction from: {pdf_path}")
            
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF not found: {pdf_path}")
            
            # Open PDF
            logger.info("[EXTRACTION] Opening PDF with PyMuPDF...")
            doc = fitz.open(str(pdf_path))
            logger.info(f"[EXTRACTION] PDF opened: {len(doc)} pages")
            
            # Extract text from all pages
            logger.info("[EXTRACTION] Extracting text from all pages...")
            pages = []
            full_text = ""
            
            for page_num, page in enumerate(doc):
                text = page.get_text()
                pages.append({
                    "page_num": page_num + 1,
                    "text": text
                })
                full_text += f"\n--- Page {page_num + 1} ---\n{text}"
            
            doc.close()
            
            # Split into sections
            logger.info("[EXTRACTION] Splitting text into sections...")
            sections = self._split_sections(full_text)
            
            result = {
                "text": full_text,
                "pages": pages,
                "sections": sections,
                "page_count": len(pages)
            }
            
            logger.info(f"[EXTRACTION] Text extraction completed: {len(sections)} sections found")
            return result
            
        except Exception as e:
            logger.error(f"[EXTRACTION] Error extracting text: {e}")
            raise
    
    def extract_tables(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extract tables from PDF (basic implementation using text patterns).
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extracted tables
        """
        try:
            logger.info(f"[EXTRACTION] Starting table extraction from: {pdf_path}")
            
            # For now, return empty tables as we focus on text extraction
            # Table extraction would require additional libraries like Camelot
            tables = []
            
            logger.info(f"[EXTRACTION] Table extraction completed: {len(tables)} tables found")
            return {"tables": tables, "table_count": len(tables)}
            
        except Exception as e:
            logger.error(f"[EXTRACTION] Error extracting tables: {e}")
            return {"tables": [], "table_count": 0}
    
    def extract_all(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extract all information from PDF (sections and tables).
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Combined extraction results
        """
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
    def _split_sections(text: str) -> Dict[str, str]:
        """
        Split text into sections based on common headers.
        
        Args:
            text: Full document text
            
        Returns:
            Dictionary with section names as keys and section text as values
        """
        sections = {}
        lines = text.split("\n")
        current_section = "preamble"
        current_text = []
        
        for line in lines:
            # Check if line matches any section header
            section_found = False
            for section_name, pattern in ExtractionService.SECTION_PATTERNS.items():
                if re.match(pattern, line.strip()):
                    # Save previous section
                    if current_section and current_text:
                        sections[current_section] = "\n".join(current_text).strip()
                    
                    # Start new section
                    current_section = section_name
                    current_text = []
                    section_found = True
                    break
            
            if not section_found and line.strip():
                current_text.append(line)
        
        # Save final section
        if current_section and current_text:
            sections[current_section] = "\n".join(current_text).strip()
        
        logger.debug(f"[EXTRACTION] Sections found: {list(sections.keys())}")
        return sections

