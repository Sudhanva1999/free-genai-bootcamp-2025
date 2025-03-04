import ollama
import boto3
import json
import logging
import re
import asyncio
import os
from typing import List, Dict, Any, Optional, Tuple
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
    
    Args:
        available_ram_gb (float): Available RAM in gigabytes
        safety_factor (float): Factor to multiply by for safety margin (default 0.8)
        
    Returns:
        int: Recommended context window size in tokens
        
    Note:
        Based on observation that 128K tokens requires ~58GB RAM
        Ratio is approximately 0.45MB per token (58GB/131072 tokens)
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
        self.prompt_path = self.base_path / "prompts" / "Lyrics-Agent.md"
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
        
        # State tracking
        self.current_song_id = None
        self.extracted_lyrics = None
        self.extracted_vocabulary = None
        
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
    
    def parse_llm_action(self, content: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Parse the LLM's response to extract tool name and arguments with enhanced robustness."""
        logger.debug(f"Parsing LLM action from content: {content[:100]}...")
        
        # First try with the standard pattern
        match = re.search(r'Tool:\s*(\w+)\((.*?)\)', content, re.DOTALL)
        if match:
            tool_name = match.group(1)
            args_str = match.group(2).strip()
            logger.debug(f"Found tool call: {tool_name}({args_str[:50]}...)")
            
            # Parse arguments with more robust pattern matching
            args = {}
            
            # Enhanced pattern matching for arguments
            key_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)'
            
            # Try to extract key-value pairs using regex with ability to handle multi-line values
            # First look for standard quoted arguments
            for arg_match in re.finditer(f'{key_pattern}\s*=\s*"((?:[^"\\\\]|\\\\.)*)"\s*,?', args_str, re.DOTALL):
                key = arg_match.group(1)
                value = arg_match.group(2).replace('\\"', '"')
                args[key] = value
                logger.debug(f"Extracted key-value pair: {key}={value[:50]}...")
            
            # If no arguments were extracted, try with the more permissive pattern for incomplete strings
            if not args and tool_name:
                # For partial or broken argument strings
                arg_match = re.search(f'{key_pattern}\s*=\s*"([^"]*)', args_str)
                if arg_match:
                    key = arg_match.group(1)
                    value = arg_match.group(2)
                    
                    # Take the rest of the content up to a reasonable limit as the value
                    # This handles cases where the closing quote is missing
                    if key and value:
                        # Look for a natural endpoint for the value (if we can find one)
                        end_indicators = ['")', '",', '" )', '")']
                        
                        # Find where the value should end by looking for indicators
                        end_index = None
                        for indicator in end_indicators:
                            idx = content.find(indicator, content.find(value))
                            if idx != -1:
                                if end_index is None or idx < end_index:
                                    end_index = idx
                        
                        # If no proper end found, take a best guess by grabbing text up to closing braces
                        if end_index is None:
                            # Extract everything up to the next closing parenthesis or end of text
                            remaining = content[content.find(value) + len(value):]
                            next_close_paren = remaining.find(')')
                            if next_close_paren != -1:
                                extended_value = value + remaining[:next_close_paren]
                            else:
                                # Limit to a reasonable size if no closing parenthesis
                                extended_value = value + remaining[:1000]  
                            args[key] = extended_value
                        else:
                            # Use the identified end point
                            end_limit = end_index - content.find(value)
                            extended_value = value + content[content.find(value) + len(value):content.find(value) + end_limit]
                            args[key] = extended_value
                        
                        logger.debug(f"Reconstructed broken argument: {key}={args[key][:50]}...")
            
            # Enhanced detection for Claude (via Bedrock) format where it splits quotes across lines
            if not args and tool_name and ('extract_vocabulary' in tool_name or 'save_results' in tool_name):
                # Handle the specific case for text argument which is often split across multiple lines
                text_match = re.search(r'text="(.*?)(?:"|$)', args_str, re.DOTALL)
                if text_match:
                    args['text'] = text_match.group(1).strip()
                    
                # For song_id argument in save_results
                if 'save_results' in tool_name:
                    song_id_match = re.search(r'song_id="([^"]*)"', args_str)
                    if song_id_match:
                        args['song_id'] = song_id_match.group(1)
                    elif self.current_song_id:
                        # Use the stored song_id if available
                        args['song_id'] = self.current_song_id
                        logger.info(f"Using stored song_id: {self.current_song_id}")
            
            if args:
                return tool_name, args
        
        # If we reach here, either no match was found or args couldn't be parsed
        # Try an alternative formatting that some models might use
        alt_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)\((.*?)\)', content, re.DOTALL)
        if alt_match:
            tool_name = alt_match.group(1)
            args_str = alt_match.group(2)
            
            # Do we have a known tool with this name?
            if tool_name in self.tools.tools:
                logger.debug(f"Found alternative tool call format: {tool_name}")
                args = {}
                
                # Parse arguments
                for arg_part in args_str.split(','):
                    kv_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.*)', arg_part.strip())
                    if kv_match:
                        key = kv_match.group(1)
                        value = kv_match.group(2).strip()
                        # Remove quotes if present
                        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        args[key] = value
                
                if args:
                    return tool_name, args
        
        # Handle FINISHED state
        if 'FINISHED' in content and self.current_song_id:
            logger.info(f"Detected FINISHED state with song_id: {self.current_song_id}")
            # Create a pseudo-call to save_results if we have required data
            if self.extracted_lyrics:
                return 'save_results', {
                    'song_id': self.current_song_id,
                    'lyrics': self.extracted_lyrics,
                    'vocabulary': self.extracted_vocabulary
                }
        
        logger.warning("No valid tool call could be parsed")
        return None
    
    async def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Execute a tool with the given arguments."""
        tool = self.tools.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool Unknown: {tool_name}")
        
        logger.info(f"Tool Execute: {tool_name} with args: {args}")
        try:
            # Special handling for each tool type
            if tool_name == 'get_page_content' and 'url' in args:
                result = await tool(**args) if asyncio.iscoroutinefunction(tool) else tool(**args)
                
                # Store lyrics for potential fallback use
                if isinstance(result, dict) and 'marathi_lyrics' in result and result['marathi_lyrics']:
                    self.extracted_lyrics = result['marathi_lyrics']
                    logger.info(f"Stored lyrics ({len(self.extracted_lyrics)} chars)")
                
                return result
                
            elif tool_name == 'extract_vocabulary' and 'text' in args:
                # If using cloud, ensure we use Bedrock-compatible extraction
                if self.use_cloud_agent:
                    # Force text to be clean
                    # Normalize newlines and strip any strange characters
                    text = re.sub(r'\s+', ' ', args['text']).strip()
                    # For Marathi text, replace non-Devanagari characters with spaces
                    text = re.sub(r'[^\u0900-\u097F\s]', ' ', text)
                    args['text'] = text
                
                result = await tool(**args) if asyncio.iscoroutinefunction(tool) else tool(**args)
                # Store vocabulary for potential fallback use
                if result:
                    self.extracted_vocabulary = result
                    logger.info(f"Stored vocabulary ({len(result)} items)")
                return result
                
            elif tool_name == 'generate_song_id':
                result = await tool(**args) if asyncio.iscoroutinefunction(tool) else tool(**args)
                # Store song_id for potential fallback use
                if isinstance(result, dict) and 'song_id' in result:
                    self.current_song_id = result['song_id']
                    logger.info(f"Captured song_id: {self.current_song_id}")
                return result
                
            elif tool_name == 'save_results':
                # Ensure we have all necessary data
                if 'song_id' not in args and self.current_song_id:
                    args['song_id'] = self.current_song_id
                
                if 'lyrics' not in args and self.extracted_lyrics:
                    args['lyrics'] = self.extracted_lyrics
                
                if 'vocabulary' not in args and self.extracted_vocabulary:
                    args['vocabulary'] = self.extracted_vocabulary
                    
                # Verify we have minimal required data
                if 'song_id' not in args:
                    raise ValueError("Missing required argument 'song_id' for save_results")
                
                if 'lyrics' not in args:
                    raise ValueError("Missing required argument 'lyrics' for save_results")
                
                # Execute the tool
                result = await tool(**args) if asyncio.iscoroutinefunction(tool) else tool(**args)
                return result
            
            else:
                # Standard execution for other tools
                result = await tool(**args) if asyncio.iscoroutinefunction(tool) else tool(**args)
                return result
                
        except Exception as e:
            logger.error(f"Tool Failed: {tool_name} - {e}")
            
            # Special fallback for extract_vocabulary
            if tool_name == 'extract_vocabulary':
                # Use the fallback extraction method directly
                from tools.extract_vocabulary import _extract_fallback
                if 'text' in args:
                    fallback_result = _extract_fallback(args['text'])
                    self.extracted_vocabulary = fallback_result
                    logger.info(f"Used fallback extraction, got {len(fallback_result)} items")
                    return fallback_result
            
            raise
    
    def _get_llm_response_bedrock(self, conversation: List[Dict[str, str]]) -> Dict[str, Any]:
        """Get response from Claude via Amazon Bedrock.
        
        Args:
            conversation (list): List of conversation messages
            
        Returns:
            dict: Response object with 'content' key
        """
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

    def _get_llm_response_ollama(self, conversation: List[Dict[str, str]]) -> Dict[str, Any]:
        """Get response from local Ollama with optional streaming.
        
        Args:
            conversation (list): List of conversation messages
            
        Returns:
            dict: Response object with 'content' key
        """
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
    
    def _get_llm_response(self, conversation: List[Dict[str, str]]) -> Dict[str, Any]:
        """Get response from either local or cloud LLM based on configuration."""
        if self.use_cloud_agent:
            return self._get_llm_response_bedrock(conversation)
        else:
            return self._get_llm_response_ollama(conversation)
    
    def _enhance_prompt_for_claude(self, system_prompt: str) -> str:
        """Add special instructions for Claude to format tool calls correctly."""
        tool_instruction = """
IMPORTANT: When calling tools, please format your calls exactly like this:
Tool: tool_name(arg1="value1", arg2="value2")

The entire tool call must be on a single line. DO NOT split the arguments across multiple lines.
For text arguments that contain multiple lines, use a single line with escaped newlines.

Example of CORRECT format:
Tool: extract_vocabulary(text="line1\\nline2\\nline3")

Example of INCORRECT format:
Tool: extract_vocabulary(text="line1
line2
line3")

Always close the parenthesis on the same line as the opening parenthesis.
"""
        return system_prompt + "\n\n" + tool_instruction
    
    async def process_request(self, message: str) -> str:
        """Process a user request using the ReAct framework."""
        logger.info("-"*20)
        
        # Reset state for new request
        self.current_song_id = None
        self.extracted_lyrics = None
        self.extracted_vocabulary = None
        
        # Read system prompt and enhance it for Claude
        system_prompt = self.prompt_path.read_text()
        if self.use_cloud_agent:
            system_prompt = self._enhance_prompt_for_claude(system_prompt)
        
        # Initialize conversation with system prompt and user message
        conversation = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        max_turns = 10
        current_turn = 0
        
        while current_turn < max_turns:
            try:
                logger.info(f"[Turn {current_turn + 1}/{max_turns}]")
                try:
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

                    # Check for FINISHED first since it might not have a tool call
                    if 'FINISHED' in content:
                        # Extract song_id from the response
                        song_id_match = re.search(r'song_id[:\s="\']+([a-zA-Z0-9_-]+)', content)
                        if song_id_match:
                            self.current_song_id = song_id_match.group(1)
                            logger.info(f"Task complete. Song ID: {self.current_song_id}")
                        else:
                            logger.warning("FINISHED but no song_id found in response")
                            
                        # If we have lyrics but no vocabulary, try to extract it now
                        if self.extracted_lyrics and not self.extracted_vocabulary and self.current_song_id:
                            try:
                                logger.info("Attempting vocabulary extraction as final step")
                                self.extracted_vocabulary = await extract_vocabulary(self.extracted_lyrics)
                                logger.info(f"Final vocabulary extraction: {len(self.extracted_vocabulary)} items")
                            except Exception as e:
                                logger.error(f"Final vocabulary extraction failed: {e}")
                        
                        # Final save to ensure we have output files
                        if self.current_song_id:
                            try:
                                # Save with available data
                                logger.info("Final save attempt with available data")
                                lyrics = self.extracted_lyrics or "No lyrics were extracted"
                                save_results(
                                    song_id=self.current_song_id, 
                                    lyrics=lyrics,
                                    vocabulary=self.extracted_vocabulary,
                                    lyrics_path=self.lyrics_path,
                                    vocabulary_path=self.vocabulary_path
                                )
                            except Exception as e:
                                logger.error(f"Final save attempt failed: {e}")
                                
                        # Return the song ID if we have one, or generate one as a last resort
                        if self.current_song_id:
                            return self.current_song_id
                        
                        # Last resort - generate a time-based ID
                        import time
                        self.current_song_id = f"unknown-song-{int(time.time())}"
                        logger.warning(f"Generated fallback song_id: {self.current_song_id}")
                        return self.current_song_id

                    # Parse the action
                    action = self.parse_llm_action(content)
                    
                    if not action:
                        if current_turn >= 3:  # After a few attempts, try to extract vocabulary directly
                            # If we have lyrics but haven't executed extract_vocabulary, try to do it automatically
                            if self.extracted_lyrics and not self.extracted_vocabulary:
                                logger.info("No tool call found, but we have lyrics. Trying direct vocabulary extraction.")
                                try:
                                    result = await extract_vocabulary(self.extracted_lyrics)
                                    self.extracted_vocabulary = result
                                    logger.info(f"Direct vocabulary extraction: {len(result)} items")
                                    
                                    # Add result to conversation
                                    conversation.extend([
                                        {"role": "assistant", "content": content},
                                        {"role": "system", "content": f"I've extracted vocabulary directly: {len(result)} items. Please generate a song_id or proceed to save_results."}
                                    ])
                                    current_turn += 1
                                    continue
                                except Exception as e:
                                    logger.error(f"Direct vocabulary extraction failed: {e}")
                            
                            # If we have lyrics but no song ID, try to generate one
                            if self.extracted_lyrics and not self.current_song_id:
                                logger.info("No tool call found, but we have lyrics. Trying to generate song_id.")
                                try:
                                    # Extract artist and title from user message or use defaults
                                    artist = "unknown_artist"
                                    title = "unknown_song"
                                    
                                    # Try to extract title from user message
                                    title_match = re.search(r'(?:find|get|search).*lyrics.*\s+for\s+(.+?)(?:\s+version|\s+by|\s+lyrics|\s+$)', message, re.IGNORECASE)
                                    if title_match:
                                        title = title_match.group(1).strip()
                                    
                                    result = generate_song_id(artist=artist, title=title)
                                    self.current_song_id = result["song_id"]
                                    logger.info(f"Auto-generated song_id: {self.current_song_id}")
                                    
                                    # Add result to conversation
                                    conversation.extend([
                                        {"role": "assistant", "content": content},
                                        {"role": "system", "content": f"I've generated a song_id: {self.current_song_id}. Please proceed to save_results."}
                                    ])
                                    current_turn += 1
                                    continue
                                except Exception as e:
                                    logger.error(f"Auto song_id generation failed: {e}")
                        
                        logger.warning("No tool call found in LLM response")
                        # For Bedrock/Claude, add explicit instructions to make it correctly format tool calls
                        if self.use_cloud_agent:
                            tool_format_reminder = """
I need you to call a tool using the exact format:
Tool: tool_name(arg1="value1", arg2="value2")

The entire call must be on a single line with no line breaks in the arguments.
Do not split arguments across multiple lines.
"""
                            conversation.append({"role": "assistant", "content": content})
                            conversation.append({"role": "system", "content": tool_format_reminder})
                        else:
                            conversation.append({"role": "assistant", "content": content})
                            conversation.append({"role": "system", "content": "Please specify a tool to use in the format 'Tool: tool_name(arg1=\"value1\")' or indicate FINISHED if done."})
                        continue
                        
                except Exception as e:
                    logger.error(f"Error getting LLM response: {e}")
                    logger.debug("Last conversation state:", exc_info=True)
                    for msg in conversation[-2:]:
                        logger.debug(f"Message ({msg['role']}): {msg['content']}")
                    
                    # Try to recover by prompting for next step
                    conversation.append({"role": "system", "content": f"Error: {str(e)}. Please try a different approach or continue with the next step."})
                    current_turn += 1
                    continue
                
                # Execute the tool
                tool_name, tool_args = action
                logger.info(f"Executing tool: {tool_name}")
                logger.info(f"Arguments: {tool_args}")
                
                try:
                    result = await self.execute_tool(tool_name, tool_args)
                    logger.info(f"Tool execution complete")
                    
                    # Check if we got a song_id from generate_song_id
                    if tool_name == "generate_song_id" and isinstance(result, dict) and "song_id" in result:
                        self.current_song_id = result["song_id"]
                        logger.info(f"Captured song_id: {self.current_song_id}")
                    
                    # Record lyrics from get_page_content
                    if tool_name == "get_page_content" and isinstance(result, dict):
                        if "marathi_lyrics" in result and result["marathi_lyrics"]:
                            self.extracted_lyrics = result["marathi_lyrics"]
                            logger.info(f"Captured lyrics: {len(self.extracted_lyrics)} chars")
                    
                    # Record vocabulary from extract_vocabulary
                    if tool_name == "extract_vocabulary" and isinstance(result, list):
                        self.extracted_vocabulary = result
                        logger.info(f"Captured vocabulary: {len(self.extracted_vocabulary)} items")
                    
                    # Add the interaction to conversation
                    conversation.extend([
                        {"role": "assistant", "content": content},
                        {"role": "system", "content": f"Tool {tool_name} result: {json.dumps(result)}"}
                    ])
                except Exception as e:
                    logger.error(f"Tool execution failed: {e}", exc_info=True)
                    
                    # Special handling for specific tools
                    if tool_name == "extract_vocabulary":
                        # Create fallback vocabulary extraction
                        logger.info("Using fallback vocabulary extraction")
                        from tools.extract_vocabulary import _extract_fallback
                        if 'text' in tool_args:
                            fallback_result = _extract_fallback(tool_args["text"])
                            self.extracted_vocabulary = fallback_result
                            logger.info(f"Fallback extracted {len(fallback_result)} vocabulary items")
                            
                            # Add fallback result to conversation
                            conversation.extend([
                                {"role": "assistant", "content": content},
                                {"role": "system", "content": f"Tool {tool_name} fallback result: {json.dumps(fallback_result)}"}
                            ])
                        else:
                            conversation.extend([
                                {"role": "assistant", "content": content},
                                {"role": "system", "content": f"Error in {tool_name}: {str(e)}. Please try again with valid text."}
                            ])
                    elif tool_name == "save_results":
                        # Try to save with what we have
                        try:
                            logger.info("Attempting fallback save_results")
                            song_id = tool_args.get('song_id', self.current_song_id)
                            if not song_id:
                                # Generate a default ID if none exists
                                song_id = f"unknown-song-{int(time.time())}"
                                self.current_song_id = song_id
                            
                            lyrics = tool_args.get('lyrics', self.extracted_lyrics)
                            if not lyrics:
                                lyrics = "No lyrics were extracted"
                            
                            vocabulary = tool_args.get('vocabulary', self.extracted_vocabulary)
                            
                            save_result = save_results(
                                song_id=song_id, 
                                lyrics=lyrics, 
                                vocabulary=vocabulary,
                                lyrics_path=self.lyrics_path,
                                vocabulary_path=self.vocabulary_path
                            )
                            logger.info(f"Fallback save completed with song_id: {save_result}")
                            
                            # Add fallback result to conversation
                            conversation.extend([
                                {"role": "assistant", "content": content},
                                {"role": "system", "content": f"Tool {tool_name} fallback result: {json.dumps({'song_id': save_result})}"}
                            ])
                        except Exception as e2:
                            logger.error(f"Fallback save failed: {e2}")
                            conversation.extend([
                                {"role": "assistant", "content": content},
                                {"role": "system", "content": f"Error in {tool_name}: {str(e)}. Fallback save also failed: {str(e2)}"}
                            ])
                    else:
                        # Generic error handling for other tools
                        conversation.extend([
                            {"role": "assistant", "content": content},
                            {"role": "system", "content": f"Error in {tool_name}: {str(e)}. Please try a different approach."}
                        ])
                
                current_turn += 1
                
            except Exception as e:
                logger.error(f"❌ Error in turn {current_turn + 1}: {e}")
                logger.error(f"Stack trace:", exc_info=True)
                conversation.append({"role": "system", "content": f"Error: {str(e)}. Please try a different approach."})
                current_turn += 1
        
        # If we reach max turns, ensure we have a song ID to return
        if not self.current_song_id:
            # Look for a potential song ID in the conversation
            for msg in conversation:
                if msg["role"] == "system" and "Tool generate_song_id result" in msg["content"]:
                    try:
                        # Try to parse the JSON and extract song_id
                        result_text = msg["content"].split("Tool generate_song_id result: ")[1]
                        result = json.loads(result_text)
                        if "song_id" in result:
                            self.current_song_id = result["song_id"]
                            logger.info(f"Found song_id in conversation: {self.current_song_id}")
                            break
                    except:
                        continue
        
        # Emergency measures if we still don't have what we need
        try:
            # If we have lyrics but no vocabulary, try a final extraction
            if self.extracted_lyrics and not self.extracted_vocabulary:
                try:
                    logger.info("Final attempt at vocabulary extraction")
                    self.extracted_vocabulary = await extract_vocabulary(self.extracted_lyrics)
                    logger.info(f"Final vocabulary extraction: {len(self.extracted_vocabulary)} items")
                except Exception as e:
                    logger.error(f"Final vocabulary extraction failed: {e}")
                    # Use fallback extraction
                    from tools.extract_vocabulary import _extract_fallback
                    self.extracted_vocabulary = _extract_fallback(self.extracted_lyrics)
                    logger.info(f"Fallback vocabulary extraction: {len(self.extracted_vocabulary)} items")
            
            # If we still don't have a song ID, generate one
            if not self.current_song_id:
                import time
                # Extract title from user message if possible
                title_match = re.search(r'(?:find|get|search).*lyrics.*\s+for\s+(.+?)(?:\s+version|\s+by|\s+lyrics|\s+$)', message, re.IGNORECASE)
                if title_match:
                    title = title_match.group(1).strip()
                    result = generate_song_id(artist="unknown_artist", title=title)
                    self.current_song_id = result["song_id"]
                else:
                    self.current_song_id = f"unknown-song-{int(time.time())}"
                logger.warning(f"Generated emergency song_id: {self.current_song_id}")
            
            # Final save to ensure we have output files
            if self.current_song_id:
                lyrics = self.extracted_lyrics or "No lyrics were extracted"
                save_results(
                    song_id=self.current_song_id, 
                    lyrics=lyrics,
                    vocabulary=self.extracted_vocabulary,
                    lyrics_path=self.lyrics_path,
                    vocabulary_path=self.vocabulary_path
                )
                logger.info(f"Emergency save completed")
        except Exception as e:
            logger.error(f"Emergency measures failed: {e}")
        
        logger.warning("Reached maximum number of turns without proper completion")
        return self.current_song_id