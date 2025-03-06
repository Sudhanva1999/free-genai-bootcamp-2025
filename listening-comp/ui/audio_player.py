"""
Audio player component for playing and generating audio
"""
import os
import streamlit as st
from services.audio_service import generate_question_audio
from services.storage_service import update_question_audio

def render_audio_player():
    """Render the audio player component"""
    st.subheader("Audio")
    
    # If we already have audio, display it
    if st.session_state.current_audio:
        _display_audio()
    # Otherwise, show generate button if we have a question
    elif st.session_state.current_question:
        _display_generate_button()
    else:
        st.info("Generate a question to create audio.")

def _display_audio():
    """Display the audio player for existing audio"""
    try:
        st.audio(st.session_state.current_audio)
    except Exception as e:
        st.error(f"Error playing audio: {str(e)}")
        st.session_state.current_audio = None

def _display_generate_button():
    """Display the generate audio button"""
    if st.button("Generate Audio"):
        with st.spinner("Generating audio..."):
            try:
                # Clear any previous audio
                if st.session_state.current_audio and os.path.exists(st.session_state.current_audio):
                    try:
                        os.unlink(st.session_state.current_audio)
                    except Exception:
                        pass
                st.session_state.current_audio = None
                
                # Generate new audio
                audio_file = generate_question_audio(st.session_state.current_question)
                
                # Verify the audio file exists
                if not os.path.exists(audio_file):
                    raise Exception("Audio file was not created")
                    
                st.session_state.current_audio = audio_file
                
                # Update stored question with audio file
                update_question_audio(
                    st.session_state.current_question,
                    st.session_state.current_practice_type,
                    st.session_state.current_topic,
                    audio_file
                )
                st.rerun()
                
            except Exception as e:
                st.error(f"Error generating audio: {str(e)}")
                # Clear the audio state on error
                st.session_state.current_audio = None