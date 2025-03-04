import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, Optional
import re
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def get_page_content(url: str) -> Dict[str, Optional[str]]:
    """
    Extract lyrics content from a webpage.
    
    Args:
        url (str): URL of the webpage to extract content from
        
    Returns:
        Dict[str, Optional[str]]: Dictionary containing marathi_lyrics, phonetic_lyrics, and metadata
    """
    logger.info(f"Fetching content from URL: {url}")
    try:
        async with aiohttp.ClientSession() as session:
            logger.debug("Making HTTP request...")
            async with session.get(url) as response:
                if response.status != 200:
                    error_msg = f"Error: HTTP {response.status}"
                    logger.error(error_msg)
                    return {
                        "marathi_lyrics": None,
                        "phonetic_lyrics": None,
                        "metadata": error_msg
                    }
                
                logger.debug("Reading response content...")
                html = await response.text()
                logger.info(f"Successfully fetched page content ({len(html)} bytes)")
                return extract_lyrics_from_html(html, url)
    except Exception as e:
        error_msg = f"Error fetching page: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "marathi_lyrics": None,
            "phonetic_lyrics": None,
            "metadata": error_msg
        }

def extract_lyrics_from_html(html: str, url: str) -> Dict[str, Optional[str]]:
    """
    Extract lyrics from HTML content based on common patterns in lyrics websites.
    """
    logger.info("Starting lyrics extraction from HTML")
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove script and style elements
    logger.debug("Cleaning HTML content...")
    for element in soup(['script', 'style', 'header', 'footer', 'nav']):
        element.decompose()
    
    # Common patterns for lyrics containers
    lyrics_patterns = [
        # Class patterns
        {"class_": re.compile(r"lyrics?|marathi|devanagari|phonetic", re.I)},
        {"class_": re.compile(r"song-content|song-text|track-text", re.I)},
        # ID patterns
        {"id": re.compile(r"lyrics?|marathi|devanagari|phonetic", re.I)},
        # Common Marathi lyrics sites patterns
        {"class_": "lyrics_box"},  
        {"class_": "marathi"},    
        {"class_": "devanagari"}, 
        {"class_": "phonetic"}   
    ]
    
    marathi_lyrics = None
    phonetic_lyrics = None
    metadata = ""
    
    # Try to find lyrics containers
    logger.debug("Searching for lyrics containers...")
    for pattern in lyrics_patterns:
        logger.debug(f"Trying pattern: {pattern}")
        elements = soup.find_all(**pattern)
        logger.debug(f"Found {len(elements)} matching elements")
        
        for element in elements:
            text = clean_text(element.get_text())
            logger.debug(f"Extracted text length: {len(text)} chars")
            
            # Detect if text is primarily Marathi or phonetic
            if is_primarily_marathi(text) and not marathi_lyrics:
                logger.info("Found Marathi lyrics")
                marathi_lyrics = text
            elif is_primarily_phonetic(text) and not phonetic_lyrics:
                logger.info("Found phonetic lyrics")
                phonetic_lyrics = text
    
    # If no structured containers found, try to find the largest text block
    if not marathi_lyrics and not phonetic_lyrics:
        logger.info("No lyrics found in structured containers, trying fallback method")
        text_blocks = [clean_text(p.get_text()) for p in soup.find_all('p')]
        if text_blocks:
            largest_block = max(text_blocks, key=len)
            logger.debug(f"Found largest text block: {len(largest_block)} chars")
            
            if is_primarily_marathi(largest_block):
                logger.info("Largest block contains Marathi text")
                marathi_lyrics = largest_block
            elif is_primarily_phonetic(largest_block):
                logger.info("Largest block contains phonetic text")
                phonetic_lyrics = largest_block
    
    result = {
        "marathi_lyrics": marathi_lyrics,
        "phonetic_lyrics": phonetic_lyrics,
        "metadata": metadata or "Lyrics extracted successfully"
    }
    
    # Log the results
    if marathi_lyrics:
        logger.info(f"Found Marathi lyrics ({len(marathi_lyrics)} chars)")
    if phonetic_lyrics:
        logger.info(f"Found phonetic lyrics ({len(phonetic_lyrics)} chars)")
    
    return result

def clean_text(text: str) -> str:
    """
    Clean extracted text by removing extra whitespace and unnecessary characters.
    """
    logger.debug(f"Cleaning text of length {len(text)}")
    # Remove HTML entities
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)
    # Remove multiple spaces and newlines
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    # Remove leading/trailing whitespace
    result = text.strip()
    logger.debug(f"Text cleaned, new length: {len(result)}")
    return result

def is_primarily_marathi(text: str) -> bool:
    """
    Check if text contains primarily Marathi characters (Devanagari script).
    """
    # Count Devanagari characters (Marathi uses Devanagari script)
    marathi_chars = len(re.findall(r'[\u0900-\u097F]', text))
    total_chars = len(text.strip())
    ratio = marathi_chars / total_chars if total_chars > 0 else 0
    logger.debug(f"Marathi character ratio: {ratio:.2f} ({marathi_chars}/{total_chars})")
    return marathi_chars > 0 and ratio > 0.3

def is_primarily_phonetic(text: str) -> bool:
    """
    Check if text contains primarily Latin characters with diacritical marks
    that would indicate a phonetic transcription.
    """
    # Count Latin characters (basic Latin alphabet) and diacritical marks
    phonetic_chars = len(re.findall(r'[a-zA-Z\u0300-\u036F\u1DC0-\u1DFF\u20D0-\u20FF\u0900-\u097F]', text))
    total_chars = len(text.strip())
    
    # Check for diacritical marks that are common in phonetic transcriptions
    has_diacritics = bool(re.search(r'[\u0300-\u036F\u1DC0-\u1DFF\u20D0-\u20FF]', text))
    
    # Calculate the ratio of phonetic characters to total characters
    ratio = phonetic_chars / total_chars if total_chars > 0 else 0
    logger.debug(f"Phonetic character ratio: {ratio:.2f} ({phonetic_chars}/{total_chars})")
    
    # Either high Latin character ratio or presence of diacritics indicates phonetic text
    return phonetic_chars > 0 and (ratio > 0.3 or has_diacritics)