import boto3
import json
from typing import Dict, List, Optional
from backend.vector_store import QuestionVectorStore

class QuestionGenerator:
    def __init__(self):
        """Initialize Bedrock client and vector store"""
        self.bedrock_client = boto3.client('bedrock-runtime', region_name="us-east-1")
        self.vector_store = QuestionVectorStore()
        self.model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

    def _invoke_bedrock(self, prompt: str) -> Optional[str]:
        """Invoke Bedrock with the given prompt"""
        try:
            messages = [{
                "role": "user",
                "content": [{
                    "text": prompt
                }]
            }]
            
            response = self.bedrock_client.converse(
                modelId=self.model_id,
                messages=messages,
                inferenceConfig={"temperature": 0.7}
            )
            
            return response['output']['message']['content'][0]['text']
        except Exception as e:
            print(f"Error invoking Bedrock: {str(e)}")
            return None

    def generate_similar_question(self, section_num: int, topic: str) -> Dict:
        """Generate a new question similar to existing ones on a given topic"""
        # Get similar questions for context
        similar_questions = self.vector_store.search_similar_questions(section_num, topic, n_results=3)
        
        if not similar_questions:
            # If no similar questions found, generate a new one from scratch
            return self.generate_new_question(section_num, topic)
        
        # Create context from similar questions
        context = "Here are some example Marathi listening questions:\n\n"
        for idx, q in enumerate(similar_questions, 1):
            if section_num == 2:
                context += f"Example {idx}:\n"
                context += f"Introduction: {q.get('Introduction', '')}\n"
                context += f"Conversation: {q.get('Conversation', '')}\n"
                context += f"Question: {q.get('Question', '')}\n"
                if 'Options' in q:
                    context += "Options:\n"
                    for i, opt in enumerate(q['Options'], 1):
                        context += f"{i}. {opt}\n"
            else:  # section 3
                context += f"Example {idx}:\n"
                context += f"Situation: {q.get('Situation', '')}\n"
                context += f"Question: {q.get('Question', '')}\n"
                if 'Options' in q:
                    context += "Options:\n"
                    for i, opt in enumerate(q['Options'], 1):
                        context += f"{i}. {opt}\n"
            context += "\n"

        # Create prompt for generating new question
        prompt = f"""Based on the following example Marathi listening questions, create a new question about {topic}.
        The question should follow the same format but be different from the examples.
        Make sure the question tests listening comprehension and has a clear correct answer.
        
        {context}
        
        Generate a new question following the exact same format as above. Include all components (Introduction/Situation, 
        Conversation/Question, and Options). Make sure the question is challenging but fair, and the options are plausible 
        but with only one clearly correct answer. Return ONLY the question without any additional text.
        
        New Question:
        """

        # Generate new question
        response = self._invoke_bedrock(prompt)
        if not response:
            return None

        # Parse the generated question
        return self._parse_question_response(response)

    def generate_new_question(self, section_num: int, topic: str) -> Dict:
        """Generate a new question from scratch when no similar questions are available"""
        template = ""
        if section_num == 2:
            template = """
            Create a Marathi language listening practice question on the topic of {topic}.
            
            The question should have these components:
            1. Introduction: A brief setup introducing the scenario (in Marathi)
            2. Conversation: A dialogue between two people (in Marathi)
            3. Question: What the listener needs to determine (in Marathi)
            4. Options: Four possible answers in Marathi, with only one correct answer
            
            Format the response exactly like this:
            
            Introduction:
            [introduction text in Marathi]
            
            Conversation:
            [conversation text in Marathi]
            
            Question:
            [question text in Marathi]
            
            Options:
            1. [first option in Marathi]
            2. [second option in Marathi]
            3. [third option in Marathi]
            4. [fourth option in Marathi]
            """
        else:  # section 3
            template = """
            Create a Marathi language phrase matching practice question on the topic of {topic}.
            
            The question should have these components:
            1. Situation: A scenario where the listener needs to choose an appropriate phrase (in Marathi)
            2. Question: Usually "काय म्हणाल?" (What would you say?) in Marathi
            3. Options: Four possible phrases in Marathi, with only one being the most appropriate
            
            Format the response exactly like this:
            
            Situation:
            [situation text in Marathi]
            
            Question:
            काय म्हणाल?
            
            Options:
            1. [first phrase in Marathi]
            2. [second phrase in Marathi]
            3. [third phrase in Marathi]
            4. [fourth phrase in Marathi]
            """
        
        prompt = template.format(topic=topic)
        response = self._invoke_bedrock(prompt)
        
        if not response:
            # Create a default question if generation fails
            return self._create_default_question(section_num, topic)
            
        return self._parse_question_response(response)

    def _parse_question_response(self, response: str) -> Dict:
        """Parse the generated question response"""
        try:
            lines = response.strip().split('\n')
            question = {}
            current_key = None
            current_value = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith("Introduction:"):
                    if current_key:
                        question[current_key] = ' '.join(current_value)
                    current_key = 'Introduction'
                    current_value = [line.replace("Introduction:", "").strip()]
                elif line.startswith("Conversation:"):
                    if current_key:
                        question[current_key] = ' '.join(current_value)
                    current_key = 'Conversation'
                    current_value = [line.replace("Conversation:", "").strip()]
                elif line.startswith("Situation:"):
                    if current_key:
                        question[current_key] = ' '.join(current_value)
                    current_key = 'Situation'
                    current_value = [line.replace("Situation:", "").strip()]
                elif line.startswith("Question:"):
                    if current_key:
                        question[current_key] = ' '.join(current_value)
                    current_key = 'Question'
                    current_value = [line.replace("Question:", "").strip()]
                elif line.startswith("Options:"):
                    if current_key:
                        question[current_key] = ' '.join(current_value)
                    current_key = 'Options'
                    current_value = []
                elif line[0].isdigit() and line[1] == "." and current_key == 'Options':
                    current_value.append(line[2:].strip())
                elif current_key:
                    current_value.append(line)
            
            if current_key:
                if current_key == 'Options':
                    question[current_key] = current_value
                else:
                    question[current_key] = ' '.join(current_value)
            
            # Ensure we have exactly 4 options
            if 'Options' not in question or len(question.get('Options', [])) != 4:
                # Use default options if we don't have exactly 4
                question['Options'] = [
                    "पहिला पर्याय",
                    "दुसरा पर्याय",
                    "तिसरा पर्याय",
                    "चौथा पर्याय"
                ]
            
            return question
        except Exception as e:
            print(f"Error parsing generated question: {str(e)}")
            return self._create_default_question(2, "default") # Default to section 2
            
    def _create_default_question(self, section_num: int, topic: str) -> Dict:
        """Create a default question when generation fails"""
        if section_num == 2:
            return {
                'Introduction': 'एका दुकानात दोन व्यक्ती संवाद करत आहेत.',
                'Conversation': 'पहिली व्यक्ती: नमस्कार, मला काही फळे हवी आहेत.\nदुसरी व्यक्ती: हो, आपल्याला कोणती फळे हवी आहेत?\nपहिली व्यक्ती: मला केळी, सफरचंद आणि संत्री हवी आहेत.\nदुसरी व्यक्ती: एक किलो प्रत्येकी का?\nपहिली व्यक्ती: हो, आणि थोडी द्राक्षे सुद्धा.',
                'Question': 'पहिल्या व्यक्तीला कोणती फळे हवी आहेत?',
                'Options': [
                    'केळी, सफरचंद आणि संत्री',
                    'केळी, सफरचंद आणि द्राक्षे',
                    'सफरचंद, संत्री आणि द्राक्षे',
                    'केळी, संत्री आणि द्राक्षे'
                ]
            }
        else:  # section 3
            return {
                'Situation': 'तुम्ही एका मित्राला भेटता आणि त्याचे नवीन घर बघण्यास जाता.',
                'Question': 'काय म्हणाल?',
                'Options': [
                    'तुमचे घर खूप छान आहे.',
                    'तुमचे घर कुठे आहे?',
                    'मला घरी जायचे आहे.',
                    'तुम्ही कोणत्या घरात राहता?'
                ]
            }

    def get_feedback(self, question: Dict, selected_answer: int) -> Dict:
        """Generate feedback for the selected answer"""
        if not question or 'Options' not in question:
            return None

        # Create prompt for generating feedback
        prompt = f"""Given this Marathi listening question and the selected answer, provide feedback explaining if it's correct 
        and why. Keep the explanation clear and concise.
        
        """
        if 'Introduction' in question:
            prompt += f"Introduction: {question['Introduction']}\n"
            prompt += f"Conversation: {question['Conversation']}\n"
        else:
            prompt += f"Situation: {question['Situation']}\n"
        
        prompt += f"Question: {question['Question']}\n"
        prompt += "Options:\n"
        for i, opt in enumerate(question['Options'], 1):
            prompt += f"{i}. {opt}\n"
        
        prompt += f"\nSelected Answer: {selected_answer}\n"
        prompt += "\nProvide feedback in JSON format with these fields:\n"
        prompt += "- correct: true/false\n"
        prompt += "- explanation: brief explanation in Marathi of why the answer is correct/incorrect\n"
        prompt += "- correct_answer: the number of the correct option (1-4)\n"

        # Get feedback
        response = self._invoke_bedrock(prompt)
        if not response:
            return None

        try:
            # Parse the JSON response
            feedback = json.loads(response.strip())
            return feedback
        except:
            # If JSON parsing fails, return a basic response with a default correct answer
            return {
                "correct": False,
                "explanation": "प्रतिसाद मिळवताना त्रुटी आली. कृपया पुन्हा प्रयत्न करा.",
                "correct_answer": 1  # Default to first option
            }