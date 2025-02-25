import os
import sys

def create_directory_structure():
    """Create the required directory structure for the application"""
    # Create base directories
    for dir_path in [
        "backend/data/vectorstore",
        "backend/data/stored_questions",
        "frontend/static/audio"
    ]:
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    # Create empty data files
    with open("backend/data/stored_questions.json", "w", encoding="utf-8") as f:
        f.write("{}")
    print("Created empty stored_questions.json file")

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import boto3
        import streamlit
        import chromadb
        print("All required Python packages are installed.")
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install the required packages using: pip install -r requirements.txt")
        return False
    
    # Check for ffmpeg
    import subprocess
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True)
        print("ffmpeg is installed.")
    except FileNotFoundError:
        print("WARNING: ffmpeg is not installed. Audio generation will not work.")
        print("Please install ffmpeg:")
        print("  - On Ubuntu/Debian: sudo apt install ffmpeg")
        print("  - On macOS: brew install ffmpeg")
        print("  - On Windows: download from https://ffmpeg.org/download.html")
        return False
    
    return True

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    import boto3
    try:
        # Try to make a simple call to AWS
        boto3.client('sts').get_caller_identity()
        print("AWS credentials are configured correctly.")
        return True
    except Exception as e:
        print(f"AWS credentials issue: {e}")
        print("Please configure your AWS credentials:")
        print("  1. Create ~/.aws/credentials file with your access keys")
        print("  2. Or set environment variables: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        return False

def main():
    """Setup the Marathi Listening Practice application"""
    print("Setting up Marathi Listening Practice...")
    
    # Create directory structure
    create_directory_structure()
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check AWS credentials
    aws_ok = check_aws_credentials()
    
    if deps_ok and aws_ok:
        print("\nSetup completed successfully! You can now run the application with:")
        print("  streamlit run frontend/main.py")
    else:
        print("\nSetup completed with warnings. Please address the issues above before running the application.")

if __name__ == "__main__":
    main()