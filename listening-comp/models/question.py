"""
Data model for questions
"""
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

@dataclass
class QuestionOption:
    """Represents a single question option"""
    text: str
    is_correct: bool = False
    explanation: Optional[str] = None

@dataclass
class Question:
    """Data model for a practice question"""
    # Basic metadata
    id: str
    practice_type: str
    topic: str
    created_at: datetime = field(default_factory=datetime.now)
    
    # Question content
    introduction: Optional[str] = None  
    conversation: Optional[str] = None  # For dialogue practice
    situation: Optional[str] = None     # For phrase matching
    question_text: str = ""
    options: List[QuestionOption] = field(default_factory=list)
    
    # Audio data
    audio_file: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], question_id: str) -> 'Question':
        """
        Create a Question object from dictionary data
        
        Args:
            data: Dictionary containing question data
            question_id: Unique identifier for the question
            
        Returns:
            Question: A new Question instance
        """
        question_dict = data.get('question', {})
        
        # Create options list
        options = []
        for i, option_text in enumerate(question_dict.get('Options', [])):
            is_correct = i + 1 == question_dict.get('CorrectAnswer', 1)
            options.append(QuestionOption(
                text=option_text,
                is_correct=is_correct
            ))
        
        # Parse creation timestamp
        created_at = datetime.strptime(
            data.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "%Y-%m-%d %H:%M:%S"
        )
        
        return cls(
            id=question_id,
            practice_type=data.get('practice_type', ''),
            topic=data.get('topic', ''),
            created_at=created_at,
            introduction=question_dict.get('Introduction'),
            conversation=question_dict.get('Conversation'),
            situation=question_dict.get('Situation'),
            question_text=question_dict.get('Question', ''),
            options=options,
            audio_file=data.get('audio_file')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Question object to dictionary format for storage
        
        Returns:
            Dict: Dictionary representation of the question
        """
        # Create question content dictionary
        question_dict = {
            'Question': self.question_text,
            'Options': [option.text for option in self.options],
        }
        
        # Add correct answer index (1-based)
        for i, option in enumerate(self.options):
            if option.is_correct:
                question_dict['CorrectAnswer'] = i + 1
                break
        
        # Add practice type specific fields
        if self.practice_type == "Dialogue Practice":
            if self.introduction:
                question_dict['Introduction'] = self.introduction
            if self.conversation:
                question_dict['Conversation'] = self.conversation
        else:
            if self.situation:
                question_dict['Situation'] = self.situation
        
        # Create full data dictionary
        return {
            'question': question_dict,
            'practice_type': self.practice_type,
            'topic': self.topic,
            'created_at': self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'audio_file': self.audio_file
        }