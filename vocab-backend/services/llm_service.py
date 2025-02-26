import json
import boto3
from typing import Dict, Any, Optional

from config import AWS_REGION, BEDROCK_MODEL_ID
from utils.validators import format_llm_response

class BedrockLLMService:
    def __init__(self, region_name: str = AWS_REGION, model_id: str = BEDROCK_MODEL_ID):
        """Initialize Bedrock client with the given region and model ID."""
        self.bedrock_client = boto3.client(
            service_name="bedrock-runtime", 
            region_name=region_name
        )
        self.model_id = model_id
    
    def generate_words(self, group_name: str) -> Optional[Dict[str, Any]]:
        """
        Generate words for a given group using Amazon Bedrock LLM.
        
        Args:
            group_name: The name of the word group
            
        Returns:
            A dictionary containing the group name and list of words, or None if failed
        """
        # Create the prompt for word generation
        prompt = self._create_prompt(group_name)
        
        try:
            # Call Amazon Bedrock with the appropriate model
            response = self._invoke_bedrock(prompt)
            
            if not response:
                print("No response from Bedrock")
                return None
                
            # Format and validate the response
            formatted_response, error = format_llm_response(response)
            
            if error:
                print(f"Error formatting LLM response: {error}")
                return None
                
            return formatted_response
        except Exception as e:
            print(f"Error calling LLM: {str(e)}")
            return None
    
    def _invoke_bedrock(self, prompt: str) -> Optional[str]:
        """Invoke Bedrock with the given prompt."""
        try:
            messages = [{
                "role": "user",
                "content": [{
                    "text": prompt
                }]
            }]
            
            response = self.bedrock_client.converse(
                modelId=self.model_id,
                messages=messages,
                inferenceConfig={"temperature": 0.2}
            )
            
            return response['output']['message']['content'][0]['text']
        except Exception as e:
            print(f"Error invoking Bedrock: {str(e)}")
            return None
    
    def _create_prompt(self, group_name: str) -> str:
        """Create a prompt for the LLM to generate words for a group."""
        return f"""
        I need you to generate a list of 10 words for the category "{group_name}".
        
        For each word, provide both the English word and its Marathi translation.
        
        STRICTLY return your response as valid JSON with the following structure:
        
        {{
          "group_name": "{group_name}",
          "words": [
            {{
              "english": "example_word_1",
              "marathi": "मराठी_शब्द_1"
            }},
            {{
              "english": "example_word_2",
              "marathi": "मराठी_शब्द_2"
            }}
          ]
        }}
        
        Include exactly 10 words in your response.
        Do not include ANY text before or after the JSON.
        Do not include explanations or additional notes.
        """