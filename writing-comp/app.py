import streamlit as st
import requests
from enum import Enum
import json
from typing import Optional, List, Dict
import logging
import random
import boto3
import base64
from PIL import Image
from io import BytesIO

# Setup Custom Logging -----------------------
# Create a custom logger for your app only
logger = logging.getLogger('my_app')
logger.setLevel(logging.DEBUG)

# Remove any existing handlers to prevent duplicate logging
if logger.hasHandlers():
    logger.handlers.clear()

# Create file handler
fh = logging.FileHandler('app.log')
fh.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter('%(asctime)s - MY_APP - %(message)s')
fh.setFormatter(formatter)

# Add handler to logger
logger.addHandler(fh)

# Prevent propagation to root logger
logger.propagate = False

# State Management
class AppState(Enum):
    SETUP = "setup"
    PRACTICE = "practice"
    REVIEW = "review"

class MarathiLearningApp:
    def __init__(self):
        logger.debug("Initializing Marathi Learning App...")
        self.initialize_session_state()
        
        # Initialize AWS clients with appropriate error handling
        try:
            self.bedrock_client = boto3.client(
                service_name='bedrock-runtime',
                region_name='us-east-1'  # Change to your preferred region
            )
            logger.debug("Successfully initialized Bedrock client")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            st.error("Failed to connect to AWS services. Please check your credentials and try again.")
        
        # Load vocabulary after AWS setup
        self.load_vocabulary()
        
    def initialize_session_state(self):
        """Initialize or get session state variables"""
        if 'app_state' not in st.session_state:
            st.session_state.app_state = AppState.SETUP
        if 'current_sentence' not in st.session_state:
            st.session_state.current_sentence = ""
        if 'review_data' not in st.session_state:
            st.session_state.review_data = None
            
    def load_vocabulary(self):
        """Fetch vocabulary from API using group_id from query parameters or use default vocabulary"""
        try:
            # Get group_id from query parameters
            group_id = st.query_params.get('group_id', '')
            
            # If no group_id is provided, use default vocabulary
            if not group_id:
                logger.debug("No group_id provided, using default vocabulary")
                # Fallback to a default set of Marathi vocabulary
                self.vocabulary = {
                    "group_name": "Default Marathi Vocabulary",
                    "words": [
                        {"english": "water", "marathi": "पाणी"},
                        {"english": "food", "marathi": "अन्न"},
                        {"english": "house", "marathi": "घर"},
                        {"english": "book", "marathi": "पुस्तक"},
                        {"english": "friend", "marathi": "मित्र"},
                        {"english": "school", "marathi": "शाळा"},
                        {"english": "mother", "marathi": "आई"},
                        {"english": "father", "marathi": "वडील"},
                        {"english": "car", "marathi": "गाडी"},
                        {"english": "time", "marathi": "वेळ"},
                        {"english": "today", "marathi": "आज"},
                        {"english": "tomorrow", "marathi": "उद्या"},
                        {"english": "eat", "marathi": "खाणे"},
                        {"english": "drink", "marathi": "पिणे"},
                        {"english": "read", "marathi": "वाचणे"}
                    ]
                }
                return
                
            # Make API request with the actual group_id
            url = f'http://localhost:5000/api/groups/{group_id}/words/raw'
            logger.debug(url)
            response = requests.get(url)
            logger.debug(f"Response status: {response.status_code}")
            
            # Check if response is successful and contains data
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.debug(f"Received data for group: {data.get('group_name', 'unknown')}") 
                    self.vocabulary = data
                except requests.exceptions.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    st.error(f"Invalid JSON response from API: {response.text}")
                    # Fall back to default vocabulary
                    self._use_default_vocabulary()
            else:
                logger.error(f"API request failed: {response.status_code}")
                st.warning(f"Could not load vocabulary from API. Using default vocabulary instead.")
                # Fall back to default vocabulary
                self._use_default_vocabulary()
        except Exception as e:
            logger.error(f"Failed to load vocabulary: {e}")
            st.warning(f"Could not connect to vocabulary service. Using default vocabulary instead.")
            # Fall back to default vocabulary
            self._use_default_vocabulary()
            
    def _use_default_vocabulary(self):
        """Set up default vocabulary when API is unavailable"""
        self.vocabulary = {
            "group_name": "Default Marathi Vocabulary",
            "words": [
                {"english": "water", "marathi": "पाणी"},
                {"english": "food", "marathi": "अन्न"},
                {"english": "house", "marathi": "घर"},
                {"english": "book", "marathi": "पुस्तक"},
                {"english": "friend", "marathi": "मित्र"},
                {"english": "school", "marathi": "शाळा"},
                {"english": "mother", "marathi": "आई"},
                {"english": "father", "marathi": "वडील"},
                {"english": "car", "marathi": "गाडी"},
                {"english": "time", "marathi": "वेळ"},
                {"english": "today", "marathi": "आज"},
                {"english": "tomorrow", "marathi": "उद्या"},
                {"english": "eat", "marathi": "खाणे"},
                {"english": "drink", "marathi": "पिणे"},
                {"english": "read", "marathi": "वाचणे"}
            ]
        }

    def invoke_bedrock(self, model_id, prompt):
        """Call Amazon Bedrock model with the given prompt"""
        try:
            # Using Claude model on Bedrock
            logger.debug(f"Calling Bedrock with prompt: {prompt}")
            
            if model_id == "anthropic.claude-3-sonnet-20240229-v1:0":
                # Format for Claude
                payload = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "messages": [
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ]
                }
            else:
                # Format for other models
                payload = {
                    "prompt": prompt,
                    "max_tokens_to_sample": 1000,
                    "temperature": 0.7
                }
                
            response = self.bedrock_client.invoke_model(
                modelId=model_id,
                body=json.dumps(payload)
            )
            
            response_body = json.loads(response['body'].read())
            
            if model_id == "anthropic.claude-3-sonnet-20240229-v1:0":
                return response_body['content'][0]['text']
            else:
                return response_body.get('completion', '')
                
        except Exception as e:
            logger.error(f"Error calling Bedrock: {e}")
            return f"Error generating sentence: {str(e)}"

    def generate_sentence(self, word: dict) -> str:
        """Generate a sentence using Amazon Bedrock API"""
        marathi = word.get('marathi', '')
        
        prompt = f"""Generate a simple Marathi sentence using the word '{marathi}'.
        The grammar should be basic and suitable for beginners.
        You can use the following vocabulary to construct a simple sentence:
        - simple objects eg. book, car, food, water
        - simple verbs, to drink, to eat, to meet
        - simple times eg. tomorrow, today, yesterday
        
        Please provide the response in this format:
        Marathi: [sentence in Marathi script]
        English: [English translation]
        """
        
        logger.debug(f"Generating sentence for word: {marathi}")
        return self.invoke_bedrock("anthropic.claude-3-sonnet-20240229-v1:0", prompt)

    def transcribe_image(self, image_data):
        """Transcribe Marathi text from image using Amazon Textract or fallback to Claude Vision"""
        try:
            # Convert streamlit uploaded file to bytes
            bytes_data = image_data.getvalue()
            
            try:
                # Try Amazon Textract first
                textract = boto3.client('textract', region_name='us-east-1')
                response = textract.detect_document_text(
                    Document={'Bytes': bytes_data}
                )
                
                # Extract text from response
                extracted_text = ""
                for item in response['Blocks']:
                    if item['BlockType'] == 'LINE':
                        extracted_text += item['Text'] + " "
                
                if extracted_text.strip():
                    return extracted_text.strip()
                else:
                    # If Textract returned no text, try the fallback method
                    logger.info("Textract returned no text, falling back to Claude Vision")
                    return self._vision_fallback_ocr(image_data)
                    
            except Exception as textract_error:
                # If Textract fails, try the fallback method
                logger.error(f"Textract error: {textract_error}")
                logger.info("Falling back to Claude Vision for OCR")
                return self._vision_fallback_ocr(image_data)
                
        except Exception as e:
            logger.error(f"Error in transcription: {e}")
            return "Error in transcription. Please try again with a clearer image."
            
    def _vision_fallback_ocr(self, image_data):
        """Fallback OCR using Claude's vision capabilities"""
        try:
            # Convert image to base64
            image_bytes = image_data.getvalue()
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # Create a vision prompt for Claude
            prompt = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "This image contains Marathi text. Please extract and transcribe ONLY the Marathi text exactly as written. Do not translate it. Only respond with the extracted Marathi text, nothing else."
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": base64_image
                                }
                            }
                        ]
                    }
                ]
            }
            
            # Call Claude model with vision capabilities (if available)
            try:
                response = self.bedrock_client.invoke_model(
                    modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                    body=json.dumps(prompt)
                )
                
                response_body = json.loads(response['body'].read())
                return response_body['content'][0]['text'].strip()
                
            except Exception as claude_error:
                logger.error(f"Claude vision error: {claude_error}")
                return "Could not extract text from image. Please try again with a clearer image."
                
        except Exception as e:
            logger.error(f"Vision fallback error: {e}")
            return "Error processing image. Please try again."

    def translate_text(self, text):
        """Translate Marathi text to English using Amazon Bedrock"""
        prompt = f"Translate this Marathi text to English: {text}"
        return self.invoke_bedrock("anthropic.claude-3-sonnet-20240229-v1:0", prompt)

    def grade_submission(self, image_data) -> Dict:
        """Process image submission and grade it"""
        # Transcribe the image
        transcription = self.transcribe_image(image_data)
        
        # Translate the transcription
        translation = self.translate_text(transcription)
        
        # Grade the translation against the target sentence
        target_sentence = st.session_state.current_sentence
        
        # Extract English part from the target sentence
        english_target = ""
        for line in target_sentence.split('\n'):
            if line.startswith('English:'):
                english_target = line.replace('English:', '').strip()
                break
        
        grading_prompt = f"""
        Grade this Marathi writing sample:
        Target English sentence: {english_target}
        Student's Marathi: {transcription}
        Literal translation: {translation}
        
        Grade based on:
        - Accuracy of translation compared to target sentence
        - Grammar correctness
        - Writing style and naturalness
        
        Use S/A/B/C grading scale where:
        S: Perfect or near-perfect
        A: Very good with minor issues
        B: Good but needs improvement
        C: Significant issues to address
        
        Provide your assessment in this format:
        Grade: [S/A/B/C]
        Feedback: [Your detailed feedback]
        """
        
        grading_response = self.invoke_bedrock("anthropic.claude-3-sonnet-20240229-v1:0", grading_prompt)
        
        # Parse grading response
        grade = "C"  # Default grade
        feedback = "Unable to determine feedback"
        
        for line in grading_response.split('\n'):
            if line.startswith('Grade:'):
                grade = line.replace('Grade:', '').strip()
            elif line.startswith('Feedback:'):
                feedback = line.replace('Feedback:', '').strip()
        
        return {
            "transcription": transcription,
            "translation": translation,
            "grade": grade,
            "feedback": feedback
        }

    def render_setup_state(self):
        """Render the setup state UI"""
        logger.debug("Entering render_setup_state")
        st.title("Marathi Writing Practice")
        
        # Display the vocabulary group name if available
        if self.vocabulary and self.vocabulary.get("group_name"):
            st.subheader(f"Vocabulary Group: {self.vocabulary['group_name']}")
            
        # Add key to button to ensure proper state management
        generate_button = st.button("Generate Sentence", key="generate_sentence_btn")
        logger.debug(f"Generate button state: {generate_button}")
        
        if generate_button:
            logger.info("Generate button clicked")
            st.session_state['last_click'] = 'generate_button'
            logger.debug(f"Session state after click: {st.session_state}")
            # Pick a random word from vocabulary
            if not self.vocabulary.get('words'):
                st.error("No words found in the vocabulary group")
                return
                
            word = random.choice(self.vocabulary['words'])
            logger.debug(f"Selected word: {word.get('english')} - {word.get('marathi')}")
            
            # Generate and display the sentence
            sentence = self.generate_sentence(word)
            st.markdown("### Generated Sentence")
            st.write(sentence)
            
            # Store the current sentence and move to practice state
            st.session_state.current_sentence = sentence
            st.session_state.app_state = AppState.PRACTICE
            st.experimental_rerun()

    def render_practice_state(self):
        """Render the practice state UI"""
        st.title("Practice Marathi")
        
        # Extract English part from the target sentence
        english_target = ""
        for line in st.session_state.current_sentence.split('\n'):
            if line.startswith('English:'):
                english_target = line.replace('English:', '').strip()
                break
                
        st.write(f"English Sentence: {english_target}")
        
        uploaded_file = st.file_uploader("Upload your written Marathi", type=['png', 'jpg', 'jpeg'])
        
        if st.button("Submit for Review") and uploaded_file:
            st.session_state.review_data = self.grade_submission(uploaded_file)
            st.session_state.app_state = AppState.REVIEW
            st.experimental_rerun()

    def render_review_state(self):
        """Render the review state UI"""
        st.title("Review")
        
        # Extract English part from the target sentence
        english_target = ""
        for line in st.session_state.current_sentence.split('\n'):
            if line.startswith('English:'):
                english_target = line.replace('English:', '').strip()
                break
                
        st.write(f"English Sentence: {english_target}")
        
        review_data = st.session_state.review_data
        st.subheader("Your Submission")
        st.write(f"Transcription: {review_data['transcription']}")
        st.write(f"Translation: {review_data['translation']}")
        st.write(f"Grade: {review_data['grade']}")
        st.write(f"Feedback: {review_data['feedback']}")
        
        if st.button("Next Question"):
            st.session_state.app_state = AppState.SETUP
            st.session_state.current_sentence = ""
            st.session_state.review_data = None
            st.experimental_rerun()

    def run(self):
        """Main app loop"""
        if st.session_state.app_state == AppState.SETUP:
            self.render_setup_state()
        elif st.session_state.app_state == AppState.PRACTICE:
            self.render_practice_state()
        elif st.session_state.app_state == AppState.REVIEW:
            self.render_review_state()

# Run the app
if __name__ == "__main__":
    app = MarathiLearningApp()
    app.run()