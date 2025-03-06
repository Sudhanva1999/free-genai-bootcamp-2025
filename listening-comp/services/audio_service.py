"""
Service for generating and managing audio files
"""
import os
import streamlit as st
from backend.audio_generator import AudioGenerator

def generate_question_audio(question):
    """
    Generate audio for a question
    
    Args:
        question (dict): The question object
        
    Returns:
        str: Path to the generated audio file
    """
    audio_generator = _get_audio_generator()
    
    # Generate audio for the question
    audio_file = audio_generator.generate_audio(question)
    
    return audio_file

def _get_audio_generator():
    """
    Get or initialize the audio generator
    
    Returns:
        AudioGenerator: The audio generator instance
    """
    if 'audio_generator' not in st.session_state:
        st.session_state.audio_generator = AudioGenerator()
    
    return st.session_state.audio_generator