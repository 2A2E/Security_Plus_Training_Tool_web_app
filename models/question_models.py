"""
Question models for Security Plus Training Tool
"""
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from .enums import QuestionType, DifficultyLevel, QuestionCategory

class QuestionModel:
    """Base model for Security+ questions"""
    
    def __init__(self, 
                 question_text: str,
                 question_type: QuestionType,
                 category: QuestionCategory,
                 difficulty: DifficultyLevel,
                 explanation: str,
                 tags: List[str] = None,
                 reference: str = None,
                 **kwargs):
        """
        Initialize a question model
        
        Args:
            question_text: The main question text
            question_type: Type of question (multiple choice, true/false, etc.)
            category: Security+ domain category
            difficulty: Difficulty level
            explanation: Explanation of the correct answer
            tags: List of tags for categorization
            reference: Reference material or source
            **kwargs: Additional fields specific to question type
        """
        self.question_text = question_text
        self.question_type = question_type.value if isinstance(question_type, QuestionType) else question_type
        self.category = category.value if isinstance(category, QuestionCategory) else category
        self.difficulty = difficulty.value if isinstance(difficulty, DifficultyLevel) else difficulty
        self.explanation = explanation
        self.tags = tags or []
        self.reference = reference
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Store additional fields
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert question to dictionary for database storage"""
        return {
            'question_text': self.question_text,
            'question_type': self.question_type,
            'category': self.category,
            'difficulty': self.difficulty,
            'explanation': self.explanation,
            'tags': self.tags,
            'reference': self.reference,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            **{k: v for k, v in self.__dict__.items() 
               if k not in ['question_text', 'question_type', 'category', 'difficulty', 
                           'explanation', 'tags', 'reference', 'created_at', 'updated_at']}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuestionModel':
        """Create question from dictionary"""
        # Extract base fields
        base_fields = {
            'question_text': data.get('question_text'),
            'question_type': data.get('question_type'),
            'category': data.get('category'),
            'difficulty': data.get('difficulty'),
            'explanation': data.get('explanation'),
            'tags': data.get('tags', []),
            'reference': data.get('reference')
        }
        
        # Extract additional fields
        additional_fields = {k: v for k, v in data.items() 
                           if k not in base_fields and k not in ['_id', 'created_at', 'updated_at']}
        
        question = cls(**base_fields, **additional_fields)
        
        # Set timestamps if available
        if 'created_at' in data:
            question.created_at = data['created_at']
        if 'updated_at' in data:
            question.updated_at = data['updated_at']
        
        return question

class MultipleChoiceQuestion(QuestionModel):
    """Model for multiple choice questions"""
    
    def __init__(self, 
                 question_text: str,
                 category: QuestionCategory,
                 difficulty: DifficultyLevel,
                 explanation: str,
                 options: List[str],
                 correct_answer: Union[int, str],
                 tags: List[str] = None,
                 reference: str = None):
        """
        Initialize a multiple choice question
        
        Args:
            question_text: The main question text
            category: Security+ domain category
            difficulty: Difficulty level
            explanation: Explanation of the correct answer
            options: List of answer options
            correct_answer: Index (int) or value (str) of correct answer
            tags: List of tags for categorization
            reference: Reference material or source
        """
        super().__init__(
            question_text=question_text,
            question_type=QuestionType.MULTIPLE_CHOICE,
            category=category,
            difficulty=difficulty,
            explanation=explanation,
            tags=tags,
            reference=reference
        )
        self.options = options
        self.correct_answer = correct_answer

class TrueFalseQuestion(QuestionModel):
    """Model for true/false questions"""
    
    def __init__(self, 
                 question_text: str,
                 category: QuestionCategory,
                 difficulty: DifficultyLevel,
                 explanation: str,
                 correct_answer: bool,
                 tags: List[str] = None,
                 reference: str = None):
        """
        Initialize a true/false question
        
        Args:
            question_text: The main question text
            category: Security+ domain category
            difficulty: Difficulty level
            explanation: Explanation of the correct answer
            correct_answer: Boolean value of correct answer
            tags: List of tags for categorization
            reference: Reference material or source
        """
        super().__init__(
            question_text=question_text,
            question_type=QuestionType.TRUE_FALSE,
            category=category,
            difficulty=difficulty,
            explanation=explanation,
            tags=tags,
            reference=reference
        )
        self.correct_answer = correct_answer

class FillInBlankQuestion(QuestionModel):
    """Model for fill-in-the-blank questions"""
    
    def __init__(self, 
                 question_text: str,
                 category: QuestionCategory,
                 difficulty: DifficultyLevel,
                 explanation: str,
                 correct_answers: List[str],
                 case_sensitive: bool = False,
                 tags: List[str] = None,
                 reference: str = None):
        """
        Initialize a fill-in-the-blank question
        
        Args:
            question_text: The main question text
            category: Security+ domain category
            difficulty: Difficulty level
            explanation: Explanation of the correct answer
            correct_answers: List of acceptable correct answers
            case_sensitive: Whether answer matching is case sensitive
            tags: List of tags for categorization
            reference: Reference material or source
        """
        super().__init__(
            question_text=question_text,
            question_type=QuestionType.FILL_IN_BLANK,
            category=category,
            difficulty=difficulty,
            explanation=explanation,
            tags=tags,
            reference=reference
        )
        self.correct_answers = correct_answers
        self.case_sensitive = case_sensitive

class ScenarioBasedQuestion(QuestionModel):
    """Model for scenario-based questions"""
    
    def __init__(self, 
                 scenario_text: str,
                 question_text: str,
                 category: QuestionCategory,
                 difficulty: DifficultyLevel,
                 explanation: str,
                 options: List[str] = None,
                 correct_answer: Union[int, str, bool] = None,
                 tags: List[str] = None,
                 reference: str = None):
        """
        Initialize a scenario-based question
        
        Args:
            scenario_text: The scenario description
            question_text: The main question text
            category: Security+ domain category
            difficulty: Difficulty level
            explanation: Explanation of the correct answer
            options: List of answer options (for multiple choice scenarios)
            correct_answer: Correct answer (varies by question type)
            tags: List of tags for categorization
            reference: Reference material or source
        """
        super().__init__(
            question_text=question_text,
            question_type=QuestionType.SCENARIO_BASED,
            category=category,
            difficulty=difficulty,
            explanation=explanation,
            tags=tags,
            reference=reference
        )
        self.scenario_text = scenario_text
        self.options = options
        self.correct_answer = correct_answer

# Question factory function
def create_question(question_type: str, **kwargs) -> QuestionModel:
    """
    Factory function to create questions based on type
    
    Args:
        question_type: Type of question to create
        **kwargs: Question-specific parameters
        
    Returns:
        QuestionModel instance
    """
    question_type = question_type.lower()
    
    if question_type == QuestionType.MULTIPLE_CHOICE.value:
        return MultipleChoiceQuestion(**kwargs)
    elif question_type == QuestionType.TRUE_FALSE.value:
        return TrueFalseQuestion(**kwargs)
    elif question_type == QuestionType.FILL_IN_BLANK.value:
        return FillInBlankQuestion(**kwargs)
    elif question_type == QuestionType.SCENARIO_BASED.value:
        return ScenarioBasedQuestion(**kwargs)
    else:
        return QuestionModel(question_type=question_type, **kwargs)
