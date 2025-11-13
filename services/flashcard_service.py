"""
Flashcard Service - Handles flashcard operations and session management
Organized by CompTIA Security+ SY0-701 Exam Domains (5 Sections)
"""
import random
import time
from typing import List, Dict, Any, Optional
from database.flashcard_manager import flashcard_manager
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
            ],
            'deck_names': ['Part 1', 'part1', 'Part1', 'Section 1', 'General Security Concepts', 'Section1'],
            'tags': ['General Security Concepts', 'Zero Trust', 'Cryptography', 'PKI', 'IAM', 'Physical Security']
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
            ],
            'deck_names': ['Part 2', 'part2', 'Part2', 'Section 2', 'Threats, Vulnerabilities, and Mitigations', 'Section2'],
            'tags': ['Threats', 'Vulnerabilities', 'Attacks', 'Malware', 'Exploits']
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
            ],
            'deck_names': ['Part 3', 'part3', 'Part3', 'Section 3', 'Security Architecture', 'Section3'],
            'tags': ['Security Architecture', 'Network Design', 'Cloud', 'Virtualization']
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
            ],
            'deck_names': ['Part 4', 'part4', 'Part4', 'Section 4', 'Security Operations', 'Section4'],
            'tags': ['Security Operations', 'Incident Response', 'Forensics', 'SIEM']
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
            ],
            'deck_names': ['Part 5', 'part5', 'Part5', 'Section 5', 'Security Program Management and Oversight', 'Section5'],
            'tags': ['Governance', 'Risk Management', 'Compliance', 'Policies', 'Standards']
        }
    }
    
    def __init__(self):
        self.flashcard_manager = flashcard_manager
        self.sessions = {}  # In-memory session storage
        self._cleanup_expired_sessions()
    
    def get_all_sections(self) -> List[Dict[str, Any]]:
        """Get all available sections with their flashcard counts"""
        if not self.flashcard_manager:
            logger.error("Flashcard manager not initialized")
            return []
        
        # First, get all available decks to see what we're working with
        available_decks = self.flashcard_manager.get_flashcard_decks()
        logger.info(f"Available decks in database: {available_decks}")
        
        # Get total count of all flashcards
        total_all_flashcards = self.flashcard_manager.get_flashcard_count()
        logger.info(f"Total flashcards in database: {total_all_flashcards}")
        
        sections = []
        for section_num, section_data in self.SECTION_CATEGORIES.items():
            # Count flashcards for this section by trying to match deck names
            total_cards = 0
            deck_names = section_data.get('deck_names', [])
            tags = section_data.get('tags', [])
            
            logger.info(f"Section {section_num}: Trying deck names {deck_names}")
            
            # Try to match by deck name first
            for deck_name in deck_names:
                count = self.flashcard_manager.get_flashcard_count(deck=deck_name)
                if count > 0:
                    total_cards = count
                    logger.info(f"Section {section_num}: Found {total_cards} flashcards for deck '{deck_name}'")
                    break
            
            # If no deck match found, try to count by tags
            if total_cards == 0 and tags:
                # Get all flashcards and filter by tags
                all_flashcards = self.flashcard_manager.get_flashcards(limit=10000)
                matched_flashcards = []
                for flashcard in all_flashcards:
                    flashcard_tags = flashcard.get('tags', [])
                    if isinstance(flashcard_tags, list):
                        if any(tag in flashcard_tags for tag in tags):
                            matched_flashcards.append(flashcard)
                    elif isinstance(flashcard_tags, str):
                        if any(tag in flashcard_tags for tag in tags):
                            matched_flashcards.append(flashcard)
                total_cards = len(matched_flashcards)
                if total_cards > 0:
                    logger.info(f"Section {section_num}: Found {total_cards} flashcards matching tags")
            
            # If still no match and we have flashcards, split them evenly across sections
            # This handles the case where deck names don't match but we still want to show counts
            if total_cards == 0 and total_all_flashcards > 0:
                # Check if any section already matched - if so, don't split
                # Otherwise, split evenly
                total_cards = total_all_flashcards // len(self.SECTION_CATEGORIES)
                logger.info(f"Section {section_num}: No deck match found, splitting evenly: {total_cards} cards")
            
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
            
            if not self.flashcard_manager:
                logger.error("Flashcard manager not initialized")
                return None
            
            section_data = self.SECTION_CATEGORIES[section]
            deck_names = section_data.get('deck_names', [])
            tags = section_data.get('tags', [])
            
            # Try to get flashcards by deck name first
            flashcards = []
            for deck_name in deck_names:
                deck_flashcards = self.flashcard_manager.get_flashcards(deck=deck_name, limit=10000)
                if deck_flashcards:
                    flashcards = deck_flashcards
                    logger.info(f"Found {len(flashcards)} flashcards for deck: {deck_name}")
                    break
            
            # If no deck match found, try to filter by tags
            if not flashcards and tags:
                all_flashcards = self.flashcard_manager.get_flashcards(limit=10000)
                for flashcard in all_flashcards:
                    flashcard_tags = flashcard.get('tags', [])
                    if isinstance(flashcard_tags, list):
                        if any(tag in flashcard_tags for tag in tags):
                            flashcards.append(flashcard)
                    elif isinstance(flashcard_tags, str):
                        if any(tag in flashcard_tags for tag in tags):
                            flashcards.append(flashcard)
                logger.info(f"Found {len(flashcards)} flashcards matching tags: {tags}")
            
            # If still no flashcards found, split all flashcards by section
            if not flashcards:
                all_flashcards = self.flashcard_manager.get_flashcards(limit=10000)
                total_all = len(all_flashcards)
                if total_all > 0:
                    # Split flashcards evenly across sections (5 sections)
                    cards_per_section = total_all // len(self.SECTION_CATEGORIES)
                    start_idx = (section - 1) * cards_per_section
                    end_idx = start_idx + cards_per_section
                    # Last section gets any remainder
                    if section == len(self.SECTION_CATEGORIES):
                        end_idx = total_all
                    flashcards = all_flashcards[start_idx:end_idx]
                    logger.info(f"Section {section}: Split flashcards - showing {len(flashcards)} cards (indices {start_idx}-{end_idx} of {total_all})")
                else:
                    logger.warning(f"No flashcards found for section {section}")
                    return None
            
            if not flashcards:
                logger.warning(f"No flashcards found for section {section}")
                return None
            
            # Format flashcards to ensure they have front/back fields
            formatted_flashcards = []
            for flashcard in flashcards:
                formatted_flashcard = {
                    'id': flashcard.get('id'),
                    'front': flashcard.get('term', flashcard.get('front', '')),
                    'back': flashcard.get('definition', flashcard.get('back', '')),
                    'term': flashcard.get('term', ''),
                    'definition': flashcard.get('definition', ''),
                    'category': flashcard.get('deck', flashcard.get('category', '')),
                    'difficulty': flashcard.get('difficulty', ''),
                    'tags': flashcard.get('tags', []),
                    'source': flashcard.get('source', ''),
                    'deck': flashcard.get('deck', '')
                }
                
                # Skip flashcards without term/definition
                if not formatted_flashcard['front'] or not formatted_flashcard['back']:
                    continue
                
                formatted_flashcards.append(formatted_flashcard)
            
            if not formatted_flashcards:
                logger.warning(f"No valid flashcards created for section {section}")
                return None
            
            # Shuffle and optionally limit to requested number
            random.shuffle(formatted_flashcards)
            if isinstance(limit, int) and limit > 0:
                formatted_flashcards = formatted_flashcards[:limit]
            
            # Create session
            session_id = f"flashcard_{section}_{int(time.time())}"
            session = FlashcardSession(session_id, section, formatted_flashcards)
            self.sessions[session_id] = session
            
            logger.info(f"Created flashcard session for section {section} ({section_data['name']}) with {len(formatted_flashcards)} cards")
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
    
    
    def get_section_info(self, section: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific section"""
        if section not in self.SECTION_CATEGORIES:
            return None
        
        if not self.flashcard_manager:
            logger.error("Flashcard manager not initialized")
            return None
        
        section_data = self.SECTION_CATEGORIES[section]
        deck_names = section_data.get('deck_names', [])
        tags = section_data.get('tags', [])
        
        # Count cards per category/deck in this section
        category_breakdown = []
        total_cards = 0
        
        # Try to count by deck names
        for deck_name in deck_names:
            count = self.flashcard_manager.get_flashcard_count(deck=deck_name)
            if count > 0:
                total_cards += count
                category_breakdown.append({
                    'category': deck_name,
                    'card_count': count
                })
        
        # If no deck match, try to count by tags
        if total_cards == 0 and tags:
            all_flashcards = self.flashcard_manager.get_flashcards(limit=10000)
            for tag in tags:
                matching_flashcards = [f for f in all_flashcards 
                                     if tag in f.get('tags', [])]
                count = len(matching_flashcards)
                if count > 0:
                    total_cards += count
                    category_breakdown.append({
                        'category': tag,
                        'card_count': count
                    })
        
        # If still no cards, count all flashcards
        if total_cards == 0:
            total_cards = self.flashcard_manager.get_flashcard_count()
            category_breakdown.append({
                'category': 'All Flashcards',
                'card_count': total_cards
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
