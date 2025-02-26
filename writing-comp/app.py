import streamlit as st
import requests
import json
import boto3
import time
import random

# Set page config
st.set_page_config(
    page_title="Marathi Practice App",
    page_icon="📚",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .word-card {
        padding: 15px;
        border-radius: 5px;
        margin: 10px;
        background-color: #f0f2f6;
        border: 1px solid #ddd;
        transition: transform 0.2s, box-shadow 0.2s;
        cursor: pointer;
    }
    .word-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .selected-card {
        background-color: #bae7ff;
        border: 2px solid #1890ff;
    }
    .card-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
    }
    .card-english {
        font-size: 24px;
        font-weight: bold;
    }
    .card-marathi {
        font-size: 22px;
        margin-top: 10px;
    }
    .sentence-container {
        margin-top: 20px;
        padding: 20px;
        border-radius: 5px;
        background-color: #f9f9f9;
        border: 1px solid #eaeaea;
    }
    .marathi-sentence {
        font-size: 24px;
        color: #333;
        margin-bottom: 10px;
    }
    .english-sentence {
        font-size: 20px;
        color: #666;
    }
    .grade-container {
        padding: 15px;
        border-radius: 8px;
        margin-top: 20px;
    }
    .grade-s {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
    }
    .grade-a {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
    }
    .grade-b {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
    }
    .grade-c {
        background-color: #d6d8d9;
        border: 1px solid #c6c8ca;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'selected_words' not in st.session_state:
    st.session_state.selected_words = []

if 'words_data' not in st.session_state:
    st.session_state.words_data = None

if 'sentence' not in st.session_state:
    st.session_state.sentence = None

if 'page' not in st.session_state:
    st.session_state.page = 'home'
    
if 'assessment_grade' not in st.session_state:
    st.session_state.assessment_grade = None
    
if 'assessment_feedback' not in st.session_state:
    st.session_state.assessment_feedback = None

# Navigation functions
def go_to_assessment():
    st.session_state.page = 'assessment'
    
def go_to_home():
    st.session_state.page = 'home'
    st.session_state.selected_words = []
    st.session_state.sentence = None
    st.session_state.assessment_grade = None
    st.session_state.assessment_feedback = None

# Generate sentence using AWS Bedrock
def generate_sentence(selected_words):
    try:
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock-runtime')
        
        # Extract English and Marathi word pairs
        word_pairs = [(word['english'], word['marathi']) for word in selected_words]
        
        # Construct message content for Claude
        message_content = [
            {
                "role": "assistant",
                "content": """You are a Marathi language teacher creating simple meaningful sentences for students.
                Create natural meaningful sentences that use the provided Marathi words.
                Always respond with a valid JSON object containing exactly two fields:
                - marathi_sentence: The Marathi sentence
                - english_translation: The literal English translation
                Do not include any other text in your response."""
            },
            {
                "role": "user",
                "content": f"""Create a simple Marathi meaningful sentence using these words: {', '.join([w[1] for w in word_pairs])}.
                The English translations of these words are: {', '.join([w[0] for w in word_pairs])}.
                Provide both the Marathi sentence and its English translation."""
            }
        ]
        
        # Call Bedrock with proper Claude message format
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 300,
                "temperature": 0.7,
                "messages": message_content
            })
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        completion = response_body.get('content', [{}])[0].get('text', '')
        
        # Log the raw response for debugging
        with open("log.txt", "a") as f:
            f.write(f"Raw response: {completion}\n")
        
        # Try to extract JSON from the response
        try:
            # First, try direct JSON parsing
            result = json.loads(completion)
            
            with open("log.txt", "a") as f:
                f.write(f"Parsed result: {result}\n")
            
            # Verify the required fields exist
            if 'marathi_sentence' in result and 'english_translation' in result:
                return result
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON using regex
            import re
            json_match = re.search(r'({.*})', completion, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                    if 'marathi_sentence' in result and 'english_translation' in result:
                        return result
                except:
                    pass
        
        # Fallback with simulated response if all parsing attempts fail
        return {
            "marathi_sentence": f"मी {word_pairs[0][1]} आणि {word_pairs[1][1]} पाहिले, ते {word_pairs[2][1]} होते.",
            "english_translation": f"I saw {word_pairs[0][0]} and {word_pairs[1][0]}, they were {word_pairs[2][0]}."
        }
            
    except Exception as e:
        st.warning(f"Could not connect to sentence generation service. Using fallback sentence.")
        # Log the exception for debugging
        with open("log.txt", "a") as f:
            f.write(f"Exception: {str(e)}\n")
        
        # Fallback with simulated response
        return {
            "marathi_sentence": f"मी {word_pairs[0][1]} आणि {word_pairs[1][1]} पाहिले, ते {word_pairs[2][1]} होते.",
            "english_translation": f"I saw {word_pairs[0][0]} and {word_pairs[1][0]}, they were {word_pairs[2][0]}."
        }

# Function to fetch words for a given category
def fetch_words(category):
    api_url = f"http://10.0.0.79:5002/api/groups/words/{category}"
    try:
        with st.spinner(f"Loading {category} words..."):
            response = requests.get(api_url)
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Error fetching words: HTTP {response.status_code}")
                return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

# Function to toggle selection of a word
def toggle_word_selection(word):
    if word in st.session_state.selected_words:
        st.session_state.selected_words.remove(word)
    elif len(st.session_state.selected_words) < 3:
        st.session_state.selected_words.append(word)
    else:
        st.warning("You can only select up to 3 words!")

# Function to grade student's Marathi translation
def grade_translation(target_english, student_marathi, correct_marathi):
    try:
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock-runtime')
        
        # Construct prompt for the LLM using Claude's message format
        message_content = [
            {
                "role": "system",
                "content": """You are a Marathi language teacher grading student writing.
                Grade based on:
                - Accuracy of translation compared to target sentence
                - Grammar correctness
                - Writing style and naturalness
                
                Use S/A/B/C grading scale where:
                S: Perfect or near-perfect
                A: Very good with minor issues
                B: Good but needs improvement
                C: Significant issues to address
                
                Always respond with exactly this format:
                Grade: [S/A/B/C]
                Feedback: [Your detailed feedback explaining the grade with specific examples]"""
            },
            {
                "role": "user",
                "content": f"""Grade this Marathi writing sample:
                Target English sentence: {target_english}
                Student's Marathi: {student_marathi}
                Correct Marathi translation: {correct_marathi}"""
            }
        ]
        
        # Call Bedrock with proper Claude message format
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "temperature": 0.2,
                "messages": message_content
            })
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        completion = response_body.get('content', [{}])[0].get('text', '')
        
        # Extract grade and feedback using more robust pattern matching
        grade_match = re.search(r'Grade:\s*([SABC])', completion, re.IGNORECASE)
        feedback_match = re.search(r'Feedback:\s*([\s\S]*)', completion)
        
        if grade_match and feedback_match:
            grade = grade_match.group(1).upper()  # Normalize to uppercase
            feedback = feedback_match.group(1).strip()
        else:
            # If pattern matching fails, provide a default assessment
            st.warning("Grading format was unexpected. Providing a generic assessment.")
            
            # Basic comparison - if student answer is very close to correct answer
            if student_marathi.strip() == correct_marathi.strip():
                grade = "S"
                feedback = "Your translation matches the correct answer perfectly!"
            else:
                grade = "B"
                feedback = ("Your translation was understood but had some differences from the model answer. "
                           "Keep practicing Marathi sentence structure and word order.")
        
        return {
            "grade": grade,
            "feedback": feedback
        }
        
    except Exception as e:
        st.warning("Could not connect to grading service. Using simplified grading.")
        
        # Simple fallback grading logic without using the LLM
        # String similarity ratio as a basic metric
        from difflib import SequenceMatcher
        
        def similarity_ratio(a, b):
            return SequenceMatcher(None, a, b).ratio()
        
        # Calculate similarity between student's answer and correct answer
        sim_ratio = similarity_ratio(student_marathi.strip(), correct_marathi.strip())
        
        # Assign grade based on similarity
        if sim_ratio > 0.9:
            grade = "S"
            feedback = "Excellent! Your translation is very close to the model answer."
        elif sim_ratio > 0.7:
            grade = "A"
            feedback = "Very good translation with minor differences from the model answer."
        elif sim_ratio > 0.5:
            grade = "B"
            feedback = "Good attempt, but there are some differences in wording or structure."
        else:
            grade = "C"
            feedback = "Your translation has significant differences from the model answer. Keep practicing!"
        
        return {
            "grade": grade,
            "feedback": feedback
        }

# Home page - Word selection and sentence generation
def show_home_page():
    st.title("Marathi Practice App")
    st.subheader("Learn Marathi words by category")
    
    # Category input
    category = st.text_input("Please enter any word category you want to practice:", placeholder="e.g., colors, animals, fruits")
    
    # Fetch words when category is provided
    if category:
        if st.session_state.words_data is None or st.session_state.words_data.get('group_name') != category:
            words_data = fetch_words(category)
            if words_data:
                st.session_state.words_data = words_data
                st.session_state.selected_words = []
                st.session_state.sentence = None
    
    # Display word cards if data is available
    if st.session_state.words_data:
        st.subheader(f"Words in category: {st.session_state.words_data['group_name']}")
        st.write("Click on cards to select up to 3 words for sentence generation")
        
        # Display the word cards in a grid
        cols = st.columns(5)
        for i, word in enumerate(st.session_state.words_data['words']):
            with cols[i % 5]:
                # Check if this word is selected
                is_selected = word in st.session_state.selected_words
                
                # Use a button for better interactivity
                if st.button(
                    f"{word['english']}\n{word['marathi']}", 
                    key=f"word_{i}",
                    use_container_width=True,
                    type="primary" if is_selected else "secondary"
                ):
                    toggle_word_selection(word)
                    st.rerun()
        
        # Show selected words
        st.subheader("Selected Words")
        if st.session_state.selected_words:
            selected_cols = st.columns(3)
            for i, word in enumerate(st.session_state.selected_words):
                with selected_cols[i]:
                    st.info(f"**{word['english']}** - {word['marathi']}")
        else:
            st.info("No words selected yet")
        
        # Generate sentence button
        if len(st.session_state.selected_words) == 3:
            if st.button("Generate Sentence", use_container_width=True, type="primary"):
                with st.spinner("Generating sentence..."):
                    # Add a slight delay to simulate processing
                    time.sleep(1.5)
                    st.session_state.sentence = generate_sentence(st.session_state.selected_words)
        else:
            st.button("Generate Sentence", use_container_width=True, disabled=True, 
                     help="Please select exactly 3 words to generate a sentence")
        
        # Display generated sentence and go to assessment button
        if st.session_state.sentence:
            st.markdown("### Generated Sentence")
            st.markdown(f"""
            <div class="sentence-container">
                <div class="english-sentence">{st.session_state.sentence['english_translation']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Button to go to assessment page
            st.button("Practice Translating This Sentence", on_click=go_to_assessment, use_container_width=True, type="primary")
    else:
        st.info("Enter a category above to start practicing!")

# Assessment page - Translation challenge
def show_assessment_page():
    st.title("Marathi Translation Practice")
    
    if not st.session_state.sentence:
        st.error("No sentence to practice with. Please go back and generate a sentence first.")
        st.button("Back to Home", on_click=go_to_home)
        return
    
    # Show the English sentence
    st.subheader("Translate this sentence to Marathi:")
    st.markdown(f"""
    <div class="sentence-container">
        <div class="english-sentence">{st.session_state.sentence['english_translation']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Text input for user's Marathi translation
    user_translation = st.text_area("Your translation in Marathi:", height=100)
    
    # Check translation button
    if st.button("Check My Translation", use_container_width=True, type="primary", disabled=not user_translation):
        with st.spinner("Analyzing your translation..."):
            # Add a slight delay to simulate processing
            time.sleep(1.5)
            
            # Grade the translation
            grading_result = grade_translation(
                st.session_state.sentence['english_translation'],
                user_translation,
                st.session_state.sentence['marathi_sentence']
            )
            
            # Save assessment results
            st.session_state.assessment_grade = grading_result['grade']
            st.session_state.assessment_feedback = grading_result['feedback']
            
            # Rerun to update the UI
            st.rerun()
    
    # Display assessment results if available
    if st.session_state.assessment_grade:
        grade = st.session_state.assessment_grade
        feedback = st.session_state.assessment_feedback
        
        # Determine grade CSS class
        grade_class = f"grade-{grade.lower()}"
        
        # Show feedback
        st.markdown(f"""
        <div class="grade-container {grade_class}">
            <h3>Grade: {grade}</h3>
            <p>{feedback}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show correct translation if grade is not S
        if grade != "S":
            st.write("Keep practicing! Try again with the same sentence.")
        else:
            st.success("Excellent job! You've mastered this sentence!")
            st.markdown(f"""
            <div class="sentence-container">
                <div class="marathi-sentence">{st.session_state.sentence['marathi_sentence']}</div>
                <div class="english-sentence">{st.session_state.sentence['english_translation']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Button to go back to home to try another category
            st.button("Practice More Words", on_click=go_to_home, use_container_width=True, type="primary")
    
    # Always show a back button
    st.button("Back to Words", on_click=go_to_home)

# Main app logic - determines which page to show
if st.session_state.page == 'home':
    show_home_page()
elif st.session_state.page == 'assessment':
    show_assessment_page()

# Add a footer
st.markdown("---")
st.markdown("Made with ❤️ for Marathi language learners")