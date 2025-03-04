from typing import List, Dict, Any
import logging
import json
from pathlib import Path
import re
import os
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger(__name__)

class Part(BaseModel):
    marathi: str
    phonetic: List[str]

class VocabularyItem(BaseModel):
    marathi: str
    phonetic: str
    english: str
    parts: List[Part]

async def extract_vocabulary(text: str) -> List[dict]:
    """
    Extract basic vocabulary from Marathi text with a fallback mechanism.
    
    Args:
        text (str): The text to extract vocabulary from
        
    Returns:
        List[dict]: List of vocabulary items in Marathi format with Devanagari, phonetic transcription, and parts
    """
    logger.info("Starting vocabulary extraction")
    logger.debug(f"Input text length: {len(text)} characters")
    
    try:
        # Check if we should use cloud services
        use_cloud = os.getenv('USE_CLOUD_AGENT', 'false').lower() == 'true'
        
        if use_cloud:
            logger.info("Using cloud service for vocabulary extraction")
            try:
                import boto3
                
                # Get cloud model from environment variable or use default
                cloud_model = os.getenv('CLOUD_MODEL', 'anthropic.claude-3-5-sonnet-20240620-v1:0')
                logger.info(f"Using Amazon Bedrock with model: {cloud_model}")
                
                return await _extract_with_bedrock(text, cloud_model)
            except Exception as e:
                logger.warning(f"Could not use Bedrock for extraction: {e}")
                return _extract_fallback(text)
        else:
            # Try to use instructor with Ollama if available
            try:
                import instructor
                import ollama
                
                # Check if ollama service is running
                client = ollama.Client()
                models = client.list()
                
                if models:
                    logger.info("Using Ollama for vocabulary extraction")
                    return await _extract_with_ollama(text, client)
                else:
                    logger.warning("Ollama is installed but no models found")
                    return _extract_fallback(text)
                    
            except (ImportError, Exception) as e:
                logger.warning(f"Could not use Ollama+Instructor for extraction: {e}")
                return _extract_fallback(text)
            
    except Exception as e:
        logger.error(f"Failed to extract vocabulary: {str(e)}", exc_info=True)
        # Return minimal vocabulary to avoid breaking the flow
        return _extract_fallback(text)

async def _extract_with_bedrock(text: str, model_id: str) -> List[dict]:
    """Try to extract vocabulary using Amazon Bedrock."""
    try:
        import boto3
        import json
        
        bedrock_client = boto3.client('bedrock-runtime')
        
        # Create a prompt for vocabulary extraction
        prompt = f"""
You are a Marathi language expert. I'll give you text in Marathi, and your task is to extract vocabulary terms.

Extract vocabulary from this Marathi text. For each word, provide:
1. The word in Devanagari
2. Phonetic transcription 
3. English meaning (best guess)
4. Break down of parts (if compound word)

FORMAT each entry as valid JSON. The output should be a JSON array where each item has this structure:
{{
  "marathi": "पैसे",
  "phonetic": "paisē",
  "english": "money",
  "parts": [
    {{ "marathi": "पैसे", "phonetic": ["paisē"] }}
  ]
}}

TEXT TO ANALYZE:
{text}

IMPORTANT: Your entire response must be ONLY the JSON array. Do not include any explanations or notes.
"""
        
        # Prepare the request for Claude API via Bedrock
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }
            ],
            "temperature": 0.2
        }
        
        # Call Bedrock API
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        content = response_body.get('content', [{}])[0].get('text', '')
        
        # Extract JSON array from the response
        json_match = re.search(r'\[\s*{.+}\s*\]', content, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group(0))
                logger.info(f"Extracted {len(result)} vocabulary items with Bedrock")
                
                # Ensure result is not empty
                if not result:
                    logger.warning("Empty result from Bedrock extraction")
                    return _extract_fallback(text)
                
                return result
            except json.JSONDecodeError as e:
                logger.warning(f"Could not parse JSON from Bedrock response: {e}")
                # Try to extract any valid JSON objects
                try:
                    # Clean up the JSON text
                    cleaned_json = re.sub(r'```json\s*|\s*```', '', content)
                    cleaned_json = cleaned_json.strip()
                    # If it doesn't start with [ and end with ], add them
                    if not cleaned_json.startswith('['):
                        cleaned_json = '[' + cleaned_json
                    if not cleaned_json.endswith(']'):
                        cleaned_json = cleaned_json + ']'
                    
                    result = json.loads(cleaned_json)
                    logger.info(f"Extracted {len(result)} vocabulary items after cleanup")
                    return result
                except:
                    logger.warning("Failed to parse JSON even after cleanup")
                    return _extract_fallback(text)
        else:
            logger.warning("No JSON array found in Bedrock response")
            return _extract_fallback(text)
            
    except Exception as e:
        logger.error(f"Error in Bedrock extraction: {e}")
        return _extract_fallback(text)

async def _extract_with_ollama(text: str, client) -> List[dict]:
    """Try to extract vocabulary using Ollama."""
    try:
        # Create a simple prompt for vocabulary extraction
        prompt = f"""
Extract vocabulary from this Marathi text. For each word, provide:
1. The word in Devanagari
2. Phonetic transcription 
3. English meaning
4. Break down of parts

FORMAT each entry as valid JSON like this:
{{
  "marathi": "पैसे देणे",
  "phonetic": "Paisē dēṇē",
  "english": "to pay",
  "parts": [
    {{ "marathi": "पैसे", "phonetic": ["Paisē"] }},
    {{ "marathi": "देणे", "phonetic": ["dēṇē"] }}
  ]
}}

TEXT TO ANALYZE:
{text}

VOCABULARY (in valid JSON array):
[
        """
        
        # Make a call to Ollama
        response = client.chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.get('message', {}).get('content', '')
        
        # Extract JSON from the response
        json_match = re.search(r'\[\s*{.+}\s*\]', content, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group(0))
                logger.info(f"Extracted {len(result)} vocabulary items with Ollama")
                return result
            except json.JSONDecodeError:
                logger.warning("Could not parse JSON from Ollama response")
                return _extract_fallback(text)
        else:
            logger.warning("No JSON array found in Ollama response")
            return _extract_fallback(text)
            
    except Exception as e:
        logger.error(f"Error in Ollama extraction: {e}")
        return _extract_fallback(text)

def _extract_fallback(text: str) -> List[dict]:
    """
    Basic fallback vocabulary extraction when LLM methods fail.
    Extracts words and creates simple vocabulary items.
    """
    logger.info("Using fallback vocabulary extraction method")
    
    # Regex to find Marathi words (Devanagari script)
    word_pattern = r'[\u0900-\u097F]+'
    words = re.findall(word_pattern, text)
    
    # Deduplicate words
    unique_words = list(set(words))
    logger.info(f"Found {len(unique_words)} unique Marathi words")
    
    # Simple phonetic mapping for common Devanagari characters
    phonetic_map = {
        'अ': 'a', 'आ': 'ā', 'इ': 'i', 'ई': 'ī', 'उ': 'u', 'ऊ': 'ū',
        'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au',
        'क': 'ka', 'ख': 'kha', 'ग': 'ga', 'घ': 'gha', 'ङ': 'ṅa',
        'च': 'ca', 'छ': 'cha', 'ज': 'ja', 'झ': 'jha', 'ञ': 'ña',
        'ट': 'ṭa', 'ठ': 'ṭha', 'ड': 'ḍa', 'ढ': 'ḍha', 'ण': 'ṇa',
        'त': 'ta', 'थ': 'tha', 'द': 'da', 'ध': 'dha', 'न': 'na',
        'प': 'pa', 'फ': 'pha', 'ब': 'ba', 'भ': 'bha', 'म': 'ma',
        'य': 'ya', 'र': 'ra', 'ल': 'la', 'व': 'va', 'श': 'śa',
        'ष': 'ṣa', 'स': 'sa', 'ह': 'ha', 'ळ': 'ḷa',
        '्': '', 'ा': 'ā', 'ि': 'i', 'ी': 'ī', 'ु': 'u', 'ू': 'ū',
        'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au', 'ं': 'ṃ', 'ः': 'ḥ'
    }
    
    # Generate simple vocabulary items
    vocabulary = []
    
    for word in unique_words:
        if len(word) < 2:  # Skip very short words
            continue
            
        # Crude phonetic approximation
        phonetic = ""
        for char in word:
            phonetic += phonetic_map.get(char, char)
        
        # Create vocabulary item
        item = {
            "marathi": word,
            "phonetic": phonetic,
            "english": "",  # No translation in fallback mode
            "parts": [{"marathi": word, "phonetic": [phonetic]}]
        }
        vocabulary.append(item)
    
    # Limit to top 50 words to avoid overwhelming
    return vocabulary[:50]