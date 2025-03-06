"""
Practice section UI component for question generation and answering
"""
import streamlit as st
from config import PRACTICE_TYPES, TOPICS
from services.question_service import generate_new_question, get_question_feedback
from ui.audio_player import render_audio_player

def render_practice_section():
    """Render the practice section with question generation and answering"""
    # Practice type selection
    practice_type = st.selectbox(
        "Select Practice Type",
        PRACTICE_TYPES
    )
    
    # Topic selection
    topic = st.selectbox(
        "Select Topic",
        TOPICS[practice_type]
    )
    
    # Generate new question button
    if st.button("Generate New Question"):
        with st.spinner("Generating question..."):
            generate_new_question(practice_type, topic)
    
    # Display current question if available
    if st.session_state.current_question:
        _render_current_question()
    else:
        st.info("Click 'Generate New Question' to start practicing!")

def _render_current_question():
    """Render the current practice question"""
    st.subheader("Practice Scenario")
    
    # Get current practice type (either from selection or stored question)
    practice_type = st.session_state.current_practice_type
    question = st.session_state.current_question
    
    # Display question components based on practice type
    if practice_type == "Dialogue Practice":
        st.write("**Introduction:**")
        st.write(question['Introduction'])
        st.write("**Conversation:**")
        st.write(question['Conversation'])
    else:
        st.write("**Situation:**")
        st.write(question['Situation'])
    
    st.write("**Question:**")
    st.write(question['Question'])
    
    # Create two columns for options and audio
    col1, col2 = st.columns([2, 1])
    
    with col1:
        _render_question_options()
    
    with col2:
        render_audio_player()

def _render_question_options():
    """Render question options and feedback"""
    options = st.session_state.current_question['Options']
    
    # If we have feedback, show which answers were correct/incorrect
    if st.session_state.feedback:
        _render_feedback(options)
    else:
        _render_options_selection(options)

def _render_feedback(options):
    """Render feedback for submitted answer"""
    feedback = st.session_state.feedback
    correct = feedback.get('correct', False)
    correct_answer = feedback.get('correct_answer', 1) - 1
    selected_index = st.session_state.selected_answer - 1 if hasattr(st.session_state, 'selected_answer') else -1
    
    st.write("\n**Your Answer:**")
    for i, option in enumerate(options):
        if i == correct_answer and i == selected_index:
            st.success(f"{i+1}. {option} ✓ (Correct!)")
        elif i == correct_answer:
            st.success(f"{i+1}. {option} ✓ (This was the correct answer)")
        elif i == selected_index:
            st.error(f"{i+1}. {option} ✗ (Your answer)")
        else:
            st.write(f"{i+1}. {option}")
    
    # Show explanation
    st.write("\n**Explanation:**")
    explanation = feedback.get('explanation', 'No feedback available')
    if correct:
        st.success(explanation)
    else:
        st.error(explanation)
    
    # Add button to try new question
    if st.button("Try Another Question"):
        st.session_state.feedback = None
        st.rerun()

def _render_options_selection(options):
    """Render options selection for answering"""
    # Display options as radio buttons
    selected = st.radio(
        "Choose your answer:",
        options,
        index=None,
        format_func=lambda x: f"{options.index(x) + 1}. {x}"
    )
    
    # Submit answer button
    if selected and st.button("Submit Answer"):
        selected_index = options.index(selected) + 1
        st.session_state.selected_answer = selected_index
        
        with st.spinner("Generating feedback..."):
            # Get feedback for the selected answer
            feedback = get_question_feedback(
                st.session_state.current_question,
                selected_index
            )
            st.session_state.feedback = feedback
            
            # Report question result to learning backend
            from services.session_service import session_service
            session_service.report_question_result(
                st.session_state.current_question,
                selected_index,
                feedback
            )
        
        st.rerun()