"""
Flashcard Service - Handles flashcard operations and session management
Organized by CompTIA Security+ SY0-701 Exam Domains (5 Sections)
"""
import json
import random
import time
from typing import List, Dict, Any, Optional
from database.question_manager import question_manager
import logging

logger = logging.getLogger(__name__)

class FlashcardSession:
    """Individual flashcard session"""
    
    def __init__(self, session_id: str, section: int, flashcards: List[Dict[str, Any]]):
        self.session_id = session_id
        self.section = section
        self.flashcards = flashcards
        self.current_card_index = 0
        self.created_at = time.time()
        self.last_accessed = time.time()
        
    def get_current_card(self) -> Optional[Dict[str, Any]]:
        """Get the current flashcard"""
        if 0 <= self.current_card_index < len(self.flashcards):
            return self.flashcards[self.current_card_index]
        return None
    
    def get_card(self, card_number: int) -> Optional[Dict[str, Any]]:
        """Get a specific card by number (1-based)"""
        index = card_number - 1
        if 0 <= index < len(self.flashcards):
            return self.flashcards[index]
        return None
    
    def get_all_cards(self) -> List[Dict[str, Any]]:
        """Get all flashcards in the session"""
        return self.flashcards
    
    def next_card(self) -> bool:
        """Move to next card, return True if successful"""
        if self.current_card_index < len(self.flashcards) - 1:
            self.current_card_index += 1
            self.last_accessed = time.time()
            return True
        return False
    
    def previous_card(self) -> bool:
        """Move to previous card, return True if successful"""
        if self.current_card_index > 0:
            self.current_card_index -= 1
            self.last_accessed = time.time()
            return True
        return False
    
    def set_card(self, card_number: int) -> bool:
        """Set current card by number (1-based)"""
        index = card_number - 1
        if 0 <= index < len(self.flashcards):
            self.current_card_index = index
            self.last_accessed = time.time()
            return True
        return False
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session has expired"""
        return (time.time() - self.last_accessed) > (timeout_minutes * 60)

class FlashcardService:
    """Service class for flashcard operations"""
    
    # Reuse the same sections from quiz service for consistency
    SECTION_CATEGORIES = {
        1: {
            'name': 'General Security Concepts',
            'description': 'Foundational security concepts, CIA triad, authentication, and basic principles',
            'categories': [
                'General Security Concepts',
                'Zero Trust Architecture',
                'Cryptography and PKI',
                'Identity and Access Management',
                'Physical Security',
                'Personnel Security'
            ]
        },
        2: {
            'name': 'Threats, Vulnerabilities, and Mitigations',
            'description': 'Threat actors, attack types, vulnerabilities, and mitigation strategies',
            'categories': [
                'Threats, Vulnerabilities, and Mitigations',
                'Threats, Attacks, and Vulnerabilities',
                'Threat Actors',
                'Threat Intelligence',
                'Attack Frameworks',
                'Application Attacks',
                'Network Attacks',
                'Physical Attacks',
                'Social Engineering Attacks',
                'Malware',
                'Exploits',
                'Vulnerability Management'
            ]
        },
        3: {
            'name': 'Security Architecture',
            'description': 'Security design, network architecture, cloud security, and configurations',
            'categories': [
                'Security Architecture',
                'Secure Network Design',
                'Secure Configurations',
                'Cloud Models & Virtualization',
                'Embedded/IoT/SCADA',
                'Resiliency',
                'Technologies and Tools'
            ]
        },
        4: {
            'name': 'Security Operations',
            'description': 'Security monitoring, incident response, forensics, and operational tasks',
            'categories': [
                'Security Operations',
                'Incident Response',
                'Digital Forensics',
                'SIEM and Monitoring',
                'Security Tools'
            ]
        },
        5: {
            'name': 'Security Program Management and Oversight',
            'description': 'Governance, risk management, compliance, policies, and standards',
            'categories': [
                'Security Program Management and Oversight',
                'Governance and Oversight',
                'Risk Management',
                'Policies and Procedures',
                'Regulations and Standards'
            ]
        }
    }
    
    def __init__(self):
        self.question_manager = question_manager
        self.sessions = {}  # In-memory session storage
        self._cleanup_expired_sessions()
    
    def get_all_sections(self) -> List[Dict[str, Any]]:
        """Get all available sections with their flashcard counts"""
        sections = []
        for section_num, section_data in self.SECTION_CATEGORIES.items():
            # Count total questions in this section
            total_cards = 0
            for category in section_data['categories']:
                count = self.question_manager.get_question_count(category=category)
                total_cards += count
            
            sections.append({
                'section_number': section_num,
                'name': section_data['name'],
                'description': section_data['description'],
                'total_cards': total_cards,
                'categories': section_data['categories']
            })
        
        return sections
    
    def create_flashcard_session(self, section: int, limit: Optional[int] = None) -> Optional[str]:
        """Create a flashcard session for a specific section"""
        try:
            if section not in self.SECTION_CATEGORIES:
                logger.error(f"Invalid section number: {section}. Must be 1-5.")
                return None
            
            section_data = self.SECTION_CATEGORIES[section]
            categories = section_data['categories']
            
            # Get questions from all categories in this section
            all_questions = []
            for category in categories:
                questions = self.question_manager.get_questions(
                    category=category,
                    limit=100  # Get more questions to have a good pool
                )
                all_questions.extend(questions)
            
            if not all_questions:
                logger.warning(f"No questions found for section {section}")
                return None
            
            # Parse JSON fields in questions
            all_questions = self._parse_question_json_fields(all_questions)
            
            # Convert questions to flashcards
            flashcards = []
            for question in all_questions:
                flashcard = self._convert_question_to_flashcard(question)
                if flashcard:
                    flashcards.append(flashcard)
            
            if not flashcards:
                logger.warning(f"No valid flashcards created for section {section}")
                return None
            
            # Shuffle and optionally limit to requested number
            random.shuffle(flashcards)
            if isinstance(limit, int) and limit > 0:
                flashcards = flashcards[:limit]
            
            # Create session
            session_id = f"flashcard_{section}_{int(time.time())}"
            session = FlashcardSession(session_id, section, flashcards)
            self.sessions[session_id] = session
            
            logger.info(f"Created flashcard session for section {section} ({section_data['name']}) with {len(flashcards)} cards")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating flashcard session: {e}")
            return None
    
    def get_flashcard(self, session_id: str, card_number: int = None) -> Optional[Dict[str, Any]]:
        """Get a specific flashcard from a session"""
        try:
            session = self.get_session(session_id)
            if not session:
                logger.error(f"Flashcard session not found: {session_id}")
                return None
            
            if card_number is None:
                # Get current card
                card = session.get_current_card()
                card_number = session.current_card_index + 1
            else:
                # Get specific card
                card = session.get_card(card_number)
            
            if card:
                # Add session metadata
                card['session_id'] = session_id
                card['card_number'] = card_number
                card['total_cards'] = len(session.flashcards)
                card['section'] = session.section
                card['section_name'] = self.SECTION_CATEGORIES[session.section]['name']
                
            return card
            
        except Exception as e:
            logger.error(f"Error getting flashcard: {e}")
            return None
    
    def get_all_flashcards(self, session_id: str, page: int = 1, per_page: int = 50) -> Dict[str, Any]:
        """Get paginated flashcards from a session for scroll mode"""
        try:
            session = self.get_session(session_id)
            if not session:
                logger.error(f"Flashcard session not found: {session_id}")
                return {'flashcards': [], 'total_cards': 0, 'current_page': 1, 'total_pages': 0, 'per_page': per_page}
            
            all_cards = session.get_all_cards()
            total_cards = len(all_cards)
            total_pages = (total_cards + per_page - 1) // per_page  # Ceiling division
            
            # Calculate pagination
            start_index = (page - 1) * per_page
            end_index = start_index + per_page
            page_cards = all_cards[start_index:end_index]
            
            # Add session metadata to each card
            for i, card in enumerate(page_cards):
                card['session_id'] = session_id
                card['card_number'] = start_index + i + 1
                card['total_cards'] = total_cards
                card['section'] = session.section
                card['section_name'] = self.SECTION_CATEGORIES[session.section]['name']
            
            return {
                'flashcards': page_cards,
                'total_cards': total_cards,
                'current_page': page,
                'total_pages': total_pages,
                'per_page': per_page,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
            
        except Exception as e:
            logger.error(f"Error getting paginated flashcards: {e}")
            return {'flashcards': [], 'total_cards': 0, 'current_page': 1, 'total_pages': 0, 'per_page': per_page}
    
    def navigate_card(self, session_id: str, direction: str) -> Optional[Dict[str, Any]]:
        """Navigate to next/previous card"""
        try:
            session = self.get_session(session_id)
            if not session:
                logger.error(f"Flashcard session not found: {session_id}")
                return None
            
            success = False
            if direction == 'next':
                success = session.next_card()
            elif direction == 'previous':
                success = session.previous_card()
            
            if success:
                return self.get_flashcard(session_id)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error navigating flashcard: {e}")
            return None
    
    def set_current_card(self, session_id: str, card_number: int) -> Optional[Dict[str, Any]]:
        """Set the current card by number"""
        try:
            session = self.get_session(session_id)
            if not session:
                logger.error(f"Flashcard session not found: {session_id}")
                return None
            
            if session.set_card(card_number):
                return self.get_flashcard(session_id)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error setting current card: {e}")
            return None
    
    def get_session(self, session_id: str) -> Optional[FlashcardSession]:
        """Get a flashcard session"""
        self._cleanup_expired_sessions()
        return self.sessions.get(session_id)
    
    def cleanup_session(self, session_id: str):
        """Clean up a specific session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleaned up flashcard session: {session_id}")
    
    def _cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        expired_sessions = []
        for session_id, session in self.sessions.items():
            if session.is_expired():
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.info(f"Cleaned up expired flashcard session: {session_id}")
    
    def _convert_question_to_flashcard(self, question: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert a question to flashcard format"""
        try:
            # Front of card: question text
            front = question.get('question_text', '')
            if not front:
                return None
            
            # Back of card: explanation + correct answer
            back_parts = []
            
            # Add explanation if available
            explanation = question.get('explanation', '')
            if explanation:
                back_parts.append(explanation)
            
            # Add correct answer based on question type
            question_type = question.get('question_type', '').lower()
            correct_answer = question.get('correct_answer', '')
            correct_answers = question.get('correct_answers', [])
            
            if question_type in ['multiple_choice', 'concept_multiple_choice', 'scenario_multiple_choice']:
                options = question.get('options', [])
                if options and correct_answer:
                    try:
                        # Handle both string and integer correct answers
                        if isinstance(correct_answer, str) and correct_answer.isdigit():
                            answer_index = int(correct_answer) - 1
                        elif isinstance(correct_answer, int):
                            answer_index = correct_answer - 1
                        else:
                            answer_index = 0
                        
                        if 0 <= answer_index < len(options):
                            back_parts.append(f"Correct Answer: {options[answer_index]}")
                    except (ValueError, IndexError):
                        back_parts.append(f"Correct Answer: {correct_answer}")
            
            elif question_type == 'true_false':
                if correct_answer is not None:
                    back_parts.append(f"Correct Answer: {'True' if correct_answer else 'False'}")
            
            elif question_type == 'fill_in_blank':
                if correct_answers:
                    if len(correct_answers) == 1:
                        back_parts.append(f"Correct Answer: {correct_answers[0]}")
                    else:
                        back_parts.append(f"Correct Answers: {', '.join(correct_answers)}")
            
            # Combine back parts
            back = '\n\n'.join(back_parts) if back_parts else 'No answer provided'
            
            return {
                'id': question.get('id'),
                'front': front,
                'back': back,
                'category': question.get('category', ''),
                'difficulty': question.get('difficulty', ''),
                'question_type': question_type,
                'tags': question.get('tags', []),
                'reference': question.get('reference', '')
            }
            
        except Exception as e:
            logger.error(f"Error converting question to flashcard: {e}")
            return None
    
    def _parse_question_json_fields(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse JSON fields in questions"""
        for question in questions:
            # Parse options
            if question.get('options'):
                if isinstance(question['options'], str):
                    try:
                        question['options'] = json.loads(question['options'])
                    except json.JSONDecodeError:
                        question['options'] = []
            
            # Parse tags
            if question.get('tags'):
                if isinstance(question['tags'], str):
                    try:
                        question['tags'] = json.loads(question['tags'])
                    except json.JSONDecodeError:
                        question['tags'] = []
            
            # Parse correct_answers
            if question.get('correct_answers'):
                if isinstance(question['correct_answers'], str):
                    try:
                        question['correct_answers'] = json.loads(question['correct_answers'])
                    except json.JSONDecodeError:
                        question['correct_answers'] = [question['correct_answers']]
        
        return questions
    
    def get_section_info(self, section: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific section"""
        if section not in self.SECTION_CATEGORIES:
            return None
        
        section_data = self.SECTION_CATEGORIES[section]
        
        # Count cards per category in this section
        category_breakdown = []
        total_cards = 0
        for category in section_data['categories']:
            count = self.question_manager.get_question_count(category=category)
            total_cards += count
            category_breakdown.append({
                'category': category,
                'card_count': count
            })
        
        return {
            'section_number': section,
            'name': section_data['name'],
            'description': section_data['description'],
            'total_cards': total_cards,
            'categories': section_data['categories'],
            'category_breakdown': category_breakdown
        }

# Global flashcard service instance
flashcard_service = FlashcardService()
