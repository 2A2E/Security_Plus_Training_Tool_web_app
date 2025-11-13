"""
Flashcard manager for Supabase database operations
Handles flashcards stored in the flashcards table with term and definition columns
"""
from datetime import datetime
from typing import List, Dict, Optional, Any
import logging
import json

logger = logging.getLogger(__name__)

class FlashcardManager:
    """Manager for flashcard-related Supabase database operations"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.flashcards_table = db_manager.get_table('flashcards')
        logger.info("FlashcardManager initialized with Supabase")
    
    def get_flashcards(self, 
                      deck: str = None, 
                      tags: List[str] = None,
                      difficulty: str = None,
                      limit: int = 50,
                      skip: int = 0) -> List[Dict[str, Any]]:
        """
        Get flashcards with optional filtering
        
        Args:
            deck: Filter by deck name
            tags: Filter by tags (any match)
            difficulty: Filter by difficulty level
            limit: Maximum number of flashcards to return
            skip: Number of flashcards to skip (for pagination)
            
        Returns:
            List of flashcard dictionaries
        """
        try:
            logger.info(f"get_flashcards called with deck='{deck}', tags={tags}, difficulty={difficulty}, limit={limit}, skip={skip}")
            query = self.flashcards_table.select('*')
            
            # Apply filters
            if deck:
                logger.info(f"Filtering by deck: '{deck}'")
                query = query.eq('deck', deck)
            if difficulty:
                query = query.eq('difficulty', difficulty)
            
            # Apply pagination
            query = query.range(skip, skip + limit - 1)
            
            # Order by id (or created_at if available)
            try:
                query = query.order('id', desc=False)
            except:
                # If id doesn't exist or ordering fails, try without order
                pass
            
            result = query.execute()
            logger.info(f"Query returned {len(result.data) if result.data else 0} flashcards")
            
            flashcards = []
            if result.data:
                for flashcard in result.data:
                    # Parse JSON fields if they exist
                    if flashcard.get('tags'):
                        if isinstance(flashcard['tags'], str):
                            try:
                                flashcard['tags'] = json.loads(flashcard['tags'])
                            except json.JSONDecodeError:
                                # If tags is a string but not JSON, treat as comma-separated
                                flashcard['tags'] = [tag.strip() for tag in flashcard['tags'].split(',') if tag.strip()]
                        elif not isinstance(flashcard['tags'], list):
                            flashcard['tags'] = []
                    
                    # Ensure tags is a list
                    if not isinstance(flashcard.get('tags'), list):
                        flashcard['tags'] = []
                    
                    # Convert to standard flashcard format
                    formatted_flashcard = {
                        'id': flashcard.get('id'),
                        'term': flashcard.get('term', ''),
                        'definition': flashcard.get('definition', ''),
                        'front': flashcard.get('term', ''),
                        'back': flashcard.get('definition', ''),
                        'deck': flashcard.get('deck', ''),
                        'tags': flashcard.get('tags', []),
                        'source': flashcard.get('source', ''),
                        'difficulty': flashcard.get('difficulty', '')
                    }
                    
                    flashcards.append(formatted_flashcard)
            
            # Filter by tags if specified (PostgreSQL JSON operations)
            if tags and flashcards:
                filtered_flashcards = []
                for flashcard in flashcards:
                    flashcard_tags = flashcard.get('tags', [])
                    if isinstance(flashcard_tags, list):
                        if any(tag in flashcard_tags for tag in tags):
                            filtered_flashcards.append(flashcard)
                    elif isinstance(flashcard_tags, str):
                        if any(tag in flashcard_tags for tag in tags):
                            filtered_flashcards.append(flashcard)
                flashcards = filtered_flashcards
            
            return flashcards
            
        except Exception as e:
            logger.error(f"Error getting flashcards: {e}")
            return []
    
    def get_flashcard(self, flashcard_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a flashcard by ID
        
        Args:
            flashcard_id: The ID of the flashcard
            
        Returns:
            Dict containing flashcard data or None if not found
        """
        try:
            result = self.flashcards_table.select('*').eq('id', flashcard_id).execute()
            
            if result.data and len(result.data) > 0:
                flashcard = result.data[0]
                # Parse JSON fields
                if flashcard.get('tags'):
                    if isinstance(flashcard['tags'], str):
                        try:
                            flashcard['tags'] = json.loads(flashcard['tags'])
                        except json.JSONDecodeError:
                            flashcard['tags'] = [tag.strip() for tag in flashcard['tags'].split(',') if tag.strip()]
                    elif not isinstance(flashcard['tags'], list):
                        flashcard['tags'] = []
                
                # Convert to standard format
                return {
                    'id': flashcard.get('id'),
                    'term': flashcard.get('term', ''),
                    'definition': flashcard.get('definition', ''),
                    'front': flashcard.get('term', ''),
                    'back': flashcard.get('definition', ''),
                    'deck': flashcard.get('deck', ''),
                    'tags': flashcard.get('tags', []),
                    'source': flashcard.get('source', ''),
                    'difficulty': flashcard.get('difficulty', '')
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting flashcard {flashcard_id}: {e}")
            return None
    
    def get_flashcard_count(self, deck: str = None, tags: List[str] = None, difficulty: str = None) -> int:
        """Get total count of flashcards with optional filtering"""
        try:
            logger.info(f"get_flashcard_count called with deck='{deck}', tags={tags}, difficulty={difficulty}")
            query = self.flashcards_table.select('id', count='exact')
            
            if deck:
                logger.info(f"Counting flashcards with deck='{deck}'")
                query = query.eq('deck', deck)
            if difficulty:
                query = query.eq('difficulty', difficulty)
            
            result = query.execute()
            count = result.count if result.count is not None else 0
            logger.info(f"Count query returned: {count} flashcards")
            
            # If tags filter is needed, we might need to filter in memory
            # For now, return the count (tags filtering can be done separately)
            return count
            
        except Exception as e:
            logger.error(f"Error getting flashcard count: {e}")
            return 0
    
    def get_flashcard_decks(self) -> List[str]:
        """Get all unique deck values"""
        try:
            result = self.flashcards_table.select('deck').execute()
            
            if result.data:
                decks = list(set([f['deck'] for f in result.data if f.get('deck')]))
                return sorted(decks)
            return []
            
        except Exception as e:
            logger.error(f"Error getting flashcard decks: {e}")
            return []
    
    def get_flashcard_tags(self) -> List[str]:
        """Get all unique tag values from flashcards"""
        try:
            result = self.flashcards_table.select('tags').execute()
            
            if result.data:
                all_tags = set()
                for flashcard in result.data:
                    if flashcard.get('tags'):
                        try:
                            if isinstance(flashcard['tags'], str):
                                tags = json.loads(flashcard['tags'])
                            else:
                                tags = flashcard['tags']
                            if isinstance(tags, list):
                                all_tags.update(tags)
                        except (json.JSONDecodeError, TypeError):
                            # If tags is a string but not JSON, treat as comma-separated
                            if isinstance(flashcard['tags'], str):
                                all_tags.update([tag.strip() for tag in flashcard['tags'].split(',') if tag.strip()])
                return sorted(list(all_tags))
            return []
            
        except Exception as e:
            logger.error(f"Error getting flashcard tags: {e}")
            return []

# Global flashcard manager instance
try:
    from .connection import db_manager
    flashcard_manager = FlashcardManager(db_manager)
except ImportError as e:
    logger.error(f"Could not import db_manager: {e}")
    flashcard_manager = None

