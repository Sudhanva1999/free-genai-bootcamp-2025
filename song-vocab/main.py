from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
import logging
from pathlib import Path
from agent import SongLyricsAgent
from dotenv import load_dotenv
from tools.save_results import save_results

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set default level to INFO
    format='%(message)s'  # Simplified format for better readability
)

# Configure specific loggers
logger = logging.getLogger('song_vocab')  # Root logger for our app
logger.setLevel(logging.DEBUG)

# Silence noisy third-party loggers
for noisy_logger in ['httpcore', 'httpx', 'urllib3']:
    logging.getLogger(noisy_logger).setLevel(logging.WARNING)

app = FastAPI()

class LyricsRequest(BaseModel):
    message_request: str

@app.post("/api/agent")
async def get_lyrics(request: LyricsRequest) -> Dict[str, Any]:
    logger.info(f"Received request: {request.message_request}")
    try:
        # Initialize agent
        logger.debug("Initializing SongLyricsAgent")
        agent = SongLyricsAgent(stream_llm=False, available_ram_gb=16)
        
        # Process request
        logger.info("Processing request through agent")
        song_id = await agent.process_request(request.message_request)
        logger.info(f"Got song_id: {song_id}")
        
        # Read the stored files
        lyrics_path = Path(agent.lyrics_path)
        vocab_path = Path(agent.vocabulary_path)
        lyrics_file = lyrics_path / f"{song_id}.txt"
        vocab_file = vocab_path / f"{song_id}.json"
        
        logger.debug(f"Checking files: {lyrics_file}, {vocab_file}")
        
        # If files don't exist, create them with placeholder data
        if not lyrics_file.exists() or not vocab_file.exists():
            logger.warning(f"Files not found: lyrics={lyrics_file.exists()}, vocab={vocab_file.exists()}")
            
            # Get default lyrics 
            default_lyrics = f"Lyrics for song ID: {song_id} (not found)"
            if hasattr(agent, 'last_lyrics') and agent.last_lyrics:
                default_lyrics = agent.last_lyrics
                
            # Create files with default data
            save_results(
                song_id=song_id,
                lyrics=default_lyrics,
                vocabulary=None,  # Will use placeholder vocab
                lyrics_path=lyrics_path,
                vocabulary_path=vocab_path
            )
            logger.info(f"Created default files for song_id: {song_id}")
        
        # Read file contents (now they should exist)
        logger.debug("Reading files")
        lyrics = lyrics_file.read_text()
        vocabulary = json.loads(vocab_file.read_text())
        logger.info(f"Successfully read lyrics ({len(lyrics)} chars) and vocabulary ({len(vocabulary)} items)")
        
        response = {
            "song_id": song_id,
            "lyrics": lyrics,
            "vocabulary": vocabulary
        }
        return response
    except Exception as e:
        logger.error(f"Error in API: {str(e)}", exc_info=True)
        # Return a partial response if we have a song_id but something else failed
        if 'song_id' in locals():
            try:
                # Try to create files with placeholder content
                lyrics_path = Path(agent.lyrics_path)
                vocab_path = Path(agent.vocabulary_path)
                
                save_results(
                    song_id=song_id,
                    lyrics=f"Error occurred, but song ID was generated: {song_id}",
                    vocabulary=None,
                    lyrics_path=lyrics_path,
                    vocabulary_path=vocab_path
                )
                
                return {
                    "song_id": song_id,
                    "lyrics": f"Error occurred: {str(e)}",
                    "vocabulary": [{"marathi": "Error", "phonetic": "error", "english": str(e), "parts": []}],
                    "error": str(e)
                }
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)