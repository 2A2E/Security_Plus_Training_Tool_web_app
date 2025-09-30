"""
Unit tests for QuestionModel classes
"""
import pytest
from datetime import datetime
from models.question_models import (
    QuestionModel, 
    MultipleChoiceQuestion, 
    TrueFalseQuestion, 
    FillInBlankQuestion, 
    ScenarioBasedQuestion,
    create_question
)
from models.enums import QuestionType, DifficultyLevel, QuestionCategory

class TestQuestionModel:
    """Test cases for base QuestionModel class"""
    
    def test_init_basic(self):
        """Test basic QuestionModel initialization"""
        question = QuestionModel(
            question_text="What is a firewall?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            category=QuestionCategory.TECHNOLOGIES_TOOLS,
            difficulty=DifficultyLevel.BEGINNER,
            explanation="A firewall is a security device."
        )
        
        assert question.question_text == "What is a firewall?"
        assert question.question_type == "multiple_choice"
        assert question.category == "technologies_tools"
        assert question.difficulty == "beginner"
        assert question.explanation == "A firewall is a security device."
        assert question.tags == []
        assert question.reference is None
        assert isinstance(question.created_at, datetime)
        assert isinstance(question.updated_at, datetime)
    
    def test_init_with_tags_and_reference(self):
        """Test QuestionModel initialization with tags and reference"""
        question = QuestionModel(
            question_text="What is encryption?",
            question_type=QuestionType.TRUE_FALSE,
            category=QuestionCategory.CRYPTOGRAPHY_PKI,
            difficulty=DifficultyLevel.INTERMEDIATE,
            explanation="Encryption protects data confidentiality.",
            tags=["encryption", "security", "cryptography"],
            reference="Security+ Study Guide"
        )
        
        assert question.tags == ["encryption", "security", "cryptography"]
        assert question.reference == "Security+ Study Guide"
    
    def test_init_with_additional_fields(self):
        """Test QuestionModel initialization with additional fields"""
        question = QuestionModel(
            question_text="Test question",
            question_type=QuestionType.MULTIPLE_CHOICE,
            category=QuestionCategory.TECHNOLOGIES_TOOLS,
            difficulty=DifficultyLevel.BEGINNER,
            explanation="Test explanation",
            custom_field="custom_value",
            another_field=123
        )
        
        assert question.custom_field == "custom_value"
        assert question.another_field == 123
    
    def test_to_dict(self):
        """Test converting question to dictionary"""
        question = QuestionModel(
            question_text="What is a firewall?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            category=QuestionCategory.TECHNOLOGIES_TOOLS,
            difficulty=DifficultyLevel.BEGINNER,
            explanation="A firewall is a security device.",
            tags=["firewall", "security"],
            reference="Security Guide",
            custom_field="custom_value"
        )
        
        result = question.to_dict()
        
        assert result['question_text'] == "What is a firewall?"
        assert result['question_type'] == "multiple_choice"
        assert result['category'] == "technologies_tools"
        assert result['difficulty'] == "beginner"
        assert result['explanation'] == "A firewall is a security device."
        assert result['tags'] == ["firewall", "security"]
        assert result['reference'] == "Security Guide"
        assert result['custom_field'] == "custom_value"
        assert 'created_at' in result
        assert 'updated_at' in result
    
    def test_from_dict(self):
        """Test creating question from dictionary"""
        data = {
            'question_text': 'What is a firewall?',
            'question_type': 'multiple_choice',
            'category': 'technologies_tools',
            'difficulty': 'beginner',
            'explanation': 'A firewall is a security device.',
            'tags': ['firewall', 'security'],
            'reference': 'Security Guide',
            'custom_field': 'custom_value',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        question = QuestionModel.from_dict(data)
        
        assert question.question_text == "What is a firewall?"
        assert question.question_type == "multiple_choice"
        assert question.category == "technologies_tools"
        assert question.difficulty == "beginner"
        assert question.explanation == "A firewall is a security device."
        assert question.tags == ["firewall", "security"]
        assert question.reference == "Security Guide"
        assert question.custom_field == "custom_value"
        assert isinstance(question.created_at, datetime)
        assert isinstance(question.updated_at, datetime)
    
    def test_from_dict_without_timestamps(self):
        """Test creating question from dictionary without timestamps"""
        data = {
            'question_text': 'What is a firewall?',
            'question_type': 'multiple_choice',
            'category': 'technologies_tools',
            'difficulty': 'beginner',
            'explanation': 'A firewall is a security device.'
        }
        
        question = QuestionModel.from_dict(data)
        
        assert question.question_text == "What is a firewall?"
        assert isinstance(question.created_at, datetime)
        assert isinstance(question.updated_at, datetime)

class TestMultipleChoiceQuestion:
    """Test cases for MultipleChoiceQuestion class"""
    
    def test_init(self):
        """Test MultipleChoiceQuestion initialization"""
        question = MultipleChoiceQuestion(
            question_text="What is a firewall?",
            category=QuestionCategory.TECHNOLOGIES_TOOLS,
            difficulty=DifficultyLevel.BEGINNER,
            explanation="A firewall is a security device.",
            options=["A security device", "A network protocol", "A type of virus"],
            correct_answer=0,
            tags=["firewall", "security"],
            reference="Security Guide"
        )
        
        assert question.question_text == "What is a firewall?"
        assert question.question_type == "multiple_choice"
        assert question.category == "technologies_tools"
        assert question.difficulty == "beginner"
        assert question.explanation == "A firewall is a security device."
        assert question.options == ["A security device", "A network protocol", "A type of virus"]
        assert question.correct_answer == 0
        assert question.tags == ["firewall", "security"]
        assert question.reference == "Security Guide"
    
    def test_init_with_string_correct_answer(self):
        """Test MultipleChoiceQuestion with string correct answer"""
        question = MultipleChoiceQuestion(
            question_text="What is a firewall?",
            category=QuestionCategory.TECHNOLOGIES_TOOLS,
            difficulty=DifficultyLevel.BEGINNER,
            explanation="A firewall is a security device.",
            options=["A security device", "A network protocol", "A type of virus"],
            correct_answer="0",
            tags=["firewall", "security"]
        )
        
        assert question.correct_answer == "0"
    
    def test_to_dict_includes_options_and_correct_answer(self):
        """Test that to_dict includes options and correct_answer"""
        question = MultipleChoiceQuestion(
            question_text="What is a firewall?",
            category=QuestionCategory.TECHNOLOGIES_TOOLS,
            difficulty=DifficultyLevel.BEGINNER,
            explanation="A firewall is a security device.",
            options=["A security device", "A network protocol"],
            correct_answer=0
        )
        
        result = question.to_dict()
        
        assert 'options' in result
        assert 'correct_answer' in result
        assert result['options'] == ["A security device", "A network protocol"]
        assert result['correct_answer'] == 0

class TestTrueFalseQuestion:
    """Test cases for TrueFalseQuestion class"""
    
    def test_init(self):
        """Test TrueFalseQuestion initialization"""
        question = TrueFalseQuestion(
            question_text="Is encryption important for security?",
            category=QuestionCategory.CRYPTOGRAPHY_PKI,
            difficulty=DifficultyLevel.BEGINNER,
            explanation="Encryption protects data confidentiality.",
            correct_answer=True,
            tags=["encryption", "security"],
            reference="Crypto Guide"
        )
        
        assert question.question_text == "Is encryption important for security?"
        assert question.question_type == "true_false"
        assert question.category == "cryptography_pki"
        assert question.difficulty == "beginner"
        assert question.explanation == "Encryption protects data confidentiality."
        assert question.correct_answer is True
        assert question.tags == ["encryption", "security"]
        assert question.reference == "Crypto Guide"
    
    def test_init_with_false_answer(self):
        """Test TrueFalseQuestion with False answer"""
        question = TrueFalseQuestion(
            question_text="Is plain text secure?",
            category=QuestionCategory.CRYPTOGRAPHY_PKI,
            difficulty=DifficultyLevel.BEGINNER,
            explanation="Plain text is not secure.",
            correct_answer=False
        )
        
        assert question.correct_answer is False
    
    def test_to_dict_includes_correct_answer(self):
        """Test that to_dict includes correct_answer"""
        question = TrueFalseQuestion(
            question_text="Is encryption important?",
            category=QuestionCategory.CRYPTOGRAPHY_PKI,
            difficulty=DifficultyLevel.BEGINNER,
            explanation="Yes, encryption is important.",
            correct_answer=True
        )
        
        result = question.to_dict()
        
        assert 'correct_answer' in result
        assert result['correct_answer'] is True

class TestFillInBlankQuestion:
    """Test cases for FillInBlankQuestion class"""
    
    def test_init(self):
        """Test FillInBlankQuestion initialization"""
        question = FillInBlankQuestion(
            question_text="What does PKI stand for?",
            category=QuestionCategory.CRYPTOGRAPHY_PKI,
            difficulty=DifficultyLevel.INTERMEDIATE,
            explanation="PKI stands for Public Key Infrastructure.",
            correct_answers=["Public Key Infrastructure", "PKI"],
            case_sensitive=False,
            tags=["pki", "cryptography"],
            reference="Crypto Guide"
        )
        
        assert question.question_text == "What does PKI stand for?"
        assert question.question_type == "fill_in_blank"
        assert question.category == "cryptography_pki"
        assert question.difficulty == "intermediate"
        assert question.explanation == "PKI stands for Public Key Infrastructure."
        assert question.correct_answers == ["Public Key Infrastructure", "PKI"]
        assert question.case_sensitive is False
        assert question.tags == ["pki", "cryptography"]
        assert question.reference == "Crypto Guide"
    
    def test_init_with_case_sensitive(self):
        """Test FillInBlankQuestion with case sensitive matching"""
        question = FillInBlankQuestion(
            question_text="What is the capital of France?",
            category=QuestionCategory.TECHNOLOGIES_TOOLS,
            difficulty=DifficultyLevel.BEGINNER,
            explanation="Paris is the capital.",
            correct_answers=["Paris"],
            case_sensitive=True
        )
        
        assert question.case_sensitive is True
    
    def test_to_dict_includes_correct_answers_and_case_sensitive(self):
        """Test that to_dict includes correct_answers and case_sensitive"""
        question = FillInBlankQuestion(
            question_text="What does PKI stand for?",
            category=QuestionCategory.CRYPTOGRAPHY_PKI,
            difficulty=DifficultyLevel.INTERMEDIATE,
            explanation="PKI explanation.",
            correct_answers=["Public Key Infrastructure"],
            case_sensitive=False
        )
        
        result = question.to_dict()
        
        assert 'correct_answers' in result
        assert 'case_sensitive' in result
        assert result['correct_answers'] == ["Public Key Infrastructure"]
        assert result['case_sensitive'] is False

class TestScenarioBasedQuestion:
    """Test cases for ScenarioBasedQuestion class"""
    
    def test_init(self):
        """Test ScenarioBasedQuestion initialization"""
        question = ScenarioBasedQuestion(
            scenario_text="A company's network is experiencing slow performance...",
            question_text="What should be the first step to investigate?",
            category=QuestionCategory.SECURITY_OPERATIONS,
            difficulty=DifficultyLevel.ADVANCED,
            explanation="First, check network monitoring tools.",
            options=["Check logs", "Restart servers", "Update software", "Change passwords"],
            correct_answer=0,
            tags=["scenario", "network", "troubleshooting"],
            reference="Network Security Guide"
        )
        
        assert question.scenario_text == "A company's network is experiencing slow performance..."
        assert question.question_text == "What should be the first step to investigate?"
        assert question.question_type == "scenario_based"
        assert question.category == "security_operations"
        assert question.difficulty == "advanced"
        assert question.explanation == "First, check network monitoring tools."
        assert question.options == ["Check logs", "Restart servers", "Update software", "Change passwords"]
        assert question.correct_answer == 0
        assert question.tags == ["scenario", "network", "troubleshooting"]
        assert question.reference == "Network Security Guide"
    
    def test_init_without_options(self):
        """Test ScenarioBasedQuestion without options (for true/false scenarios)"""
        question = ScenarioBasedQuestion(
            scenario_text="A security incident occurred...",
            question_text="Should the incident be reported immediately?",
            category=QuestionCategory.INCIDENT_RESPONSE,
            difficulty=DifficultyLevel.INTERMEDIATE,
            explanation="Yes, incidents should be reported immediately.",
            correct_answer=True
        )
        
        assert question.scenario_text == "A security incident occurred..."
        assert question.question_text == "Should the incident be reported immediately?"
        assert question.options is None
        assert question.correct_answer is True
    
    def test_to_dict_includes_scenario_fields(self):
        """Test that to_dict includes scenario-specific fields"""
        question = ScenarioBasedQuestion(
            scenario_text="Test scenario",
            question_text="Test question",
            category=QuestionCategory.SECURITY_OPERATIONS,
            difficulty=DifficultyLevel.INTERMEDIATE,
            explanation="Test explanation",
            options=["Option A", "Option B"],
            correct_answer=0
        )
        
        result = question.to_dict()
        
        assert 'scenario_text' in result
        assert 'options' in result
        assert 'correct_answer' in result
        assert result['scenario_text'] == "Test scenario"
        assert result['options'] == ["Option A", "Option B"]
        assert result['correct_answer'] == 0

class TestCreateQuestionFactory:
    """Test cases for create_question factory function"""
    
    def test_create_multiple_choice_question(self):
        """Test creating multiple choice question via factory"""
        question = create_question(
            question_type="multiple_choice",
            question_text="What is a firewall?",
            category=QuestionCategory.TECHNOLOGIES_TOOLS,
            difficulty=DifficultyLevel.BEGINNER,
            explanation="A firewall is a security device.",
            options=["A security device", "A network protocol"],
            correct_answer=0
        )
        
        assert isinstance(question, MultipleChoiceQuestion)
        assert question.question_type == "multiple_choice"
        assert question.options == ["A security device", "A network protocol"]
        assert question.correct_answer == 0
    
    def test_create_true_false_question(self):
        """Test creating true/false question via factory"""
        question = create_question(
            question_type="true_false",
            question_text="Is encryption important?",
            category=QuestionCategory.CRYPTOGRAPHY_PKI,
            difficulty=DifficultyLevel.BEGINNER,
            explanation="Yes, encryption is important.",
            correct_answer=True
        )
        
        assert isinstance(question, TrueFalseQuestion)
        assert question.question_type == "true_false"
        assert question.correct_answer is True
    
    def test_create_fill_in_blank_question(self):
        """Test creating fill-in-blank question via factory"""
        question = create_question(
            question_type="fill_in_blank",
            question_text="What does PKI stand for?",
            category=QuestionCategory.CRYPTOGRAPHY_PKI,
            difficulty=DifficultyLevel.INTERMEDIATE,
            explanation="PKI stands for Public Key Infrastructure.",
            correct_answers=["Public Key Infrastructure"],
            case_sensitive=False
        )
        
        assert isinstance(question, FillInBlankQuestion)
        assert question.question_type == "fill_in_blank"
        assert question.correct_answers == ["Public Key Infrastructure"]
        assert question.case_sensitive is False
    
    def test_create_scenario_based_question(self):
        """Test creating scenario-based question via factory"""
        question = create_question(
            question_type="scenario_based",
            scenario_text="Test scenario",
            question_text="Test question",
            category=QuestionCategory.SECURITY_OPERATIONS,
            difficulty=DifficultyLevel.ADVANCED,
            explanation="Test explanation",
            options=["Option A", "Option B"],
            correct_answer=0
        )
        
        assert isinstance(question, ScenarioBasedQuestion)
        assert question.question_type == "scenario_based"
        assert question.scenario_text == "Test scenario"
        assert question.options == ["Option A", "Option B"]
        assert question.correct_answer == 0
    
    def test_create_unknown_question_type(self):
        """Test creating question with unknown type falls back to base QuestionModel"""
        question = create_question(
            question_type="unknown_type",
            question_text="Test question",
            category=QuestionCategory.TECHNOLOGIES_TOOLS,
            difficulty=DifficultyLevel.BEGINNER,
            explanation="Test explanation"
        )
        
        assert isinstance(question, QuestionModel)
        assert question.question_type == "unknown_type"
    
    def test_create_question_case_insensitive_type(self):
        """Test creating question with case insensitive type"""
        question = create_question(
            question_type="MULTIPLE_CHOICE",  # Uppercase
            question_text="Test question",
            category=QuestionCategory.TECHNOLOGIES_TOOLS,
            difficulty=DifficultyLevel.BEGINNER,
            explanation="Test explanation",
            options=["Option A", "Option B"],
            correct_answer=0
        )
        
        assert isinstance(question, MultipleChoiceQuestion)
        assert question.question_type == "multiple_choice"  # Should be lowercase
