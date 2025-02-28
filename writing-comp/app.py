import streamlit as st
import requests
import json
import boto3
import time
import random
import re
import io
import base64
from PIL import Image

# Set page config
st.set_page_config(page_title="Marathi Writing Practice App", page_icon="📚", layout="wide")

# Custom CSS for styling with improved color theme
st.markdown(
    """
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
            .canvas-container {
    border: 2px solid #e6e6e6;
    border-radius: 8px;
    padding: 15px;
    margin: 15px 0;
    background-color: #fafafa;
}

.canvas-title {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 10px;
    color: #333;
}

.recognized-text-container {
    padding: 15px;
    background-color: #f0f8ff;
    border-left: 4px solid #1e90ff;
    margin: 15px 0;
    border-radius: 4px;
}

.canvas-controls {
    margin-top: 15px;
    display: flex;
    gap: 10px;
}

/* Make the canvas stand out more */
.canvas-component {
    border: 1px solid #ddd;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    border-radius: 4px;
}

/* Improve the appearance of the toolbar */
.canvas-toolbar {
    background-color: #f1f3f4;
    padding: 5px;
    border-radius: 4px;
    margin-bottom: 10px;
}

/* Better styling for edit area */
.edit-recognized-text {
    margin-top: 15px;
    padding: 10px;
    background-color: #fff;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
}

/* Add pulsing animation to the processing button when active */
.processing-animation {
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% {
        opacity: 1;
    }
    50% {
        opacity: 0.7;
    }
    100% {
        opacity: 1;
    }
}

/* Improved drawing instructions */
.drawing-instructions {
    color : black;
    margin: 10px 0;
    padding: 10px;
    background-color: #fffde7;
    border-left: 4px solid #ffd600;
    font-size: 14px;
    border-radius: 4px;
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
            margin-bottom: 20px;
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
            color: black;
        padding: 15px;
        border-radius: 8px;
        margin-top: 20px;
    }
    .grade-s {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
    }
    .grade-a {
        background-color: #e7f1ff;
        border: 1px solid #b8daff;
    }
    .grade-b {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
    }
    .grade-c {
        background-color: #d6d8d9;
        border: 1px solid #c6c8ca;
    }
    .canvas-container {
        border: 2px dashed #aaa;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    .input-method-container {
        margin-top: 20px;
        
        padding: 15px;
        border-radius: 5px;
        background-color: #262730;
        margin-bottom: 20px;
    }
    .recognized-text-container {
        color: black;
        padding: 10px;
        background-color: #f5f5f5;
        border-left: 4px solid #007bff;
        margin: 10px 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state variables
if "selected_words" not in st.session_state:
    st.session_state.selected_words = []

if "words_data" not in st.session_state:
    st.session_state.words_data = None

if "sentence" not in st.session_state:
    st.session_state.sentence = None

if "page" not in st.session_state:
    st.session_state.page = "home"

if "assessment_grade" not in st.session_state:
    st.session_state.assessment_grade = None

if "assessment_feedback" not in st.session_state:
    st.session_state.assessment_feedback = None

if "input_method" not in st.session_state:
    st.session_state.input_method = "text"

if "recognized_text" not in st.session_state:
    st.session_state.recognized_text = None


# Navigation functions
def go_to_assessment():
    st.session_state.page = "assessment"
    st.session_state.input_method = "text"
    st.session_state.recognized_text = None


def go_to_home():
    st.session_state.page = "home"
    st.session_state.selected_words = []
    st.session_state.sentence = None
    st.session_state.assessment_grade = None
    st.session_state.assessment_feedback = None
    st.session_state.input_method = "text"
    st.session_state.recognized_text = None


# Generate sentence using AWS Bedrock
def generate_sentence(selected_words):
    try:
        # Initialize Bedrock client
        bedrock = boto3.client("bedrock-runtime")

        # Extract English and Marathi word pairs
        word_pairs = [(word["english"], word["marathi"]) for word in selected_words]

        # Construct message content for Claude
        message_content = [
            {
                "role": "assistant",
                "content": """You are a Marathi language teacher creating simple meaningful sentences for students.
                Create natural meaningful sentences that use the provided Marathi words.
                Always respond with a valid JSON object containing exactly two fields:
                - marathi_sentence: The Marathi sentence
                - english_translation: The literal English translation
                Do not include any other text in your response.""",
            },
            {
                "role": "user",
                "content": f"""Create a simple Marathi meaningful sentence using these words: {', '.join([w[1] for w in word_pairs])}.
                The English translations of these words are: {', '.join([w[0] for w in word_pairs])}.
                Provide both the Marathi sentence and its English translation.""",
            },
        ]

        # Call Bedrock with proper Claude message format
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
            body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 300,
                    "temperature": 0.7,
                    "messages": message_content,
                }
            ),
        )

        # Parse response
        response_body = json.loads(response["body"].read())
        completion = response_body.get("content", [{}])[0].get("text", "")

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
            if "marathi_sentence" in result and "english_translation" in result:
                return result
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON using regex
            import re

            json_match = re.search(r"({.*})", completion, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                    if "marathi_sentence" in result and "english_translation" in result:
                        return result
                except:
                    pass

        # Create fallback with simulated response if all parsing attempts fail
        if len(word_pairs) == 1:
            return {
                "marathi_sentence": f"मला {word_pairs[0][1]} आवडते.",
                "english_translation": f"I like {word_pairs[0][0]}.",
            }
        elif len(word_pairs) == 2:
            return {
                "marathi_sentence": f"मी {word_pairs[0][1]} आणि {word_pairs[1][1]} पाहिले.",
                "english_translation": f"I saw {word_pairs[0][0]} and {word_pairs[1][0]}.",
            }
        else:
            return {
                "marathi_sentence": f"मी {word_pairs[0][1]} आणि {word_pairs[1][1]} पाहिले, ते {word_pairs[2][1]} होते.",
                "english_translation": f"I saw {word_pairs[0][0]} and {word_pairs[1][0]}, they were {word_pairs[2][0]}.",
            }

    except Exception as e:
        st.warning(
            f"Could not connect to sentence generation service. Using fallback sentence."
        )
        # Log the exception for debugging
        with open("log.txt", "a") as f:
            f.write(f"Exception: {str(e)}\n")

        # Create fallback with simulated response based on number of words
        if len(word_pairs) == 1:
            return {
                "marathi_sentence": f"मला {word_pairs[0][1]} आवडते.",
                "english_translation": f"I like {word_pairs[0][0]}.",
            }
        elif len(word_pairs) == 2:
            return {
                "marathi_sentence": f"मी {word_pairs[0][1]} आणि {word_pairs[1][1]} पाहिले.",
                "english_translation": f"I saw {word_pairs[0][0]} and {word_pairs[1][0]}.",
            }
        else:
            return {
                "marathi_sentence": f"मी {word_pairs[0][1]} आणि {word_pairs[1][1]} पाहिले, ते {word_pairs[2][1]} होते.",
                "english_translation": f"I saw {word_pairs[0][0]} and {word_pairs[1][0]}, they were {word_pairs[2][0]}.",
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
    else:
        st.session_state.selected_words.append(word)


# Function to extract text from image using AWS Bedrock
def extract_text_from_image(image_bytes):
    try:
        # Convert image to base64
        import base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock-runtime')
        
        # Construct message content for Claude with specific OCR instructions
        message_content = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": """Extract the Marathi text from this handwritten image. 
                        Be tolerant of messy handwriting and focus on recognizing Marathi characters.
                        If you see handwritten Marathi text, please transcribe it exactly as written.
                        If you don't see any Marathi text or are unsure, respond with 'No Marathi text detected'.
                        Only return the extracted text without any additional explanations."""
                    }
                ]
            }
        ]
        
        # Call Bedrock with proper Claude message format
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "temperature": 0.2,
                "messages": message_content
            })
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        extracted_text = response_body.get('content', [{}])[0].get('text', '')
        
        # Clean up the extracted text - remove any explanations Claude might add
        clean_text = extracted_text.strip()
        
        # Log the extraction for debugging
        with open("ocr_log.txt", "a") as f:
            f.write(f"Raw OCR output: {clean_text}\n")
            
        return clean_text
        
    except Exception as e:
        st.error(f"Error extracting text from image: {str(e)}")
        return "Error processing the handwriting. Please try again."


# Function to grade student's Marathi translation with more lenient grading
def grade_translation(target_english, student_marathi, correct_marathi):
    try:
        # Initialize Bedrock client
        bedrock = boto3.client("bedrock-runtime")

        # Construct prompt for the LLM using Claude's message format
        message_content = [
            {
                "role": "system",
                "content": """You are a Marathi language teacher grading student writing.
                Grade based on:
                - If the general meaning is conveyed using correct grammar and proper nouns, the answer should be accepted
                - Focus more on meaning and communication than exact wording
                - Be supportive and encouraging rather than strict
                
                Use S/A/B/C grading scale where:
                S: Great job! The meaning is clearly conveyed
                A: Good work with minor issues that don't affect understanding
                B: The basic meaning is there but with some grammar issues
                C: Meaning is unclear or has significant issues
                
                Always respond with exactly this format:
                Grade: [S/A/B/C]
                Feedback: [Your detailed feedback explaining the grade with specific examples]""",
            },
            {
                "role": "user",
                "content": f"""Grade this Marathi writing sample:
                Target English sentence: {target_english}
                Student's Marathi: {student_marathi}
                Correct Marathi translation: {correct_marathi}""",
            },
        ]

        # Call Bedrock with proper Claude message format
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
            body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "temperature": 0.2,
                    "messages": message_content,
                }
            ),
        )

        # Parse response
        response_body = json.loads(response["body"].read())
        completion = response_body.get("content", [{}])[0].get("text", "")

        # Extract grade and feedback using more robust pattern matching
        grade_match = re.search(r"Grade:\s*([SABC])", completion, re.IGNORECASE)
        feedback_match = re.search(r"Feedback:\s*([\s\S]*)", completion)

        if grade_match and feedback_match:
            grade = grade_match.group(1).upper()  # Normalize to uppercase
            feedback = feedback_match.group(1).strip()
        else:
            # If pattern matching fails, provide a default assessment
            st.warning("Grading format was unexpected. Providing a generic assessment.")

            # Basic comparison - be more lenient
            from difflib import SequenceMatcher

            similarity = SequenceMatcher(
                None, student_marathi.strip(), correct_marathi.strip()
            ).ratio()

            if similarity > 0.8:
                grade = "S"
                feedback = "Your translation conveys the meaning effectively!"
            elif similarity > 0.6:
                grade = "A"
                feedback = "Good job! Your translation captures the essential meaning with minor differences."
            elif similarity > 0.4:
                grade = "B"
                feedback = "Your translation conveys some of the meaning. Keep working on sentence structure."
            else:
                grade = "C"
                feedback = "Your translation has some challenges. Try focusing on the key words in the sentence."

        return {"grade": grade, "feedback": feedback}

    except Exception as e:
        st.warning("Could not connect to grading service. Using simplified grading.")

        # Simple fallback grading logic without using the LLM
        # String similarity ratio as a basic metric
        from difflib import SequenceMatcher

        def similarity_ratio(a, b):
            return SequenceMatcher(None, a, b).ratio()

        # Calculate similarity between student's answer and correct answer
        sim_ratio = similarity_ratio(student_marathi.strip(), correct_marathi.strip())

        # Assign grade based on similarity - be more lenient
        if sim_ratio > 0.7:
            grade = "S"
            feedback = (
                "Excellent! Your translation effectively communicates the meaning."
            )
        elif sim_ratio > 0.5:
            grade = "A"
            feedback = "Very good translation that captures the main ideas."
        elif sim_ratio > 0.3:
            grade = "B"
            feedback = "Good attempt that communicates some of the meaning."
        else:
            grade = "C"
            feedback = (
                "Your translation needs some work to better communicate the meaning."
            )

        return {"grade": grade, "feedback": feedback}


# Home page - Word selection and sentence generation
def show_home_page():
    st.title("Marathi Writing Practice App")
    st.subheader("Learn Marathi words by category")

    # Category input
    category = st.text_input(
        "Please enter any word category you want to practice writing:",
        placeholder="e.g., colors, animals, fruits",
    )

    # Fetch words when category is provided
    if category:
        if (
            st.session_state.words_data is None
            or st.session_state.words_data.get("group_name") != category
        ):
            words_data = fetch_words(category)
            if words_data:
                st.session_state.words_data = words_data
                st.session_state.selected_words = []
                st.session_state.sentence = None

    # Display word cards if data is available
    if st.session_state.words_data:
        st.subheader(f"Words in category: {st.session_state.words_data['group_name']}")
        st.write("Click on cards to select words for sentence generation (1-3 words)")

        # Display the word cards in a grid
        cols = st.columns(5)
        for i, word in enumerate(st.session_state.words_data["words"]):
            with cols[i % 5]:
                # Check if this word is selected
                is_selected = word in st.session_state.selected_words

                # Use a button for better interactivity
                if st.button(
                    f"{word['english']}\n{word['marathi']}",
                    key=f"word_{i}",
                    use_container_width=True,
                    type="primary" if is_selected else "secondary",
                ):
                    toggle_word_selection(word)
                    st.rerun()

        # Show selected words
        st.subheader("Selected Words")
        if st.session_state.selected_words:
            selected_cols = st.columns(3)
            for i, word in enumerate(st.session_state.selected_words):
                with selected_cols[i % 3]:
                    st.info(f"**{word['english']}** - {word['marathi']}")
        else:
            st.info("No words selected yet")

        # Generate sentence button
        if len(st.session_state.selected_words) >= 1:
            if st.button("Generate Sentence", use_container_width=True, type="primary"):
                with st.spinner("Generating sentence..."):
                    # Add a slight delay to simulate processing
                    time.sleep(1.5)
                    st.session_state.sentence = generate_sentence(
                        st.session_state.selected_words
                    )
        else:
            st.button(
                "Generate Sentence",
                use_container_width=True,
                disabled=True,
                help="Please select at least 1 word to generate a sentence",
            )

        # Display generated sentence and go to assessment button
        if st.session_state.sentence:
            st.markdown("### Generated Sentence")
            st.markdown(
                f"""
            <div class="sentence-container">
                <div class="english-sentence">{st.session_state.sentence['english_translation']}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Button to go to assessment page
            st.button(
                "Practice Translating This Sentence",
                on_click=go_to_assessment,
                use_container_width=True,
                type="primary",
            )
    else:
        st.info("Enter a category above to start practicing!")


# Assessment page - Translation challenge
def show_assessment_page():
    st.title("Marathi Translation Practice")

    if not st.session_state.sentence:
        st.error(
            "No sentence to practice with. Please go back and generate a sentence first."
        )
        st.button("Back to Home", on_click=go_to_home)
        return

    # Show the English sentence
    st.subheader("Translate this sentence to Marathi:")
    st.markdown(
        f"""
    <div class="sentence-container">
        <div class="english-sentence">{st.session_state.sentence['english_translation']}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Input method selection
    st.markdown(
        """
    <div class="input-method-container">
        <h3>Choose your input method:</h3>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(
            "Text Input",
            use_container_width=True,
            type="primary" if st.session_state.input_method == "text" else "secondary",
        ):
            st.session_state.input_method = "text"
            st.session_state.recognized_text = None
            st.rerun()
    with col2:
        if st.button(
            "Draw on Canvas",
            use_container_width=True,
            type=(
                "primary" if st.session_state.input_method == "canvas" else "secondary"
            ),
        ):
            st.session_state.input_method = "canvas"
            st.session_state.recognized_text = None
            st.rerun()
    with col3:
        if st.button(
            "Upload Image",
            use_container_width=True,
            type="primary" if st.session_state.input_method == "image" else "secondary",
        ):
            st.session_state.input_method = "image"
            st.session_state.recognized_text = None
            st.rerun()

    # Based on input method, show appropriate input form
    user_translation = ""

    if st.session_state.input_method == "text":
        user_translation = st.text_area("Your translation in Marathi:", height=100)
        check_button_disabled = not user_translation

    elif st.session_state.input_method == "canvas":
        st.markdown('<div class="canvas-container">', unsafe_allow_html=True)
        
        # Simple drawing instructions
        st.markdown("""
        <div class="drawing-instructions">
            Write your Marathi translation below. Use the clear button to start over.
        </div>
        """, unsafe_allow_html=True)
        
        # Create a canvas component with simplified options
        from streamlit_drawable_canvas import st_canvas
        
        # Canvas controls in columns for better layout
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Simplified canvas with just essential parameters
            canvas_result = st_canvas(
                stroke_width=3,
                stroke_color="#000000",
                background_color="#FFFFFF",
                height=300,
                width=600,
                drawing_mode="freedraw",
                key="canvas",
            )
        
        with col2:
            # Add stroke width control
            stroke_width = st.slider("Stroke width", 1, 10, 3)
            
            # Add a clear button
            if st.button("Clear Canvas"):
                # This will force the canvas to reset
                st.session_state.pop("canvas", None)
                st.rerun()
        
        # Process drawing button
        if canvas_result.image_data is not None:
            # Convert the canvas image data to bytes
            canvas_image = Image.fromarray(canvas_result.image_data.astype("uint8"))
            buf = io.BytesIO()
            canvas_image.save(buf, format="PNG")
            image_bytes = buf.getvalue()
            
            # Display a thumbnail of the current drawing
            st.image(canvas_image, width=150, caption="Current Drawing")
            
            # Button to process the canvas
            if st.button("Process Drawing", use_container_width=True):
                with st.spinner("Recognizing text from drawing..."):
                    recognized_text = extract_text_from_image(image_bytes)
                    st.session_state.recognized_text = recognized_text
                    st.rerun()
        
        # Display recognized text if available
        if st.session_state.recognized_text:
            st.markdown("""
            <div class="recognized-text-container">
                <h4>Recognized Text:</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Allow user to edit the recognized text
            user_translation = st.text_area(
                "Edit if needed:", 
                value=st.session_state.recognized_text,
                height=100
            )
            check_button_disabled = False
        else:
            user_translation = ""
            check_button_disabled = True
        
        st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.input_method == "image":
        st.markdown('<div class="canvas-container">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload an image of your Marathi handwriting", type=["jpg", "jpeg", "png"]
        )

        if uploaded_file is not None:
            # Display the uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)

            # Button to process the image
            if st.button("Process Image", use_container_width=True):
                with st.spinner("Recognizing text from image..."):
                    image_bytes = uploaded_file.getvalue()
                    recognized_text = extract_text_from_image(image_bytes)
                    st.session_state.recognized_text = recognized_text
                    st.rerun()

        if st.session_state.recognized_text:
            st.write(st.session_state.recognized_text)
            user_translation = st.session_state.recognized_text
            check_button_disabled = False
        else:
            check_button_disabled = True

        st.markdown("</div>", unsafe_allow_html=True)

    # Check translation button
    if st.button(
        "Check My Translation",
        use_container_width=True,
        type="primary",
        disabled=check_button_disabled,
    ):
        with st.spinner("Analyzing your translation..."):
            # Add a slight delay to simulate processing
            time.sleep(1.5)

            # Grade the translation
            grading_result = grade_translation(
                st.session_state.sentence["english_translation"],
                user_translation,
                st.session_state.sentence["marathi_sentence"],
            )

            # Save assessment results
            st.session_state.assessment_grade = grading_result["grade"]
            st.session_state.assessment_feedback = grading_result["feedback"]

            # If there was recognized text, include it in the feedback
            if (
                st.session_state.input_method in ["canvas", "image"]
                and st.session_state.recognized_text
            ):
                st.session_state.recognized_text_for_feedback = (
                    st.session_state.recognized_text
                )
            else:
                st.session_state.recognized_text_for_feedback = None

            # Rerun to update the UI
            st.rerun()

    # Display assessment results if available
    if st.session_state.assessment_grade:
        grade = st.session_state.assessment_grade
        feedback = st.session_state.assessment_feedback

        # Determine grade CSS class
        grade_class = f"grade-{grade.lower()}"

        # Show feedback
        st.markdown(
            f"""
        <div class="grade-container {grade_class}">
            <h3>Grade: {grade}</h3>
            <p>{feedback}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # If recognized text was used, show what was extracted
        if (
            hasattr(st.session_state, "recognized_text_for_feedback")
            and st.session_state.recognized_text_for_feedback
        ):
            st.info(st.session_state.recognized_text_for_feedback)

        # Show correct translation
        st.markdown("### Model Translation")
        st.markdown(
            f"""
        <div class="sentence-container">
            <div class="marathi-sentence">{st.session_state.sentence['marathi_sentence']}</div>
            <div class="english-sentence">{st.session_state.sentence['english_translation']}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Button to go back to home to try another category
        st.button(
            "Practice More Words",
            on_click=go_to_home,
            use_container_width=True,
            type="primary",
        )

    # Always show a back button
    st.button("Back to Words", on_click=go_to_home)


# Main app logic - determines which page to show
if st.session_state.page == "home":
    show_home_page()
elif st.session_state.page == "assessment":
    show_assessment_page()

# Add a footer
st.markdown("---")
st.markdown("Made with ❤️ for Marathi language learners")
