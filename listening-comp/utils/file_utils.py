"""
Utilities for file operations
"""
import os
import json
import shutil
from config import get_data_path

def ensure_directory_exists(directory_path):
    """
    Ensure a directory exists, creating it if necessary
    
    Args:
        directory_path (str): The directory path to check/create
    """
    os.makedirs(directory_path, exist_ok=True)

def read_json_file(file_path, default=None):
    """
    Read and parse a JSON file
    
    Args:
        file_path (str): Path to the JSON file
        default (any, optional): Default value if file doesn't exist or has errors
        
    Returns:
        dict: The parsed JSON data or the default value
    """
    if not os.path.exists(file_path):
        return default if default is not None else {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error reading JSON file {file_path}: {e}")
        return default if default is not None else {}

def write_json_file(file_path, data):
    """
    Write data to a JSON file
    
    Args:
        file_path (str): Path to the JSON file
        data (dict): Data to write
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Ensure directory exists
    directory = os.path.dirname(file_path)
    ensure_directory_exists(directory)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error writing JSON file {file_path}: {e}")
        return False

def clean_audio_files(older_than_days=30):
    """
    Clean up old audio files to save space
    
    Args:
        older_than_days (int): Remove files older than this many days
        
    Returns:
        int: Number of files removed
    """
    import time
    
    audio_dir = os.path.join(get_data_path(), "audio")
    if not os.path.exists(audio_dir):
        return 0
    
    now = time.time()
    removed = 0
    
    for filename in os.listdir(audio_dir):
        file_path = os.path.join(audio_dir, filename)
        
        # Skip if not a file
        if not os.path.isfile(file_path):
            continue
            
        # Check file age
        file_age = now - os.path.getmtime(file_path)
        if file_age > (older_than_days * 86400):  # Convert days to seconds
            try:
                os.remove(file_path)
                removed += 1
            except Exception as e:
                print(f"Error removing file {file_path}: {e}")
    
    return removed