"""
Session Management for Word Cycling
Implements Anki-like queue system:
- Maintains a queue of words for today's session
- Prevents consecutive duplicate words
- Cycles words until all are mastered
"""

import random
from datetime import date
from database import get_words_for_today, get_words_for_child

class WordSession:
    """Manages word queue for a single practice session"""
    
    def __init__(self, num_words=None, child_id=None):
        """
        Initialize session with words from today
        
        Args:
            num_words: Limit words to practice (None = all available)
            child_id: Child ID for filtering words (None = use all words)
        """
        self.num_words = num_words
        self.child_id = child_id
        self.available_words = []  # Words yet to be mastered today
        self.last_word_id = None  # Track last shown word to prevent consecutive duplicates
        self.mastered_words = set()  # Words completed in this session
        self.session_started = False
        self.initial_word_count = 0  # Track actual number of words loaded
        
        self._load_words()
    
    def _load_words(self):
        """Load available words for today from database"""
        # Use child-specific words if child_id is provided
        if self.child_id:
            all_words = get_words_for_child(self.child_id)
        else:
            all_words = get_words_for_today()
        
        # Limit to num_words if specified
        if self.num_words:
            all_words = all_words[:self.num_words]
        
        # Store word IDs for queue
        self.available_words = [word['id'] for word in all_words]
        
        self.initial_word_count = len(self.available_words)
        
        # Shuffle for variety
        random.shuffle(self.available_words)
        self.session_started = True
    
    def get_next_word_id(self):
        """
        Get next word ID ensuring:
        1. No consecutive duplicates
        2. Cycles through all words before repeating
        
        Returns:
            word_id (int) or None if session complete
        """
        if not self.available_words:
            return None
        
        # If only one word left
        if len(self.available_words) == 1:
            word_id = self.available_words[0]
            # Allow same word if it's the only one left
            return word_id
        
        # Multiple words available - ensure no consecutive duplicates
        available_without_last = [
            w for w in self.available_words 
            if w != self.last_word_id
        ]
        
        if not available_without_last:
            # Shouldn't happen, but fallback to any word
            word_id = self.available_words[0]
        else:
            # Pick random from available (excluding last)
            word_id = random.choice(available_without_last)
        
        self.last_word_id = word_id
        return word_id
    
    def mark_word_mastered(self, word_id):
        """
        Mark word as mastered (correct answer)
        Word is removed from queue completely
        
        Args:
            word_id: ID of word that was spelled correctly
        """
        if word_id in self.available_words:
            # Remove from queue completely
            self.available_words.remove(word_id)
            # Track as mastered in this session
            self.mastered_words.add(word_id)
    
    def mark_word_incorrect(self, word_id):
        """
        Mark word as incorrect (wrong answer)
        Word stays in queue at current position for retry
        
        Args:
            word_id: ID of word that was spelled incorrectly
        """
        # Word stays in available_words, no change needed
        pass
    
    def is_session_complete(self):
        """
        Check if session is complete
        Session ends when all words have been mastered at least once
        
        Returns:
            bool: True if all words mastered, False otherwise
        """
        if not self.available_words:
            return True
        
        # Session complete when all words mastered at least once
        # But continue cycling while there are words in queue
        return False
    
    def get_session_stats(self):
        """
        Get current session statistics
        
        Returns:
            dict: {
                'total_words': total words in session,
                'mastered': number of unique words mastered,
                'remaining': words not yet mastered,
                'queue_size': current queue size
            }
        """
        return {
            'total_words': self.initial_word_count,
            'mastered': len(self.mastered_words),
            'remaining': len(self.available_words) - len([w for w in self.available_words if w in self.mastered_words]),
            'queue_size': len(self.available_words)
        }
