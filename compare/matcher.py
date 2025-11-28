"""
Document comparison and matching logic.
"""
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
from difflib import SequenceMatcher
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from compare.preprocessor import Preprocessor


@dataclass
class Match:
    """Represents a match between two documents."""
    left_text: str
    left_start: int
    left_end: int
    right_text: str
    right_start: int
    right_end: int
    match_type: str  # 'exact', 'fuzzy', 'semantic'
    score: float


class Matcher:
    """Handles document comparison with multiple matching strategies."""
    
    def __init__(self, config: Dict):
        """
        Initialize matcher.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.preprocessor = Preprocessor(lowercase=config.get('LOWERCASE', True))
        self.fuzzy_min_ratio = config.get('FUZZY_MIN_RATIO', 0.85)
        self.semantic_threshold = config.get('SEMANTIC_THRESHOLD', 0.75)
        self.embedding_model_name = config.get('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        self.enable_semantic = config.get('ENABLE_SEMANTIC', True)
        
        # Load embedding model if semantic matching is enabled
        self.embedding_model = None
        if self.enable_semantic:
            try:
                self.embedding_model = SentenceTransformer(self.embedding_model_name)
            except Exception as e:
                print(f"Warning: Could not load embedding model: {e}. Semantic matching disabled.")
                self.enable_semantic = False
    
    def compare_documents(self, left_text: str, right_text: str) -> Tuple[float, List[Dict], Dict]:
        """
        Compare two documents and return matches.
        
        Args:
            left_text: Text from first document
            right_text: Text from second document
            
        Returns:
            Tuple of (overall_score, matches, stats)
        """
        # Preprocess texts
        left_processed = self.preprocessor.preprocess(left_text)
        right_processed = self.preprocessor.preprocess(right_text)
        
        # Find matches using different strategies
        matches: List[Match] = []
        
        # 1. Exact substring matches
        exact_matches = self._find_exact_matches(left_text, right_text, left_processed, right_processed)
        matches.extend(exact_matches)
        
        # 2. Fuzzy matches
        fuzzy_matches = self._find_fuzzy_matches(left_text, right_text, left_processed, right_processed)
        matches.extend(fuzzy_matches)
        
        # 3. Semantic matches
        if self.enable_semantic and self.embedding_model:
            semantic_matches = self._find_semantic_matches(left_text, right_text, left_processed, right_processed)
            matches.extend(semantic_matches)
        
        # Deduplicate and rank matches
        unique_matches = self._deduplicate_matches(matches)
        unique_matches.sort(key=lambda m: m.score, reverse=True)
        
        # Calculate overall similarity
        overall_score = self._calculate_overall_similarity(left_processed, right_processed, unique_matches)
        
        # Convert to dictionaries and limit to top N
        top_n = self.config.get('TOP_N_MATCHES', 20)
        matches_dict = self._matches_to_dicts(unique_matches[:top_n])
        
        # Calculate statistics
        stats = {
            'left_word_count': len(left_text.split()),
            'right_word_count': len(right_text.split()),
            'total_matches': len(unique_matches),
        }
        
        return overall_score, matches_dict, stats
    
    def _find_exact_matches(self, left_orig: str, right_orig: str, 
                           left_proc: str, right_proc: str) -> List[Match]:
        """Find exact substring matches."""
        matches = []
        words_left = left_proc.split()
        
        # Look for common phrases (min 3 words)
        min_words = 3
        
        for i in range(len(words_left) - min_words + 1):
            phrase_proc = ' '.join(words_left[i:i + min_words])
            if phrase_proc in right_proc:
                # Get the corresponding phrase from original text
                orig_words_left = left_orig.split()
                if i + min_words > len(orig_words_left):
                    continue
                    
                phrase_orig = ' '.join(orig_words_left[i:i + min_words])
                
                # Find positions in original text
                # Search case-insensitively in original
                left_start = left_orig.lower().find(phrase_orig.lower())
                if left_start == -1:
                    # If not found, skip this match
                    continue
                left_end = left_start + len(phrase_orig)
                
                # Find in right document - need to find matching words
                orig_words_right = right_orig.split()
                right_proc_list = right_proc.split()
                
                # Find the matching index in right proc first
                try:
                    right_idx = right_proc_list.index(words_left[i])
                except ValueError:
                    continue
                
                # Check if phrase matches at this index
                if right_idx + min_words > len(right_proc_list):
                    continue
                if ' '.join(right_proc_list[right_idx:right_idx + min_words]) != phrase_proc:
                    continue
                    
                # Now find in original right
                if right_idx + min_words > len(orig_words_right):
                    continue
                phrase_orig_right = ' '.join(orig_words_right[right_idx:right_idx + min_words])
                
                right_start = right_orig.lower().find(phrase_orig_right.lower())
                if right_start == -1:
                    continue
                right_end = right_start + len(phrase_orig_right)
                
                matches.append(Match(
                    left_text=phrase_orig[:100] + ('...' if len(phrase_orig) > 100 else ''),
                    left_start=left_start,
                    left_end=left_end,
                    right_text=phrase_orig_right[:100] + ('...' if len(phrase_orig_right) > 100 else ''),
                    right_start=right_start,
                    right_end=right_end,
                    match_type='exact',
                    score=1.0
                ))
        
        return matches
    
    def _find_fuzzy_matches(self, left_orig: str, right_orig: str,
                           left_proc: str, right_proc: str) -> List[Match]:
        """Find fuzzy matches using RapidFuzz."""
        matches = []
        
        # Split into sentences for better matching - use processed text
        left_sentences_proc = self.preprocessor.split_sentences(left_proc)
        right_sentences_proc = self.preprocessor.split_sentences(right_proc)
        
        # Get offsets from original text using original sentence splits
        left_sentences_orig = self.preprocessor.split_sentences(left_orig)
        right_sentences_orig = self.preprocessor.split_sentences(right_orig)
        
        left_offsets = self.preprocessor.get_sentence_offsets(left_orig, left_sentences_orig)
        right_offsets = self.preprocessor.get_sentence_offsets(right_orig, right_sentences_orig)
        
        # Match indices from processed sentences to original
        # Note: sentence counts should match after preprocessing
        for i, left_sent in enumerate(left_sentences_proc):
            # Find corresponding index in original
            orig_idx = min(i, len(left_sentences_orig) - 1) if left_sentences_orig else 0
            
            for j, right_sent in enumerate(right_sentences_proc):
                # Skip if either sentence is too short
                if len(left_sent) < 10 or len(right_sent) < 10:
                    continue
                
                # Calculate similarity
                ratio = fuzz.ratio(left_sent, right_sent) / 100.0
                
                if ratio >= self.fuzzy_min_ratio:
                    # Find corresponding index in original for right
                    orig_idx_right = min(j, len(right_sentences_orig) - 1) if right_sentences_orig else 0
                    
                    left_start, left_end = left_offsets[orig_idx] if left_offsets else (0, len(left_orig))
                    right_start, right_end = right_offsets[orig_idx_right] if right_offsets else (0, len(right_orig))
                    
                    matches.append(Match(
                        left_text=left_sent[:100] + ('...' if len(left_sent) > 100 else ''),
                        left_start=left_start,
                        left_end=left_end,
                        right_text=right_sent[:100] + ('...' if len(right_sent) > 100 else ''),
                        right_start=right_start,
                        right_end=right_end,
                        match_type='fuzzy',
                        score=ratio
                    ))
        
        return matches
    
    def _find_semantic_matches(self, left_orig: str, right_orig: str,
                              left_proc: str, right_proc: str) -> List[Match]:
        """Find semantic matches using embeddings."""
        if not self.embedding_model:
            return []
        
        matches = []
        
        # Split into sentences - use processed text for matching
        left_sentences_proc = self.preprocessor.split_sentences(left_proc)
        right_sentences_proc = self.preprocessor.split_sentences(right_proc)
        
        # Get offsets from original text
        left_sentences_orig = self.preprocessor.split_sentences(left_orig)
        right_sentences_orig = self.preprocessor.split_sentences(right_orig)
        
        left_offsets = self.preprocessor.get_sentence_offsets(left_orig, left_sentences_orig)
        right_offsets = self.preprocessor.get_sentence_offsets(right_orig, right_sentences_orig)
        
        # Get embeddings in batches
        try:
            left_embeddings = self.embedding_model.encode(left_sentences_proc, show_progress_bar=False)
            right_embeddings = self.embedding_model.encode(right_sentences_proc, show_progress_bar=False)
            
            # Compute similarity matrix
            similarity_matrix = cosine_similarity(left_embeddings, right_embeddings)
            
            # Find pairs above threshold
            for i in range(len(left_sentences_proc)):
                # Find corresponding index in original
                orig_idx = min(i, len(left_sentences_orig) - 1) if left_sentences_orig else 0
                
                for j in range(len(right_sentences_proc)):
                    similarity = float(similarity_matrix[i][j])
                    
                    if similarity >= self.semantic_threshold:
                        # Find corresponding index in original for right
                        orig_idx_right = min(j, len(right_sentences_orig) - 1) if right_sentences_orig else 0
                        
                        left_start, left_end = left_offsets[orig_idx] if left_offsets else (0, len(left_orig))
                        right_start, right_end = right_offsets[orig_idx_right] if right_offsets else (0, len(right_orig))
                        
                        matches.append(Match(
                            left_text=left_sentences_proc[i][:100] + ('...' if len(left_sentences_proc[i]) > 100 else ''),
                            left_start=left_start,
                            left_end=left_end,
                            right_text=right_sentences_proc[j][:100] + ('...' if len(right_sentences_proc[j]) > 100 else ''),
                            right_start=right_start,
                            right_end=right_end,
                            match_type='semantic',
                            score=similarity
                        ))
        except Exception as e:
            print(f"Error in semantic matching: {e}")
            return []
        
        return matches
    
    def _deduplicate_matches(self, matches: List[Match]) -> List[Match]:
        """Remove duplicate matches."""
        seen: Set[Tuple[int, int]] = set()
        unique_matches = []
        
        for match in sorted(matches, key=lambda m: m.score, reverse=True):
            # Use position ranges as key for deduplication
            key = (match.left_start, match.left_end, match.right_start, match.right_end)
            if key not in seen:
                seen.add(key)
                unique_matches.append(match)
        
        return unique_matches
    
    def _calculate_overall_similarity(self, left_proc: str, right_proc: str, 
                                     matches: List[Match]) -> float:
        """Calculate overall document similarity score."""
        if not matches:
            return 0.0
        
        # Use weighted average of match scores
        total_score = sum(m.score for m in matches)
        avg_match_score = total_score / len(matches)
        
        # Also consider coverage
        left_words = set(left_proc.split())
        right_words = set(right_proc.split())
        
        # Jaccard similarity as baseline
        intersection = left_words & right_words
        union = left_words | right_words
        jaccard = len(intersection) / len(union) if union else 0.0
        
        # Combine scores
        overall = (avg_match_score * 0.7 + jaccard * 0.3)
        
        return round(overall, 4)
    
    def _matches_to_dicts(self, matches: List[Match]) -> List[Dict]:
        """Convert Match objects to dictionaries."""
        return [
            {
                'left_text': m.left_text,
                'left_start': m.left_start,
                'left_end': m.left_end,
                'right_text': m.right_text,
                'right_start': m.right_start,
                'right_end': m.right_end,
                'type': m.match_type,
                'score': round(m.score, 4)
            }
            for m in matches
        ]

