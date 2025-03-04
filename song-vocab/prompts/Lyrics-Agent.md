import ollama
import boto3
import json
import logging
import re
import asyncio
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from functools import partial
from tools.search_web_serp import search_web_serp
from tools.get_page_content import get_page_content
from tools.extract_vocabulary import extract_vocabulary
from tools.generate_song_id import generate_song_id
from tools.save_results import save_results
import math

# Get the app's root logger
logger = logging.getLogger('song_vocab')

class ToolRegistry:
    def __init__(self, lyrics_path: Path, vocabulary_path: Path):
        self.lyrics_path = lyrics_path
        self.vocabulary_path = vocabulary_path
        self.tools = {
            'search_web_serp': search_web_serp,
            'get_page_content': get_page_content,
            'extract_vocabulary': extract_vocabulary,
            'generate_song_id': generate_song_id,
            'save_results': partial(save_results, lyrics_path=lyrics_path, vocabulary_path=vocabulary_path)
        }
    
    def get_tool(self, name: str):
        return self.tools.get(name)

def calculate_safe_context_window(available_ram_gb: float, safety_factor: float = 0.8) -> int:
    """
    Calculate a safe context window size based on available RAM.
    """
    # Known ratio from our testing
    GB_PER_128K_TOKENS = 58.0
    TOKENS_128K = 131072
    
    # Calculate tokens per GB
    tokens_per_gb = TOKENS_128K / GB_PER_128K_TOKENS
    
    # Calculate safe token count
    safe_tokens = math.floor(available_ram_gb * tokens_per_gb * safety_factor)
    
    # Round down to nearest power of 2 for good measure
    power_of_2 = 2 ** math.floor(math.log2(safe_tokens))
    
    # Cap at 128K tokens
    final_tokens = min(power_of_2, TOKENS_128K)
    
    logger.debug(f"Context window calculation:")
    logger.debug(f"  Available RAM: {available_ram_gb}GB")
    logger.debug(f"  Tokens per GB: {tokens_per_gb}")
    logger.debug(f"  Raw safe tokens: {safe_tokens}")
    logger.debug(f"  Power of 2: {power_of_2}")
    logger.debug(f"  Final tokens: {final_tokens}")
    
    return final_tokens

class SongLyricsAgent:
    def __init__(self, stream_llm=True, available_ram_gb=32):
        logger.info("Initializing SongLyricsAgent")
        self.base_path = Path(__file__).parent
        
        # Create the agent prompt file if it doesn't exist
        self.prompt_path = self.base_path / "prompts" / "Lyrics-Agent.md"
        self.prompts_dir = self.base_path / "prompts"
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        
        # If the prompt file doesn't exist, create it with the default prompt
        if not self.prompt_path.exists():
            default_prompt = self._get_default_prompt()
            self.prompt_path.write_text(default_prompt)
            logger.info(f"Created default prompt file at {self.prompt_path}")
        
        self.lyrics_path = self.base_path / "outputs" / "lyrics"
        self.vocabulary_path = self.base_path / "outputs" / "vocabulary"
        self.stream_llm = stream_llm
        self.context_window = calculate_safe_context_window(available_ram_gb)
        logger.info(f"Calculated safe context window size: {self.context_window} tokens for {available_ram_gb}GB RAM")
        
        # Create output directories
        self.lyrics_path.mkdir(parents=True, exist_ok=True)
        self.vocabulary_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directories created: {self.lyrics_path}, {self.vocabulary_path}")
        
        # Check if cloud agent should be used
        self.use_cloud_agent = os.getenv('USE_CLOUD_AGENT', 'false').lower() == 'true'
        
        # Initialize LLM client and tool registry
        logger.info(f"Using {'cloud' if self.use_cloud_agent else 'local'} agent")
        try:
            if self.use_cloud_agent:
                # Get cloud model from environment variable or use default
                self.cloud_model = os.getenv('CLOUD_MODEL', 'anthropic.claude-3-5-sonnet-20240620-v1:0')
                logger.info(f"Initializing Amazon Bedrock client with model: {self.cloud_model}")
                self.bedrock_client = boto3.client('bedrock-runtime')
            else:
                # Get local model from environment variable or use default
                self.local_model = os.getenv('LOCAL_MODEL', 'mistral')
                logger.info(f"Initializing Ollama client with model: {self.local_model}")
                self.client = ollama.Client()
            
            self.tools = ToolRegistry(self.lyrics_path, self.vocabulary_path)
            logger.info("Initialization successful")
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            raise
    
    def _get_default_prompt(self) -> str:
        """Return the default prompt for the agent."""
        return """You are a helpful AI assistant that helps find Marathi song lyrics and extract Marathi vocabulary from them.

You have access to the following tools:
- search_web_serp(query: str): Search for Marathi song lyrics using SERP API
- get_page_content(url: str): Extract content from a webpage
- extract_vocabulary(text: str): Extract Marathi vocabulary and break it down into Devanagari, phonetic transcription, and parts
- generate_song_id(artist: str, title: str): Generate a URL-safe song ID from artist and title
- save_results(song_id: str, lyrics: str, vocabulary: List[Dict]): Save lyrics and vocabulary to files

Follow these steps in order:
1. Search for lyrics using search_web_serp
2. Extract content from webpage using get_page_content
3. Extract vocabulary using extract_vocabulary
4. Generate song ID using generate_song_id (MUST include both artist and title)
5. Save results using save_results
6. Return the song_id

IMPORTANT FORMATTING INSTRUCTIONS:
When calling tools, you MUST use EXACTLY this format:
Tool: tool_name(param1="value1", param2="value2")

Examples of CORRECT tool calls:
Tool: search_web_serp(query="Ajay-Atul तू मला संगते lyrics")
Tool: get_page_content(url="https://example.com/lyrics")
Tool: extract_vocabulary(text="काजळ लावुनी आले मी आज")
Tool: generate_song_id(artist="Ajay-Atul", title="तू मला संगते")
Tool: save_results(song_id="ajay-atul-tu-mala-sangte", lyrics="लिरिक्स टेक्स्ट", vocabulary=[{"marathi": "तू", "phonetic": "tū", "english": "you", "parts": [{"marathi": "तू", "phonetic": ["tū"]}]}])

After you've successfully saved the lyrics and vocabulary, respond with:
FINISHED
song_id: your-song-id-here

Always wait for the result after each tool call before proceeding to the next step.
"""
    
    def parse_llm_action(self, content: str) -> Optional[tuple[str, Dict[str, Any]]]:
        """Parse the LLM's response to extract tool name and arguments."""
        # Look for tool calls in multiple formats to handle different LLM outputs
        # Format 1: Tool: tool_name(arg1="value1", arg2="value2")
        match = re.search(r'Tool:\s*(\w+)\((.*?)\)', content)
        if match:
            tool_name = match.group(1)
            args_str = match.group(2)
            
            # Parse arguments - handle different quoting styles
            args = {}
            
            # Match arguments with double quotes
            # Pattern: key="value"
            for arg_match in re.finditer(r'(\w+)="([^"]*?)"', args_str):
                args[arg_match.group(1)] = arg_match.group(2)
            
            # If no arguments found with double quotes, try single quotes
            if not args:
                for arg_match in re.finditer(r"(\w+)='([^']*?)'", args_str):
                    args[arg_match.group(1)] = arg_match.group(2)
            
            # If still no arguments, try without quotes (for numeric values)
            if not args and args_str.strip():
                for arg_match in re.finditer(r'(\w+)=([^,\s]+)', args_str):
                    args[arg_match.group(1)] = arg_match.group(2)
            
            return tool_name, args
        
        return None
    
    async def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Execute a tool with the given arguments."""
        tool = self.tools.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool Unknown: {tool_name}")
        
        logger.info(f"Tool Execute: {tool_name} with args: {args}")
        try:
            result = await tool(**args) if asyncio.iscoroutinefunction(tool) else tool(**args)
            logger.info(f"Tool Succeeded: {tool_name}")
            return result
        except Exception as e:
            logger.error(f"Tool Failed: {tool_name} - {e}")
            raise

    def _get_llm_response_bedrock(self, conversation):
        """Get response from Claude via Amazon Bedrock."""
        try:
            # Convert conversation format to Anthropic format
            messages = []
            for msg in conversation:
                role = "assistant" if msg["role"] == "assistant" else "user"
                if msg["role"] == "system" and len(messages) == 0:
                    # Handle system message at the beginning
                    messages.append({
                        "role": "user",
                        "content": [{"type": "text", "text": msg["content"]}]
                    })
                    continue
                elif msg["role"] == "system":
                    # Handle system messages elsewhere as user messages
                    role = "user"
                
                messages.append({
                    "role": role,
                    "content": [{"type": "text", "text": msg["content"]}]
                })
            
            # Prepare Claude API request
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": messages,
                "temperature": 0.2
            }
            
            # Log the request (truncated for brevity)
            logger.info(f"Bedrock request: {json.dumps(request_body)[:500]}...")
            
            # Call Bedrock API
            response = self.bedrock_client.invoke_model(
                modelId=self.cloud_model,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            content = response_body.get('content', [{}])[0].get('text', '')
            
            logger.info(f"Bedrock response: {content[:300]}...")
            return {'message': {'role': 'assistant', 'content': content}}
            
        except Exception as e:
            logger.error(f"Bedrock response error: {e}")
            return {'message': {'role': 'assistant', 'content': f'Error: {str(e)}'}}

    def _get_llm_response_ollama(self, conversation):
        """Get response from local Ollama with optional streaming."""
        if self.stream_llm:
            # Stream response and collect tokens
            full_response = ""
            logger.info("Streaming tokens:")
            for chunk in self.client.chat(
                model=self.local_model,
                messages=conversation,
                stream=True
            ):
                content = chunk.get('message', {}).get('content', '')
                if content:
                    logger.info(f"Token: {content}")
                    full_response += content
            
            # Create response object similar to non-streaming format
            return {'message': {'role': 'assistant', 'content': full_response}}
        else:
            # Non-streaming response
            try:
                response = self.client.chat(
                    model=self.local_model,
                    messages=conversation,
                    options={
                        "num_ctx": self.context_window
                    }
                )
                # Log context window usage
                prompt_tokens = response.get('prompt_eval_count', 0)
                total_tokens = prompt_tokens + response.get('eval_count', 0)
                logger.info(f"Context window usage: {prompt_tokens}/{self.context_window} tokens (prompt), {total_tokens} total tokens")
                
                logger.info(f"  Message ({response['message']['role']}): {response['message']['content'][:300]}...")
                return response
            except Exception as e:
                logger.error(f"LLM response error: {e}")
                # Return a minimal response to prevent crashes
                return {'message': {'role': 'assistant', 'content': f'Error: {str(e)}'}}
    
    def _get_llm_response(self, conversation):
        """Get response from either local or cloud LLM based on configuration."""
        if self.use_cloud_agent:
            return self._get_llm_response_bedrock(conversation)
        else:
            return self._get_llm_response_ollama(conversation)
    
    def _extract_song_id_from_finished(self, content: str) -> str:
        """Extract the song_id from a FINISHED message."""
        # Check for explicit song_id format first
        explicit_match = re.search(r'song[_-]id:?\s*["\']?([a-z0-9-]+)["\']?', content, re.IGNORECASE)
        if explicit_match:
            return explicit_match.group(1)
        
        # Look for the last Tool: generate_song_id result
        generate_id_result = re.search(r'Tool\s+generate_song_id\s+result:.*?"song_id":\s*"([^"]+)"', content, re.DOTALL)
        if generate_id_result:
            return generate_id_result.group(1)
            
        # Look for the last Tool: save_results call
        save_results_call = re.search(r'Tool:\s*save_results\(song_id="([^"]+)"', content)
        if save_results_call:
            return save_results_call.group(1)
        
        # Last resort: look for any word that looks like a song_id
        song_id_pattern = re.search(r'([a-z0-9][a-z0-9-]+[a-z0-9])', content)
        if song_id_pattern:
            return song_id_pattern.group(1)
            
        return "unknown_song_id"
    
    async def process_request(self, message: str) -> str:
        """Process a user request using the ReAct framework."""
        logger.info("-"*20)
        
        # Initialize conversation with system prompt and user message
        conversation = [
            {"role": "system", "content": self.prompt_path.read_text()},
            {"role": "user", "content": message}
        ]
        
        max_turns = 15  # Increased from 10 to give more chances to complete
        current_turn = 0
        last_song_id = None  # Track the last generated song_id
        
        while current_turn < max_turns:
            try:
                logger.info(f"[Turn {current_turn + 1}/{max_turns}]")
                
                # Log the request payload
                logger.info(f"Request:")
                for msg in conversation[-2:]:  # Show last 2 messages for context
                    logger.info(f"  Message ({msg['role']}): {msg['content'][:300]}...")

                response = self._get_llm_response(conversation)
                
                if not isinstance(response, dict) or 'message' not in response or 'content' not in response['message']:
                    raise ValueError(f"Unexpected response format from LLM: {response}")
                
                # Extract content from the message
                content = response.get('message', {}).get('content', '')
                if not content or not content.strip():
                    logger.warning("Received empty response from LLM")
                    conversation.append({"role": "system", "content": "Your last response was empty. Please process the previous result and specify the next tool to use, or indicate FINISHED if done."})
                    continue
                
                # Check if FINISHED
                if 'FINISHED' in content:
                    logger.info("LLM indicated task is complete")
                    song_id = self._extract_song_id_from_finished(content)
                    if song_id != "unknown_song_id":
                        logger.info(f"Extracted song_id from FINISHED message: {song_id}")
                        return song_id
                    elif last_song_id:
                        logger.info(f"Using last generated song_id: {last_song_id}")
                        return last_song_id
                    else:
                        logger.warning("No song_id found in FINISHED message and no previous song_id available")
                        return "unknown_song_id"
                
                # Parse the action
                action = self.parse_llm_action(content)
                
                if not action:
                    logger.warning("No tool call found in LLM response. Adding guidance and continuing.")
                    conversation.append({"role": "assistant", "content": content})
                    conversation.append({
                        "role": "system", 
                        "content": "I don't see a valid tool call. You must include a tool call in EXACTLY this format: Tool: tool_name(param1=\"value1\", param2=\"value2\"). Please try again."
                    })
                    continue
                
                # Execute the tool
                tool_name, tool_args = action
                logger.info(f"Executing tool: {tool_name}")
                logger.info(f"Arguments: {tool_args}")
                
                # Track song_id if this is a generate_song_id call
                if tool_name == "generate_song_id" and "artist" in tool_args and "title" in tool_args:
                    # Track the artist and title for later use if needed
                    self.last_artist = tool_args["artist"]
                    self.last_title = tool_args["title"]
                
                result = await self.execute_tool(tool_name, tool_args)
                logger.info(f"Tool execution complete")
                
                # If this was a generate_song_id call, store the result
                if tool_name == "generate_song_id" and isinstance(result, dict) and "song_id" in result:
                    last_song_id = result["song_id"]
                    logger.info(f"Saved song_id: {last_song_id}")
                
                # Add the interaction to conversation
                conversation.extend([
                    {"role": "assistant", "content": content},
                    {"role": "system", "content": f"Tool {tool_name} result: {json.dumps(result)}"}
                ])
                
                current_turn += 1
                
            except Exception as e:
                logger.error(f"❌ Error in turn {current_turn + 1}: {e}")
                logger.error(f"Stack trace:", exc_info=True)
                
                # Add more helpful error messages based on the error type
                if "missing 1 required positional argument: 'artist'" in str(e):
                    error_msg = "Error: The generate_song_id function requires both artist and title parameters. Please call it as: Tool: generate_song_id(artist=\"Artist Name\", title=\"Song Title\")"
                else:
                    error_msg = f"Error: {str(e)}. Please try a different approach."
                
                conversation.append({"role": "system", "content": error_msg})
                current_turn += 1
        
        # If we got here, we hit the maximum turns without completing
        if last_song_id:
            logger.warning(f"Reached maximum turns but returning last generated song_id: {last_song_id}")
            return last_song_id
            
        raise Exception("Reached maximum number of turns without completing the task")