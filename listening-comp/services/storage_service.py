"""
Service for storing and retrieving questions
"""
import os
import json
from datetime import datetime
from config import get_questions_file_path, get_data_path

def load_stored_questions():
    """
    Load previously stored questions from JSON file
    
    Returns:
        dict: Dictionary of stored questions
    """
    questions_file = get_questions_file_path()
    
    if os.path.exists(questions_file):
        try:
            with open(questions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            # Handle corrupted or missing file
            print(f"Error loading questions file: {e}")
            return {}
    
    return {}

def save_question(question, practice_type, topic, audio_file=None):
    """
    Save a generated question to JSON file
    
    Args:
        question (dict): The question object
        practice_type (str): The type of practice
        topic (str): The question topic
        audio_file (str, optional): Path to the audio file
        
    Returns:
        str: The question ID
    """
    # Load existing questions
    stored_questions = load_stored_questions()
    
    # Create a unique ID for the question using timestamp
    question_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Add metadata
    question_data = {
        "question": question,
        "practice_type": practice_type,
        "topic": topic,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "audio_file": audio_file
    }
    
    # Add to stored questions
    stored_questions[question_id] = question_data
    
    # Save back to file
    _save_questions_to_file(stored_questions)
    
    return question_id

def update_question_audio(question, practice_type, topic, audio_file):
    """
    Update a question with its audio file
    
    Args:
        question (dict): The question object
        practice_type (str): The type of practice
        topic (str): The question topic
        audio_file (str): Path to the audio file
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Load existing questions
    stored_questions = load_stored_questions()
    
    # Find the question by matching content
    # This is a simplistic approach - in production, use a more robust ID system
    for qid, qdata in stored_questions.items():
        if qdata["question"] == question and qdata["practice_type"] == practice_type and qdata["topic"] == topic:
            # Update audio file
            stored_questions[qid]["audio_file"] = audio_file
            _save_questions_to_file(stored_questions)
            return True
    
    # If not found, save as a new question
    save_question(question, practice_type, topic, audio_file)
    return False

def _save_questions_to_file(questions_data):
    """
    Save questions data to the JSON file
    
    Args:
        questions_data (dict): The questions data
    """
    questions_file = get_questions_file_path()
    
    # Ensure the data directory exists
    os.makedirs(get_data_path(), exist_ok=True)
    
    # Save with error handling
    try:
        with open(questions_file, 'w', encoding='utf-8') as f:
            json.dump(questions_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving questions file: {e}")
        raise