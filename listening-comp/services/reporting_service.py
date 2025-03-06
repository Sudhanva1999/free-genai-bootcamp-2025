"""
Reporting service for sending data to the main learning backend
"""
import os
import json
import requests
from datetime import datetime
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ReportingService:
    """Service for reporting data to the main learning backend"""
    
    def __init__(self):
        """Initialize the reporting service with API endpoints"""
        self.base_url = os.environ.get('LEARNING_BACKEND_URL', 'http://localhost:3000')
        self.study_activity_id = int(os.environ.get('LISTENING_ACTIVITY_ID', 3))  # Default to 3 based on study_activities.json
        
    def create_study_session(self, group_id: int) -> Optional[int]:
        """
        Create a new study session for the given group
        
        Args:
            group_id: The ID of the group
            
        Returns:
            session_id: ID of the created session or None if failed
        """
        try:
            url = f"{self.base_url}/api/study_activities"
            params = {
                'group_id': group_id,
                'study_activity_id': self.study_activity_id
            }
            
            response = requests.post(url, params=params)
            response.raise_for_status()
            
            session_data = response.json()
            logger.info(f"Created study session: {session_data}")
            
            # Return the session ID
            return session_data.get('id')
            
        except requests.RequestException as e:
            logger.error(f"Failed to create study session: {e}")
            return None
    
    def report_word_review(self, session_id: int, word: str, correct: bool) -> bool:
        """
        Report a word review to the backend
        
        Args:
            session_id: The study session ID
            word: The Marathi word being reviewed
            correct: Whether the answer was correct
            
        Returns:
            bool: True if successfully reported, False otherwise
        """
        try:
            # We need to change our approach - let's use the reviewWord approach in the controller
            # but instead of using the URL parameter for the word, let's send it in the body
            url = f"{self.base_url}/api/study_sessions/{session_id}/words/review"
            
            payload = {
                'word': word,
                'correct': correct
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Reported word review: {word}, correct: {correct}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to report word review: {e}")
            return False
    
    def report_question_words(self, session_id: int, question: Dict[str, Any], correct: bool) -> Dict[str, bool]:
        """
        Extract words from a question and report them all
        
        Args:
            session_id: The study session ID
            question: The question object
            correct: Whether the answer was correct
            
        Returns:
            Dict[str, bool]: Dictionary of words and their reporting status
        """
        # Extract relevant words from the question
        from services.word_mapping_service import word_mapping_service
        words = word_mapping_service.extract_words_from_question(question)
        
        # Report each word
        results = {}
        for word in words:
            results[word] = self.report_word_review(session_id, word, correct)
            
        # Log summary
        logger.info(f"Reported {len(results)} words for question, correct: {correct}")
        
        return results

# Create a singleton instance
reporting_service = ReportingService()