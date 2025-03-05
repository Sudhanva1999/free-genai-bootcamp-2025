import streamlit as st
import boto3
import json
import os
import time
import sounddevice as sd
import numpy as np
import io
from scipy.io.wavfile import write
from PIL import Image
import base64
from tempfile import NamedTemporaryFile
from google.cloud import speech
import soundfile as sf
from pydub import AudioSegment

# Set page configuration
st.set_page_config(
    page_title="Marathi Speaking Practice",
    page_icon="🗣️",
    layout="centered"
)

# Constants
SAMPLE_RATE = 16000
MAX_RECORDING_SECONDS = 30
TEMP_DIR = "temp"
WAV_FILE = os.path.join(TEMP_DIR, "recording.wav")
MP3_FILE = os.path.join(TEMP_DIR, "recording.mp3")
IMAGE_FILE = os.path.join(TEMP_DIR, "generated_image.png")

# Create temp directory if it doesn't exist
os.makedirs(TEMP_DIR, exist_ok=True)

def setup_bedrock_client():
    """Initialize and return an Amazon Bedrock client."""
    try:
        # Setup with standard boto3 credentials config (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY)
        bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=st.session_state.get('aws_region', 'us-east-1')
        )
        return bedrock_client
    except Exception as e:
        st.error(f"Failed to initialize Bedrock client: {str(e)}")
        st.error("Please check your AWS credentials and region settings.")
        return None

def generate_image(topic):
    """Generate an image related to the given topic using Stability AI."""
    bedrock_client = setup_bedrock_client()
    if not bedrock_client:
        return None
    
    try:
        prompt = f"A clear, educational image showing {topic} in Maharashtra, India. Suitable for language learning. Photorealistic."
        
        body = json.dumps({
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 8,
            "steps": 50,
            "seed": int(time.time()) % 10000
        })
        
        response = bedrock_client.invoke_model(
            modelId="stability.stable-diffusion-xl-v1",
            body=body
        )
        
        response_body = json.loads(response.get("body").read())
        image_bytes = base64.b64decode(response_body.get("artifacts")[0].get("base64"))
        
        # Save image locally
        with open(IMAGE_FILE, "wb") as f:
            f.write(image_bytes)
        
        return Image.open(io.BytesIO(image_bytes))
    
    except Exception as e:
        st.error(f"Failed to generate image: {str(e)}")
        return None

def record_audio():
    """Record audio from the user for up to 30 seconds and save as MP3."""
    st.write("Recording will automatically stop after 30 seconds.")
    
    recording = st.empty()
    recording.write("🔴 Recording... Speak in Marathi about the topic while looking at the image.")
    
    # Initialize recording
    audio_data = []
    
    def callback(indata, frames, time, status):
        if status:
            st.error(f"Stream error: {status}")
        audio_data.append(indata.copy())
    
    # Start recording
    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=callback):
            remaining = st.empty()
            progress_bar = st.progress(0)
            
            for i in range(MAX_RECORDING_SECONDS):
                progress_bar.progress((i + 1) / MAX_RECORDING_SECONDS)
                remaining.write(f"Seconds remaining: {MAX_RECORDING_SECONDS - i}")
                time.sleep(1)
            
            remaining.empty()
        
        recording.write("✅ Recording complete!")
        progress_bar.empty()
        
        # Convert recorded data to numpy array
        if audio_data:
            audio_np = np.concatenate(audio_data, axis=0)
            
            # First save to WAV file
            write(WAV_FILE, SAMPLE_RATE, audio_np)
            
            # Convert WAV to MP3 using pydub
            audio = AudioSegment.from_wav(WAV_FILE)
            audio.export(MP3_FILE, format="mp3")
            
            # Remove the temporary WAV file
            if os.path.exists(WAV_FILE):
                os.remove(WAV_FILE)
                
            return MP3_FILE
        else:
            st.error("No audio was recorded.")
            return None
    
    except Exception as e:
        st.error(f"Error during recording: {str(e)}")
        return None

def transcribe_audio(audio_path):
    """Transcribe Marathi audio to text using Google Speech-to-Text API."""
    try:
        # Initialize the Google Speech-to-Text client
        client = speech.SpeechClient()
        
        # Read the audio file
        with open(audio_path, "rb") as audio_file:
            content = audio_file.read()
        
        # Configure the recognition request
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.MP3,
            sample_rate_hertz=SAMPLE_RATE,
            language_code="mr-IN",  # Marathi language code
            enable_automatic_punctuation=True,
        )
        
        # Send the request to Google's Speech-to-Text API
        response = client.recognize(config=config, audio=audio)
        
        # Extract the transcribed text
        transcription = ""
        for result in response.results:
            transcription += result.alternatives[0].transcript + " "
        
        # If no transcription is returned, simulate with Claude (for demo purposes)
        if not transcription.strip():
            st.warning("No transcription was returned from Google Speech-to-Text. Using Claude to simulate transcription for this demo.")
            transcription = simulate_transcription_with_claude(st.session_state.topic)
        
        return transcription.strip()
        
    except Exception as e:
        st.error(f"Failed to transcribe audio: {str(e)}")
        st.warning("Using Claude to simulate transcription for this demo due to error.")
        return simulate_transcription_with_claude(st.session_state.topic)

def simulate_transcription_with_claude(topic):
    """Simulate transcription with Claude for demo purposes."""
    bedrock_client = setup_bedrock_client()
    if not bedrock_client:
        return "Error generating simulated transcription."
        
    prompt = """
    Please simulate the transcription of a Marathi speech audio file.
    Write out what a Marathi speaker might say about the given topic, using proper Marathi script.
    The transcription should be about 3-5 sentences long and related to the topic.
    """
    
    response = bedrock_client.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "temperature": 0,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"{prompt}\n\nTopic: '{topic}'"}
                    ]
                }
            ]
        })
    )
    
    response_body = json.loads(response.get("body").read())
    return response_body.get("content")[0].get("text")

def analyze_speech(transcription, topic):
    """Analyze the transcribed Marathi speech using Claude."""
    bedrock_client = setup_bedrock_client()
    if not bedrock_client:
        return None
    
    try:
        prompt = f"""
        You are a Marathi language expert assessing a student's speaking skills.
        
        The student was asked to speak about this topic: "{topic}"
        
        Here is the transcription of what the student said in Marathi:
        
        "{transcription}"
        
        Grade the student's speaking on a scale of 1-10 in these categories:
        1. Grammar Correctness
        2. Meaningfulness and Relevance to Topic
        3. Vocabulary Level 
        4. Overall Fluency
        
        Calculate a total score (out of 40) and assign a letter grade based on the following scale:
        - A: 36-40 points (90-100%)
        - B: 32-35 points (80-89%)
        - C: 28-31 points (70-79%)
        - D: 24-27 points (60-69%)
        - F: Below 24 points (Below 60%)
        
        Provide detailed, constructive feedback IN ENGLISH ONLY (not Marathi) that will help the student improve.
        Include specific examples from their speech.
        
        Your response should begin with the letter grade prominently displayed.
        
        Finally, provide 2-3 suggested practice phrases in both Marathi and English for the student to try next.
        """
        
        response = bedrock_client.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "temperature": 0.7,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt}
                        ]
                    }
                ]
            })
        )
        
        response_body = json.loads(response.get("body").read())
        analysis = response_body.get("content")[0].get("text")
        
        return analysis
    
    except Exception as e:
        st.error(f"Failed to analyze speech: {str(e)}")
        return None

def display_audio_player(file_path):
    """Display an audio player for the recorded audio."""
    try:
        with open(file_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        
        st.audio(audio_bytes, format="audio/mp3")
    except Exception as e:
        st.error(f"Failed to display audio player: {str(e)}")

def main():
    # Set up the state
    if 'step' not in st.session_state:
        st.session_state.step = 1
    
    if 'topic' not in st.session_state:
        st.session_state.topic = ""
    
    if 'generated_image' not in st.session_state:
        st.session_state.generated_image = None
    
    # Header
    st.title("🗣️ Marathi Speaking Practice")
    st.write("Improve your Marathi speaking skills with AI-powered feedback")
    
    # Sidebar for AWS and Google Cloud configuration
    with st.sidebar:
        st.header("Configuration")
        aws_region = st.text_input("AWS Region", value=st.session_state.get('aws_region', 'us-east-1'))
        
        if aws_region != st.session_state.get('aws_region'):
            st.session_state.aws_region = aws_region
        
        st.markdown("---")
        st.subheader("About")
        st.write("""
        This application helps you practice speaking Marathi by:
        1. Generating a topic-related image
        2. Recording your Marathi speech
        3. Providing AI-powered feedback on your speaking skills
        """)
        
        st.info("Note: This app uses Google Speech-to-Text API for transcription. Make sure you have set up your Google Cloud credentials properly.")
    
    # Step 1: Topic Selection
    if st.session_state.step == 1:
        st.header("Step 1: Choose a Topic")
        st.write("Enter a topic you'd like to speak about in Marathi (3-4 words maximum):")
        
        topic = st.text_input("Topic", key="topic_input")
        
        if st.button("Generate Image"):
            if len(topic.split()) > 4:
                st.error("Please limit your topic to 3-4 words maximum.")
            elif not topic:
                st.error("Please enter a topic.")
            else:
                with st.spinner("Generating image related to your topic..."):
                    image = generate_image(topic)
                
                if image:
                    st.session_state.topic = topic
                    st.session_state.generated_image = image
                    st.session_state.step = 2
                    st.rerun()
    
    # Step 2: Image Display and Recording
    elif st.session_state.step == 2:
        st.header("Step 2: Speak about the Image")
        st.write(f"Topic: **{st.session_state.topic}**")
        
        st.image(st.session_state.generated_image, caption=f"Image for: {st.session_state.topic}")
        
        st.write("Now, speak in Marathi about this topic for up to 30 seconds.")
        st.write("Look at the image and try to describe what you see or share your thoughts related to the topic.")
        
        if st.button("Start Recording"):
            recording_path = record_audio()
            if recording_path:
                st.session_state.recording_path = recording_path
                st.session_state.step = 3
                st.rerun()
        
        if st.button("Back to Topic Selection", key="back_to_topic"):
            st.session_state.step = 1
            st.session_state.topic = ""
            st.session_state.generated_image = None
            st.rerun()
    
    # Step 3: Playback and Analysis
    elif st.session_state.step == 3:
        st.header("Step 3: Review Your Speaking")
        st.write(f"Topic: **{st.session_state.topic}**")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(st.session_state.generated_image, caption=f"Image for: {st.session_state.topic}")
        
        with col2:
            st.write("Your Recording:")
            display_audio_player(st.session_state.recording_path)
            
            if st.button("Record Again"):
                st.session_state.step = 2
                st.rerun()
        
        if st.button("Get Feedback"):
            with st.spinner("Transcribing your Marathi speech..."):
                transcription = transcribe_audio(st.session_state.recording_path)
                
                if transcription:
                    st.session_state.transcription = transcription
                    
                    with st.spinner("Analyzing your Marathi speaking..."):
                        analysis = analyze_speech(transcription, st.session_state.topic)
                        
                        if analysis:
                            st.session_state.analysis = analysis
                            st.session_state.step = 4
                            st.rerun()
    
    # Step 4: Feedback Display
    elif st.session_state.step == 4:
        st.header("Step 4: Your Speaking Feedback")
        st.write(f"Topic: **{st.session_state.topic}**")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(st.session_state.generated_image, caption=f"Image for: {st.session_state.topic}")
            st.write("Your Recording:")
            display_audio_player(st.session_state.recording_path)
        
        with col2:
            st.subheader("Transcription")
            # Using a larger text area for transcription
            st.text_area("Your transcribed speech:", value=st.session_state.transcription, 
                        height=200, disabled=True, key="transcription_area")
            
            st.subheader("Analysis & Feedback")
            st.markdown(st.session_state.analysis)
        
        if st.button("Try Another Topic"):
            st.session_state.step = 1
            st.session_state.topic = ""
            st.session_state.generated_image = None
            st.rerun()
        
        if st.button("Practice Same Topic Again"):
            st.session_state.step = 2
            st.rerun()

if __name__ == "__main__":
    main()