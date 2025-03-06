"""
Main page UI for the Marathi Listening Practice application
"""
import streamlit as st
from config import APP_TITLE, APP_DESCRIPTION
from ui.sidebar import render_sidebar
from ui.practice_section import render_practice_section
from utils.session_utils import initialize_session_state

def render_main_page():
    """Render the main application page"""
    # Initialize session state variables
    initialize_session_state()
    
    # Initialize session service
    from services.session_service import session_service
    session_service.initialize_session()
    
    # Render page title and description
    st.title(APP_TITLE)
    st.markdown(APP_DESCRIPTION)
    
    # Group selection in the header area
    col1, col2 = st.columns([3, 1])
    with col2:
        group_id = st.number_input(
            "Group ID", 
            min_value=1,
            value=session_service.get_group_id(),
            step=1,
            help="Select your learning group ID"
        )
        
        if group_id != session_service.get_group_id():
            session_service.set_group_id(group_id)
            st.success(f"Group set to {group_id}")
    
    # Render sidebar with saved questions
    render_sidebar()
    
    # Render the practice section
    render_practice_section()