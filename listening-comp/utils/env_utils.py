"""
Utilities for loading environment variables
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def load_environment():
    """
    Load environment variables from .env file
    """
    # Find the project root directory
    project_root = Path(__file__).parent.parent.absolute()
    env_path = project_root / '.env'
    
    # Load .env file if it exists
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded environment variables from {env_path}")
    else:
        logger.warning(f"No .env file found at {env_path}, using defaults")

    # Log key configuration values
    logger.info(f"LEARNING_BACKEND_URL: {os.environ.get('LEARNING_BACKEND_URL', 'http://localhost:3000')}")
    logger.info(f"LISTENING_ACTIVITY_ID: {os.environ.get('LISTENING_ACTIVITY_ID', 3)}")