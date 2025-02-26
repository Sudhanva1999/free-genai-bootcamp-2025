import json
from typing import Dict, Any, Tuple, Optional
from models.schemas import WordGroup
from jsonschema import validate, ValidationError

def validate_llm_response(response: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate the response from an LLM against our expected schema.
    
    Args:
        response: The dictionary response from the LLM
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Use Pydantic model for validation
        WordGroup(**response)
        return True, None
    except Exception as e:
        return False, str(e)

def format_llm_response(response_text: str) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Attempt to parse and format the raw LLM response text into our expected JSON structure.
    
    Args:
        response_text: Raw text response from the LLM
        
    Returns:
        Tuple of (formatted_response, error_message)
    """
    try:
        # Try to find and extract JSON from the response
        response_text = response_text.strip()
        
        # Look for JSON opening and closing braces
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx]
            parsed = json.loads(json_str)
            
            # Validate against our schema
            is_valid, error = validate_llm_response(parsed)
            if is_valid:
                return parsed, None
            else:
                return None, f"Invalid response format: {error}"
        else:
            return None, "Could not find valid JSON in the response"
    except json.JSONDecodeError as e:
        return None, f"JSON parsing error: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error formatting response: {str(e)}"