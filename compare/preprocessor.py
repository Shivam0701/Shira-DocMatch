"""
Text preprocessing for comparison.
"""
import re
from typing import List, Tuple


class Preprocessor:
    """Handles text preprocessing before comparison."""
    
    def __init__(self, lowercase: bool = True):
        """
        Initialize preprocessor.
        
        Args:
            lowercase: Whether to convert text to lowercase
        """
        self.lowercase = lowercase
    
    def preprocess(self, text: str) -> str:
        """
        Preprocess text by normalizing whitespace and removing control characters.
        
        Args:
            text: Input text
            
        Returns:
            Preprocessed text
        """
        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Normalize whitespace (replace multiple spaces with single, preserve newlines)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r' +\n', '\n', text)
        text = re.sub(r'\n +', '\n', text)
        
        # Optional lowercase
        if self.lowercase:
            text = text.lower()
        
        return text
    
    def split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        import nltk
        try:
            sentences = nltk.sent_tokenize(text)
        except LookupError:
            # Download punkt if not available
            nltk.download('punkt', quiet=True)
            sentences = nltk.sent_tokenize(text)
        return [s.strip() for s in sentences if s.strip()]
    
    def get_sentence_offsets(self, text: str, sentences: List[str]) -> List[Tuple[int, int]]:
        """
        Get character offsets for each sentence.
        
        Args:
            text: Original text
            sentences: List of sentences
            
        Returns:
            List of (start, end) tuples
        """
        offsets = []
        current_pos = 0
        
        for sentence in sentences:
            # Find sentence in text starting from current position
            start = text.find(sentence, current_pos)
            if start == -1:
                # If not found, approximate
                start = current_pos
            end = start + len(sentence)
            offsets.append((start, end))
            current_pos = end
        
        return offsets

