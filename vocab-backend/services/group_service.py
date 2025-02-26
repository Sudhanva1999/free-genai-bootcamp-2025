from typing import Dict, Any, List, Optional, Tuple

from models.database import Database
from services.llm_service import BedrockLLMService

class GroupService:
    def __init__(self):
        self.db = Database()
        self.llm_service = BedrockLLMService()
    
    def get_words_by_group_id(self, group_id: int) -> Tuple[Optional[Dict[str, Any]], int]:
        """
        Get words for a specific group ID, fetching from DB or LLM if needed.
        
        Args:
            group_id: The ID of the group
            
        Returns:
            Tuple of (response_data, status_code)
        """
        # Check if group exists
        group = self.db.get_group_by_id(group_id)
        if not group:
            return {"error": f"Group with ID {group_id} not found"}, 404
        
        # Check if we already have words for this group
        words = self.db.get_words_by_group_id(group_id)
        
        if words:
            # We have words in the database, return them
            return {
                "group_name": group["name"],
                "words": words
            }, 200
        
        # No words found, call LLM to generate them
        return self._generate_and_save_words(group["name"], group_id)
    
    def get_words_by_group_name(self, group_name: str) -> Tuple[Dict[str, Any], int]:
        """
        Get words for a specific group name, directly calling the LLM and storing results.
        
        Args:
            group_name: The name of the group
            
        Returns:
            Tuple of (response_data, status_code)
        """
        # Check if the group exists in our database
        group = self.db.get_group_by_name(group_name)
        
        if group:
            group_id = group["id"]
        else:
            # Create the new group
            group_id = self.db.add_group(group_name)
        
        # Call LLM to generate words regardless of whether we have existing words
        return self._generate_and_save_words(group_name, group_id)
    
    def _generate_and_save_words(self, group_name: str, group_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Generate words using LLM and save them to the database.
        
        Args:
            group_name: The name of the group
            group_id: The ID of the group
            
        Returns:
            Tuple of (response_data, status_code)
        """
        # Call LLM to generate words
        llm_response = self.llm_service.generate_words(group_name)
        
        if not llm_response:
            return {"error": "Failed to generate words from LLM"}, 500
        
        # Save words to database
        self.db.add_words(group_id, llm_response["words"])
        
        return llm_response, 200