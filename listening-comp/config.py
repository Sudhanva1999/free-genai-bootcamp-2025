"""
Configuration settings for the Marathi Listening Practice application
"""
import os
import sys
import streamlit as st

# Constants
APP_TITLE = "Marathi Listening Practice"
APP_ICON = "🎧"
APP_DESCRIPTION = """
Welcome to Marathi Listening Practice! This application helps you improve your Marathi 
listening comprehension skills. Choose a practice type and topic, then generate questions 
to test your understanding.
"""

# Practice types and topics
PRACTICE_TYPES = ["Dialogue Practice", "Phrase Matching"]
TOPICS = {
    "Dialogue Practice": [
        "Daily Conversation", "Shopping", "Restaurant", 
        "Travel", "Family", "Education", "Health"
    ],
    "Phrase Matching": [
        "Greetings", "Directions", "Public Announcements", 
        "Cultural Expressions", "Festivals"
    ]
}

# Paths
def get_root_path():
    """Get the project root path"""
    return os.path.dirname(os.path.abspath(__file__))

def get_data_path():
    """Get the data directory path"""
    return os.path.join(get_root_path(), "backend", "data")

def get_questions_file_path():
    """Get the full path to the stored questions JSON file"""
    return os.path.join(get_data_path(), "stored_questions.json")

def setup_config():
    """Setup Streamlit configuration and environment"""
    # Page configuration
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="wide"
    )
    
    # Add the project root to the Python path
    project_root = get_root_path()
    if project_root not in sys.path:
        sys.path.append(project_root)