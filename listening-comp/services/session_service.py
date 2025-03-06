"""
Session management service for tracking user sessions and group IDs
"""
import os
import streamlit as st
import logging
from datetime import datetime
from services.reporting_service import reporting_service

logger = logging.getLogger(__name__)

class SessionService:
    """Service for managing user sessions and group IDs"""
    
    def __init__(self):
        """Initialize the session service"""
        self.default_group_id = int(os.environ.get('DEFAULT_GROUP_ID', 1))
    
    def initialize_session(self):
        """
        Initialize session state for group ID and session tracking
        """
        # Initialize group_id if not already set
        if 'group_id' not in st.session_state:
            st.session_state.group_id = self.default_group_id
            
        # Initialize study_session_id if not already set
        if 'study_session_id' not in st.session_state:
            st.session_state.study_session_id = None
            
        # Initialize session_words to track words in the current session
        if 'session_words' not in st.session_state:
            st.session_state.session_words = []
    
    def set_group_id(self, group_id):
        """
        Set the group ID for the current session
        
        Args:
            group_id (int): The group ID
        """
        st.session_state.group_id = group_id
        
        # Reset session ID when group changes
        st.session_state.study_session_id = None
        st.session_state.session_words = []
        
        logger.info(f"Set group ID to {group_id}")
    
    def get_group_id(self):
        """
        Get the current group ID
        
        Returns:
            int: The group ID
        """
        return st.session_state.group_id
    
    def ensure_study_session(self):
        """
        Ensure a study session exists for the current group
        
        Returns:
            int: The study session ID
        """
        # If we already have a session ID, return it
        if st.session_state.study_session_id is not None:
            return st.session_state.study_session_id
            
        # Otherwise, create a new session
        group_id = self.get_group_id()
        session_id = reporting_service.create_study_session(group_id)
        
        if session_id:
            st.session_state.study_session_id = session_id
            st.session_state.session_words = []
            return session_id
        else:
            # If failed to create a session, use a placeholder ID
            logger.warning("Failed to create study session, using placeholder")
            return -1
    
    def report_question_result(self, question, selected_answer, feedback):
        """
        Report question result to the backend
        
        Args:
            question (dict): The question object
            selected_answer (int): The selected answer index
            feedback (dict): The feedback object
            
        Returns:
            bool: True if successfully reported, False otherwise
        """
        # Ensure we have a study session
        session_id = self.ensure_study_session()
        
        if session_id <= 0:
            logger.warning("No valid study session, skipping report")
            return False
        
        # Extract correctness from feedback
        correct = feedback.get('correct', False)
        
        # Report all words from the question
        results = reporting_service.report_question_words(session_id, question, correct)
        
        # Track words in session state for reference
        for word in results.keys():
            if word not in st.session_state.session_words:
                st.session_state.session_words.append(word)
        
        # Log the results
        logger.info(f"Reported {len(results)} words for question, correct: {correct}")
        
        return True

# Create a singleton instance
session_service = SessionService()