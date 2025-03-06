"""
Service for generating and managing questions
"""
import streamlit as st
from backend.question_generator import QuestionGenerator
from backend.vector_store import QuestionVectorStore
from services.storage_service import save_question

def generate_new_question(practice_type, topic):
    """
    Generate a new question based on practice type and topic
    
    Args:
        practice_type (str): The type of practice (e.g., "Dialogue Practice")
        topic (str): The topic for the question
        
    Returns:
        dict: The generated question object
    """
    # Determine the section number based on practice type
    section_num = 2 if practice_type == "Dialogue Practice" else 3
    
    # Generate the question
    question_generator = _get_question_generator()
    new_question = question_generator.generate_similar_question(section_num, topic)
    
    # Update session state
    st.session_state.current_question = new_question
    st.session_state.current_practice_type = practice_type
    st.session_state.current_topic = topic
    st.session_state.feedback = None
    st.session_state.current_audio = None
    
    # Save the generated question
    question_id = save_question(new_question, practice_type, topic)
    
    # Also save to vector store for future retrieval
    vector_store = QuestionVectorStore()
    vector_store.add_question(section_num, new_question, question_id)
    
    return new_question

def get_question_feedback(question, selected_answer):
    """
    Get feedback for a selected answer
    
    Args:
        question (dict): The question object
        selected_answer (int): The selected answer index
        
    Returns:
        dict: Feedback information
    """
    question_generator = _get_question_generator()
    return question_generator.get_feedback(question, selected_answer)

def _get_question_generator():
    """
    Get or initialize the question generator
    
    Returns:
        QuestionGenerator: The question generator instance
    """
    if 'question_generator' not in st.session_state:
        st.session_state.question_generator = QuestionGenerator()
    
    return st.session_state.question_generator