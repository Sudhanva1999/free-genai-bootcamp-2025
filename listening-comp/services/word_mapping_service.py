"""
Service for mapping between Marathi words and their representation for the learning backend
"""
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class WordMappingService:
    """Service for handling Marathi words for reporting"""
    
    def __init__(self):
        """Initialize the word mapping service"""
        logger.info("Initializing word mapping service - no local dictionary needed")
    
    def extract_words_from_question(self, question: Dict[str, Any]) -> List[str]:
        """
        Extract Marathi words from a question
        
        Args:
            question: The question object
            
        Returns:
            List[str]: List of Marathi words found in the question
        """
        words = []
        
        # Extract words from different parts of the question
        if 'Introduction' in question:
            words.extend(self._extract_marathi_words(question['Introduction']))
            
        if 'Conversation' in question:
            words.extend(self._extract_marathi_words(question['Conversation']))
            
        if 'Situation' in question:
            words.extend(self._extract_marathi_words(question['Situation']))
            
        if 'Question' in question:
            words.extend(self._extract_marathi_words(question['Question']))
            
        # Extract words from options
        if 'Options' in question and isinstance(question['Options'], list):
            for option in question['Options']:
                words.extend(self._extract_marathi_words(option))
        
        # Remove duplicates while preserving order
        unique_words = []
        for word in words:
            if word not in unique_words:
                unique_words.append(word)
                
        return unique_words
    
    def _extract_marathi_words(self, text: str) -> List[str]:
        """
        Extract Marathi words from text
        
        Args:
            text: The text to extract words from
            
        Returns:
            List[str]: List of Marathi words
        """
        # Simple implementation - split by whitespace and filter out punctuation
        if not text:
            return []
            
        # Remove common punctuation
        for char in '.,!?()[]{};:"\'':
            text = text.replace(char, ' ')
            
        # Split by whitespace and filter out empty strings
        raw_words = [word.strip() for word in text.split() if word.strip()]
        
        # Filter words to only include those with Marathi characters
        # Marathi Unicode range: \u0900-\u097F
        marathi_words = []
        for word in raw_words:
            # Check if word contains at least one Marathi character
            if any(ord('\u0900') <= ord(char) <= ord('\u097F') for char in word):
                marathi_words.append(word)
                
        return marathi_words

# Create a singleton instance
word_mapping_service = WordMappingService()