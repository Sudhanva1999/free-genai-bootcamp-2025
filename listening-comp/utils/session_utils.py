"""
Utilities for managing Streamlit session state
"""
import streamlit as st

def initialize_session_state():
    """Initialize all necessary session state variables"""
    # Question state
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    
    # Practice type and topic
    if 'current_practice_type' not in st.session_state:
        st.session_state.current_practice_type = None
    if 'current_topic' not in st.session_state:
        st.session_state.current_topic = None
    
    # Audio state
    if 'current_audio' not in st.session_state:
        st.session_state.current_audio = None
    
    # Feedback state
    if 'feedback' not in st.session_state:
        st.session_state.feedback = None
    
    # Answer state
    if 'selected_answer' not in st.session_state:
        st.session_state.selected_answer = None

def reset_question_state():
    """Reset the question-related session state"""
    st.session_state.current_question = None
    st.session_state.current_practice_type = None
    st.session_state.current_topic = None
    st.session_state.current_audio = None
    st.session_state.feedback = None
    st.session_state.selected_answer = None