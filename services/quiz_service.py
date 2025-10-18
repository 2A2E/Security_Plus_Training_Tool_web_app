"""
Quiz Service - Handles quiz operations and database interactions
Organized by CompTIA Security+ SY0-701 Exam Domains (5 Sections)
"""
import json
import random
from typing import List, Dict, Any, Optional
from database.question_manager import question_manager
from utils.quiz_logic import quiz_manager, QuizSession
import logging

logger = logging.getLogger(__name__)

class QuizService:
    """Service class for quiz operations"""
    
    # Percentage weights for practice test distribution by section
    PRACTICE_WEIGHTS = {
        1: 24,
        2: 30,
        3: 21,
        4: 16,
        5: 9,
    }

    # Map sections to categories based on CompTIA Security+ SY0-701 Exam Domains
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
    
    def get_all_sections(self) -> List[Dict[str, Any]]:
        """Get all available sections with their details"""
        sections = []
        for section_num, section_data in self.SECTION_CATEGORIES.items():
            # Count total questions in this section
            total_questions = 0
            for category in section_data['categories']:
                count = self.question_manager.get_question_count(category=category)
                total_questions += count
            
            sections.append({
                'section_number': section_num,
                'name': section_data['name'],
                'description': section_data['description'],
                'total_questions': total_questions,
                'categories': section_data['categories']
            })
        
        return sections
    
    def create_section_quiz(self, section: int, limit: int = 10, difficulty: str = None) -> Optional[str]:
        """Create a quiz for a specific section (1-5)"""
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
                    difficulty=difficulty,
                    limit=100  # Get more questions to have a good pool
                )
                all_questions.extend(questions)
            
            if not all_questions:
                logger.warning(f"No questions found for section {section}")
                return None
            
            # Shuffle and limit to requested number
            random.shuffle(all_questions)
            all_questions = all_questions[:limit]
            
            # Parse JSON fields in questions
            all_questions = self._parse_question_json_fields(all_questions)
            
            # Create quiz session
            quiz_id = quiz_manager.create_quiz_session('section_quiz', section)
            session = quiz_manager.get_session(quiz_id)
            session.add_questions(all_questions)
            
            logger.info(f"Created section quiz for section {section} ({section_data['name']}) with {len(all_questions)} questions")
            return quiz_id
            
        except Exception as e:
            logger.error(f"Error creating section quiz: {e}")
            return None
    
    def create_category_quiz(self, category: str, limit: int = 10, difficulty: str = None) -> Optional[str]:
        """Create a quiz for a specific category"""
        try:
            # Get questions for this category
            questions = self.question_manager.get_questions(
                category=category,
                difficulty=difficulty,
                limit=limit
            )
            
            if not questions:
                logger.warning(f"No questions found for category: {category}")
                return None
            
            # Parse JSON fields in questions
            questions = self._parse_question_json_fields(questions)
            
            # Shuffle questions
            random.shuffle(questions)
            
            # Create quiz session
            quiz_id = quiz_manager.create_quiz_session('category_quiz', category)
            session = quiz_manager.get_session(quiz_id)
            session.add_questions(questions)
            
            logger.info(f"Created category quiz for '{category}' with {len(questions)} questions")
            return quiz_id
            
        except Exception as e:
            logger.error(f"Error creating category quiz: {e}")
            return None
    
    def create_random_quiz(self, limit: int = 10, difficulty: str = None) -> Optional[str]:
        """Create a random quiz from all categories"""
        try:
            # Get random questions from all categories
            questions = self.question_manager.get_questions(
                difficulty=difficulty,
                limit=limit * 3  # Get more questions to shuffle from
            )
            
            if not questions:
                logger.warning("No questions found for random quiz")
                return None
            
            # Parse JSON fields in questions
            questions = self._parse_question_json_fields(questions)
            
            # Shuffle and limit
            random.shuffle(questions)
            questions = questions[:limit]
            
            # Create quiz session
            quiz_id = quiz_manager.create_quiz_session('random_quiz')
            session = quiz_manager.get_session(quiz_id)
            session.add_questions(questions)
            
            logger.info(f"Created random quiz with {len(questions)} questions")
            return quiz_id
            
        except Exception as e:
            logger.error(f"Error creating random quiz: {e}")
            return None
    
    def create_full_practice_test(self, difficulty: str = None) -> Optional[str]:
        """Legacy helper: create a 90-question practice test using default weights."""
        return self.create_practice_test(question_count=90, sections=None, difficulty=difficulty)

    def create_practice_test(self, question_count: int = 90, sections: Optional[List[int]] = None, difficulty: str = None) -> Optional[str]:
        """Create a practice test with weighted distribution across sections.

        Args:
            question_count: Total number of questions desired (default 90)
            sections: Optional subset of sections (1-5). If None, use all sections.
            difficulty: Optional difficulty filter passed to question manager
        """
        try:
            selected_sections = sections or list(self.SECTION_CATEGORIES.keys())
            selected_sections = [s for s in selected_sections if s in self.SECTION_CATEGORIES]
            if not selected_sections:
                logger.error("No valid sections selected for practice test")
                return None

            # Compute weighted allocation using largest remainder method
            total_weight = sum(self.PRACTICE_WEIGHTS.get(s, 0) for s in selected_sections)
            if total_weight == 0:
                logger.error("Total weight is zero; check PRACTICE_WEIGHTS configuration")
                return None

            base_allocations = {}
            int_counts = {}
            for s in selected_sections:
                weight = self.PRACTICE_WEIGHTS.get(s, 0) / total_weight
                desired = weight * question_count
                base_allocations[s] = desired
                int_counts[s] = int(desired)

            remainder = question_count - sum(int_counts.values())
            if remainder > 0:
                # Distribute remaining questions to sections with largest fractional parts
                fractional_order = sorted(
                    ((s, base_allocations[s] - int_counts[s]) for s in selected_sections),
                    key=lambda x: x[1],
                    reverse=True
                )
                for i in range(remainder):
                    int_counts[fractional_order[i % len(fractional_order)][0]] += 1

            # Collect questions per section
            all_questions: List[Dict[str, Any]] = []
            leftover_pool: List[Dict[str, Any]] = []

            for section_num in selected_sections:
                take_count = int_counts.get(section_num, 0)
                if take_count <= 0:
                    continue

                section_data = self.SECTION_CATEGORIES[section_num]
                categories = section_data['categories']

                section_questions: List[Dict[str, Any]] = []
                for category in categories:
                    questions = self.question_manager.get_questions(
                        category=category,
                        difficulty=difficulty,
                        limit=200  # gather a healthy pool
                    )
                    section_questions.extend(questions)

                random.shuffle(section_questions)
                # Take what we can for this section; keep extras for leftover fill
                chosen = section_questions[:take_count]
                all_questions.extend(chosen)
                if len(section_questions) > take_count:
                    leftover_pool.extend(section_questions[take_count:])

            # If not enough questions collected, top up from leftovers
            if len(all_questions) < question_count and leftover_pool:
                random.shuffle(leftover_pool)
                needed = question_count - len(all_questions)
                all_questions.extend(leftover_pool[:needed])

            if not all_questions:
                # Fallback: pull random questions from entire pool so users can still practice
                logger.warning("No section-matched questions found; falling back to global random pool")
                try:
                    fallback_questions = self.question_manager.get_questions(
                        difficulty=difficulty,
                        limit=max(question_count * 2, 50)
                    )
                except Exception:
                    fallback_questions = []

                if not fallback_questions:
                    logger.warning("Global random pool also empty; cannot create practice test")
                    return None

                all_questions = fallback_questions

            # Parse and shuffle
            all_questions = self._parse_question_json_fields(all_questions)
            random.shuffle(all_questions)

            # Trim to requested total
            if len(all_questions) > question_count:
                all_questions = all_questions[:question_count]

            quiz_id = quiz_manager.create_quiz_session('practice_test')
            session = quiz_manager.get_session(quiz_id)
            session.add_questions(all_questions)

            logger.info(
                f"Created practice test with {len(all_questions)} questions across sections {selected_sections}"
            )
            return quiz_id

        except Exception as e:
            logger.error(f"Error creating practice test: {e}")
            return None
    
    def get_quiz_question(self, quiz_id: str, question_number: int = 1) -> Optional[Dict[str, Any]]:
        """Get a specific question from a quiz session"""
        try:
            session = quiz_manager.get_session(quiz_id)
            if not session:
                logger.error(f"Quiz session not found: {quiz_id}")
                return None
            
            # Set current question index (0-based)
            session.current_question_index = question_number - 1
            
            question = session.get_current_question()
            if question:
                # Add quiz metadata
                question['quiz_id'] = quiz_id
                question['question_number'] = question_number
                question['total_questions'] = session.total_questions
                question['progress_percentage'] = (question_number / session.total_questions) * 100
                
            return question
            
        except Exception as e:
            logger.error(f"Error getting quiz question: {e}")
            return None
    
    def submit_quiz_answer(self, quiz_id: str, answer: str) -> Optional[Dict[str, Any]]:
        """Submit an answer for the current question"""
        try:
            session = quiz_manager.get_session(quiz_id)
            if not session:
                logger.error(f"Quiz session not found: {quiz_id}")
                return None
            
            current_question = session.get_current_question()
            if not current_question:
                logger.error(f"No current question in session: {quiz_id}")
                return None
            
            # Submit the answer
            result = session.submit_answer(answer, str(current_question.get('id', '')))
            if 'error' in result:
                logger.error(f"Submit error for quiz {quiz_id}: {result['error']}")
                return None
            
            # Add additional metadata
            result['question_number'] = session.current_question_index + 1
            result['total_questions'] = session.total_questions
            result['has_next_question'] = session.current_question_index + 1 < session.total_questions
            result['quiz_completed'] = session.current_question_index + 1 >= session.total_questions
            
            return result
            
        except Exception as e:
            logger.error(f"Error submitting quiz answer: {e}")
            return None
    
    def get_quiz_results(self, quiz_id: str) -> Optional[Dict[str, Any]]:
        """Get final quiz results"""
        try:
            session = quiz_manager.get_session(quiz_id)
            if not session:
                logger.error(f"Quiz session not found: {quiz_id}")
                return None
            
            return session.get_quiz_results()
            
        except Exception as e:
            logger.error(f"Error getting quiz results: {e}")
            return None
    
    def get_wrong_questions_review(self, quiz_id: str) -> List[Dict[str, Any]]:
        """Get questions that were answered incorrectly for review"""
        try:
            session = quiz_manager.get_session(quiz_id)
            if not session:
                logger.error(f"Quiz session not found: {quiz_id}")
                return []
            
            return session.get_wrong_questions_for_review()
            
        except Exception as e:
            logger.error(f"Error getting wrong questions review: {e}")
            return []
    
    def cleanup_quiz_session(self, quiz_id: str):
        """Clean up a quiz session"""
        quiz_manager.cleanup_session(quiz_id)
    
    def get_section_info(self, section: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific section"""
        if section not in self.SECTION_CATEGORIES:
            return None
        
        section_data = self.SECTION_CATEGORIES[section]
        
        # Count questions per category in this section
        category_breakdown = []
        total_questions = 0
        for category in section_data['categories']:
            count = self.question_manager.get_question_count(category=category)
            total_questions += count
            category_breakdown.append({
                'category': category,
                'question_count': count
            })
        
        return {
            'section_number': section,
            'name': section_data['name'],
            'description': section_data['description'],
            'total_questions': total_questions,
            'categories': section_data['categories'],
            'category_breakdown': category_breakdown
        }
    
    def get_available_categories(self) -> List[str]:
        """Get all available categories across all sections"""
        return self.question_manager.get_question_categories()
    
    def get_quiz_statistics(self) -> Dict[str, Any]:
        """Get overall quiz statistics"""
        total_questions = self.question_manager.get_question_count()
        total_categories = len(self.question_manager.get_question_categories())
        total_tags = len(self.question_manager.get_question_tags())
        
        # Get section breakdown
        sections_info = []
        for section_num in range(1, 6):
            section_info = self.get_section_info(section_num)
            if section_info:
                sections_info.append(section_info)
        
        return {
            'total_questions': total_questions,
            'total_categories': total_categories,
            'total_tags': total_tags,
            'total_sections': 5,
            'sections': sections_info
        }
    
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

# Global quiz service instance
quiz_service = QuizService()
