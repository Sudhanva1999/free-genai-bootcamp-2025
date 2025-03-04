from typing import List, Dict, Any, Optional
import json
import logging
from pathlib import Path

logger = logging.getLogger('song_vocab')

def save_results(song_id: str, lyrics: str, vocabulary: Optional[List[Dict[str, Any]]] = None, lyrics_path: Path = None, vocabulary_path: Path = None) -> str:
    """
    Save lyrics and vocabulary to their respective files.
    
    Args:
        song_id (str): ID of the song
        lyrics (str): Marathi lyrics text
        vocabulary (List[Dict[str, Any]], optional): List of vocabulary items. If None, generates a placeholder.
        lyrics_path (Path, optional): Directory to save lyrics files. If None, uses default.
        vocabulary_path (Path, optional): Directory to save vocabulary files. If None, uses default.
    
    Returns:
        str: The song_id that was used to save the files
    """
    # Handle the case where paths are not provided
    if lyrics_path is None or vocabulary_path is None:
        base_path = Path(__file__).parent.parent
        lyrics_path = lyrics_path or base_path / "outputs" / "lyrics"
        vocabulary_path = vocabulary_path or base_path / "outputs" / "vocabulary"
        
        # Create directories if they don't exist
        lyrics_path.mkdir(parents=True, exist_ok=True)
        vocabulary_path.mkdir(parents=True, exist_ok=True)
    
    # Create a placeholder vocabulary if none provided
    if vocabulary is None or not vocabulary:
        logger.warning("No vocabulary provided, creating a placeholder")
        vocabulary = [{
            "marathi": "placeholder",
            "phonetic": "placeholder",
            "english": "This is a placeholder vocabulary item",
            "parts": [{"marathi": "placeholder", "phonetic": ["placeholder"]}]
        }]
    
    # Save lyrics
    lyrics_file = lyrics_path / f"{song_id}.txt"
    lyrics_file.write_text(lyrics)
    logger.info(f"Saved lyrics to {lyrics_file}")
    
    # Save vocabulary
    vocab_file = vocabulary_path / f"{song_id}.json"
    try:
        vocab_file.write_text(json.dumps(vocabulary, ensure_ascii=False, indent=2))
        logger.info(f"Saved vocabulary to {vocab_file}")
    except Exception as e:
        logger.error(f"Error saving vocabulary: {e}")
        # Attempt to save a simplified version
        try:
            # Create simple placeholder if JSON conversion fails
            placeholder = [{
                "marathi": "error_placeholder",
                "phonetic": "error_placeholder",
                "english": f"Error occurred: {str(e)}",
                "parts": [{"marathi": "error_placeholder", "phonetic": ["error_placeholder"]}]
            }]
            vocab_file.write_text(json.dumps(placeholder, ensure_ascii=False, indent=2))
            logger.info(f"Saved placeholder vocabulary to {vocab_file}")
        except Exception as e2:
            logger.error(f"Failed to save placeholder vocabulary: {e2}")
    
    return song_id