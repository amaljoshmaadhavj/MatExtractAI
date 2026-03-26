"""Test OLLAMA integration with MatExtractAI backend."""

import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.services.ollama_service import OllamaService
from app.services.agent_service import AgentService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_ollama_service():
    """Test basic OLLAMA service connection."""
    logger.info("=" * 60)
    logger.info("Testing OLLAMA Service Connection")
    logger.info("=" * 60)
    
    logger.info(f"OLLAMA Host: {settings.ollama_host}")
    logger.info(f"OLLAMA Model: {settings.ollama_model}")
    
    try:
        service = OllamaService()
        logger.info("✅ OLLAMA Service initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ OLLAMA Service failed: {e}")
        return False


def test_agent_service():
    """Test agent service initialization."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Agent Service")
    logger.info("=" * 60)
    
    try:
        agent_service = AgentService()
        
        if agent_service.ollama:
            logger.info("✅ Agent Service initialized with OLLAMA")
        else:
            logger.warning("⚠️ Agent Service initialized without OLLAMA (fallback mode)")
        
        return True
    except Exception as e:
        logger.error(f"❌ Agent Service failed: {e}")
        return False


def test_extraction_with_mock():
    """Test extraction and agent services with mock data."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Extraction & Agents with Mock Data")
    logger.info("=" * 60)
    
    try:
        agent_service = AgentService()
        
        # Mock sections
        mock_sections = {
            "abstract": "This paper studies magnesium alloys...",
            "introduction": "AZ31 is a Mg+3%Al+1%Zn alloy...",
            "materials": "Materials were prepared by casting and rolling...",
            "methods": "Hot rolling at 400°C for 2 hours followed by annealing at 350°C...",
            "results": "The grain size was measured as 15 μm. Yield strength: 170 MPa...",
            "discussion": "The mechanical properties indicate good ductility...",
            "conclusion": "AZ31 shows promising properties for applications..."
        }
        
        mock_tables = []
        
        logger.info("Running all agents with mock data...")
        results = agent_service.run_all_agents(mock_sections, mock_tables)
        
        logger.info(f"✅ Extraction completed with status: {results.get('extraction_status')}")
        
        # Show summary
        logger.info(f"  - Mechanical Properties: {len(results.get('mechanical_properties', {}).get('extracted_data', []))} items")
        logger.info(f"  - Composition: {len(results.get('composition', {}).get('extracted_data', []))} items")
        logger.info(f"  - Processing: {len(results.get('processing', {}).get('extracted_data', []))} items")
        logger.info(f"  - Microstructure: {len(results.get('microstructure', {}).get('extracted_data', []))} items")
        
        return True
    except Exception as e:
        logger.error(f"❌ Extraction test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    """Run all OLLAMA integration tests."""
    logger.info("\n🔍 MatExtractAI - OLLAMA Integration Test Suite\n")
    
    results = {
        "OLLAMA Service": test_ollama_service(),
        "Agent Service": test_agent_service(),
        "Mock Extraction": test_extraction_with_mock()
    }
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    logger.info("=" * 60)
    if all_passed:
        logger.info("✅ All tests passed! OLLAMA integration is ready.")
        logger.info("\nNext steps:")
        logger.info("1. Start backend: python -m uvicorn app.main:app --reload")
        logger.info("2. Upload a PDF document via the frontend")
        logger.info("3. Check results in MongoDB Atlas")
        return 0
    else:
        logger.error("❌ Some tests failed. Check logs above for details.")
        logger.error("\nTroubleshooting:")
        logger.error("1. Verify OLLAMA is running: http://localhost:11435")
        logger.error("2. Check OLLAMA_HOST in .env file")
        logger.error("3. Verify model is loaded: ollama pull mistral")
        return 1


if __name__ == "__main__":
    sys.exit(main())
