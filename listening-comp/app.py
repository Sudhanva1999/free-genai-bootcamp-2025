"""
Marathi Listening Practice Application - Entry Point
"""
import streamlit as st
import logging
from ui.main_page import render_main_page
from config import setup_config
from utils.env_utils import load_environment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    # Load environment variables
    load_environment()
    
    # Setup configuration (page, paths, etc.)
    setup_config()
    
    # Render the main application
    render_main_page()

if __name__ == "__main__":
    main()