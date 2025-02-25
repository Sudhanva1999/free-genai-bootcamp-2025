import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.audio_generator import AudioGenerator

# Test question data
test_question = {
    "Introduction": "पुढील संभाषण ऐकून प्रश्नाचे उत्तर द्या.",
    "Conversation": """
    पुरुष: नमस्कार, मला बाजारात जायचे आहे. रस्ता सांगाल का?
    स्त्री: अर्थात. थेट जा आणि दुसऱ्या चौकात उजवीकडे वळा.
    पुरुष: किती वेळ लागेल?
    स्त्री: पायी जाण्यास १० मिनिटे लागतील.
    """,
    "Question": "बाजारापर्यंत पायी जाण्यास किती वेळ लागेल?",
    "Options": [
        "५ मिनिटे",
        "१० मिनिटे",
        "१५ मिनिटे",
        "२० मिनिटे"
    ]
}

def test_audio_generation():
    print("Initializing audio generator...")
    generator = AudioGenerator()
    
    print("\nParsing conversation...")
    parts = generator.parse_conversation(test_question)
    
    print("\nParsed conversation parts:")
    for speaker, text, gender in parts:
        print(f"Speaker: {speaker} ({gender})")
        print(f"Text: {text}")
        print("---")
    
    print("\nGenerating audio file...")
    audio_file = generator.generate_audio(test_question)
    print(f"Audio file generated: {audio_file}")
    
    return audio_file

if __name__ == "__main__":
    try:
        audio_file = test_audio_generation()
        print("\nTest completed successfully!")
        print(f"You can find the audio file at: {audio_file}")
    except Exception as e:
        print(f"\nError during test: {str(e)}")
        import traceback
        traceback.print_exc()