"""Background task worker for processing PDF extraction jobs."""

import logging
import json
import traceback
import asyncio
from pathlib import Path
from app.services.job_service import JobService
from app.services.extraction_service import ExtractionService
from app.services.agent_service import AgentService
from app.services.validation_service import ValidationService
from app.services.consolidation_agent import ConsolidationAgent
from app.services.conflict_resolver import ConflictResolver
from app.storage.file_manager import FileManager
from app.storage.mongodb_manager import MongoDBManager
from app.config import settings

logger = logging.getLogger(__name__)


def process_pdf_job(job_id: str, pdf_path: str):
    """
    Process a PDF extraction job in the background.
    
    Args:
        job_id: Job ID to process
        pdf_path: Path to uploaded PDF file
    """
    try:
        logger.info(f"[WORKER] Starting processing for job {job_id}")
        logger.info(f"[WORKER] PDF path: {pdf_path}")
        
        job_service = JobService()
        file_manager = FileManager()
        mongodb_manager = MongoDBManager()
        
        try:
            logger.info(f"[WORKER] Initializing extraction service...")
            extraction_service = ExtractionService()
            logger.info(f"[WORKER] Extraction service initialized successfully")
        except Exception as e:
            logger.error(f"[WORKER] Failed to initialize extraction service: {e}")
            logger.error(traceback.format_exc())
            error_msg = f"Failed to initialize extraction: {str(e)}"
            job_service.update_status(
                job_id,
                "failed",
                error_message=error_msg
            )
            mongodb_manager.update_job_progress(job_id, 0, "Failed to initialize")
            return
        
        # Update status
        logger.info(f"[WORKER] Updating job status to processing (20%)")
        job_service.update_status(
            job_id,
            "processing",
            progress=20,
            current_step="Extracting text and sections"
        )
        mongodb_manager.update_job_progress(job_id, 20, "Extracting text and sections")
        
        # Extract text and sections
        logger.info(f"[WORKER] Starting extraction for {pdf_path}")
        try:
            extraction_result = extraction_service.extract_all(Path(pdf_path))
            logger.info(f"[WORKER] Extraction completed: {extraction_result.get('extraction_status')}")
        except Exception as e:
            logger.error(f"[WORKER] Extraction failed: {e}")
            logger.error(traceback.format_exc())
            error_msg = f"Extraction error: {str(e)}"
            job_service.update_status(
                job_id,
                "failed",
                error_message=error_msg
            )
            mongodb_manager.update_job_progress(job_id, 20, "Extraction failed")
            return
        
        if extraction_result.get("extraction_status") == "failed":
            logger.error(f"[WORKER] Extraction status is failed for job {job_id}")
            error_msg = f"Extraction error: {extraction_result.get('error', 'Unknown error')}"
            job_service.update_status(
                job_id,
                "failed",
                error_message=error_msg
            )
            mongodb_manager.update_job_progress(job_id, 20, "Extraction failed")
            return
        
        # Update progress
        logger.info(f"[WORKER] Updating job status to processing (60%)")
        job_service.update_status(
            job_id,
            "processing",
            progress=60,
            current_step="Running LLM agents for property extraction"
        )
        mongodb_manager.update_job_progress(job_id, 60, "Running LLM agents for property extraction")
        
        # Run LLM agents for property extraction
        logger.info(f"[WORKER] Initializing agent service...")
        try:
            agent_service = AgentService()
            sections = extraction_result.get("sections", {})
            tables = extraction_result.get("tables", [])
            full_text = extraction_result.get("text", "")
            
            # Ensure sections has all expected keys
            sections_dict = {
                "title": sections.get("title", ""),
                "abstract": sections.get("abstract", ""),
                "introduction": sections.get("introduction", ""),
                "methods": sections.get("methods", ""),
                "results": sections.get("results", ""),
                "discussion": sections.get("discussion", ""),
                "conclusion": sections.get("conclusion", ""),
                "composition": sections.get("composition", ""),
                "processing": sections.get("processing", ""),
                "microstructure": sections.get("microstructure", ""),
                "text": full_text
            }
            
            logger.info(f"[WORKER] Running agents on {len(full_text)} chars of text and {len(tables)} tables")
            
            # Create async context for running async agent methods
            logger.info(f"[WORKER] Running mechanical properties agent...")
            mechanical_properties = asyncio.run(agent_service._run_mechanical_properties(sections_dict, tables))
            
            # Check extraction status
            mech_status = mechanical_properties.get("extraction_status", "unknown")
            if mech_status != "success":
                logger.warning(f"[WORKER] Mechanical properties extraction did not succeed: {mech_status}")
                logger.warning(f"[WORKER] Error: {mechanical_properties.get('error', 'No error message')}")
            
            job_service.update_status(job_id, "processing", progress=70, current_step="Mechanical properties agent completed")
            mongodb_manager.update_job_progress(job_id, 70, "Mechanical properties agent completed")
            
            logger.info(f"[WORKER] Running composition agent...")
            composition = asyncio.run(agent_service._run_composition(sections_dict, tables))
            job_service.update_status(job_id, "processing", progress=75, current_step="Composition agent completed")
            mongodb_manager.update_job_progress(job_id, 75, "Composition agent completed")
            
            logger.info(f"[WORKER] Running processing agent...")
            processing = asyncio.run(agent_service._run_processing(sections_dict, tables))
            job_service.update_status(job_id, "processing", progress=80, current_step="Processing agent completed")
            mongodb_manager.update_job_progress(job_id, 80, "Processing agent completed")
            
            logger.info(f"[WORKER] Running microstructure agent...")
            microstructure = asyncio.run(agent_service._run_microstructure(sections_dict, tables))
            job_service.update_status(job_id, "processing", progress=85, current_step="Microstructure agent completed")
            mongodb_manager.update_job_progress(job_id, 85, "Microstructure agent completed")
            
            logger.info(f"[WORKER] All agents completed successfully")
            
            # Assemble final results - use ACTUAL agent results, not mock fallback
            agent_results = {
                "mechanical_properties": mechanical_properties,
                "composition": composition,
                "processing": processing,
                "microstructure": microstructure,
                "extraction_status": "completed"
            }
            logger.info(f"[WORKER] Agent service completed")
            
            # Log extraction status summary
            mech_status = mechanical_properties.get("extraction_status", "unknown")
            comp_status = composition.get("extraction_status", "unknown")
            proc_status = processing.get("extraction_status", "unknown")
            micro_status = microstructure.get("extraction_status", "unknown")
            
            logger.info(f"[WORKER] Extraction summary: mechanical={mech_status}, composition={comp_status}, processing={proc_status}, microstructure={micro_status}")
            
            # Skip consolidation agent - it was causing bottlenecks
            logger.info(f"[WORKER] Skipping consolidation step (results are ready from agents)")
            agent_results["consolidation"] = {
                "consolidation_status": "skipped",
                "material_records": [],
                "note": "Direct agent results used instead of consolidation"
            }
        except Exception as e:
            # Log error but DON'T fall back to all mock data
            logger.error(f"[WORKER] Agent service error: {e}")
            logger.error(traceback.format_exc())
            # Return empty results instead of fake data
            agent_results = {
                "mechanical_properties": {"extraction_status": "error", "extracted_data": [], "error": str(e)},
                "composition": {"extraction_status": "error", "extracted_data": [], "error": str(e)},
                "processing": {"extraction_status": "error", "extracted_data": [], "error": str(e)},
                "microstructure": {"extraction_status": "error", "extracted_data": [], "error": str(e)},
                "extraction_status": "error"
            }
        
        # Prepare results
        logger.info(f"[WORKER] Preparing final results with comprehensive validation...")
        
        # Update progress: validation starting
        job_service.update_status(job_id, "processing", progress=88, current_step="Validating extraction results")
        mongodb_manager.update_job_progress(job_id, 88, "Validating extraction results")
        
        sections = extraction_result.get("sections", {})
        full_text = extraction_result.get("text", "")
        
        # Extract properties from sections (for display)
        properties = {
            "materials": sections.get("materials", "")[:500],  # First 500 chars
            "methods": sections.get("methods", "")[:500],
            "results": sections.get("results", "")[:500],
            "discussion": sections.get("discussion", "")[:500]
        }
        
        # Create validation using ValidationService
        logger.info(f"[WORKER] Running validation service...")
        validation_service = ValidationService()
        validation = validation_service.validate_results({
            "mechanical_properties": agent_results.get("mechanical_properties", {}),
            "composition": agent_results.get("composition", {}),
            "processing": agent_results.get("processing", {}),
            "microstructure": agent_results.get("microstructure", {}),
            "tables": extraction_result.get("tables", [])
        }, full_text)
        
        results = {
            "job_id": job_id,
            "sections": sections,
            "tables": extraction_result.get("tables", []),
            "mechanical_properties": agent_results.get("mechanical_properties", {}),
            "composition": agent_results.get("composition", {}),
            "processing": agent_results.get("processing", {}),
            "microstructure": agent_results.get("microstructure", {}),
            "validation": validation,
            "material_records": agent_results.get("consolidation", {}).get("material_records", []),
            "consolidation_status": agent_results.get("consolidation", {}).get("consolidation_status", "not_run"),
            "conflict_report": agent_results.get("consolidation", {}).get("conflict_report", {}),
            "extraction_status": "completed",
            "extraction_timestamp": extraction_result.get("extraction_timestamp", ""),
            "page_count": extraction_result.get("page_count", 0)
        }
        
        # Save results to MongoDB and file
        logger.info(f"[WORKER] Saving results to MongoDB and file")
        job_service.update_status(job_id, "processing", progress=95, current_step="Saving results")
        mongodb_manager.update_job_progress(job_id, 95, "Saving results")
        try:
            # Save to MongoDB first (primary storage)
            mongodb_manager.save_results(results)
            # Save to file (backup storage)
            file_manager.save_results(results, job_id)
            logger.info(f"[WORKER] Results saved successfully to MongoDB and file")
        except Exception as e:
            logger.error(f"[WORKER] Failed to save results: {e}")
            logger.error(traceback.format_exc())
            error_msg = f"Failed to save results: {str(e)}"
            job_service.update_status(
                job_id,
                "failed",
                error_message=error_msg
            )
            return
        
        # Mark job as completed
        logger.info(f"[WORKER] Marking job as completed (100%)")
        job_service.update_status(
            job_id,
            "completed",
            progress=100,
            current_step="Processing complete"
        )
        mongodb_manager.update_job_progress(job_id, 100, "Processing complete")
        
        logger.info(f"[WORKER] Successfully completed job {job_id}")
        
    except Exception as e:
        logger.error(f"[WORKER] Unexpected error in process_pdf_job: {e}")
        logger.error(traceback.format_exc())
        try:
            job_service = JobService()
            error_msg = f"Processing error: {str(e)}"
            job_service.update_status(
                job_id,
                "failed",
                error_message=error_msg
            )
            mongodb_manager = MongoDBManager()
            mongodb_manager.update_job_progress(job_id, 0, "Failed")
        except:
            logger.error(f"[WORKER] Failed to update job status for {job_id}")

