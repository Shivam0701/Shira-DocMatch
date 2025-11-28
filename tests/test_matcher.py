"""
Tests for document matching logic.
"""
import pytest
from compare.matcher import Matcher
from compare.preprocessor import Preprocessor


@pytest.fixture
def matcher_config():
    """Configuration for matcher."""
    return {
        'FUZZY_MIN_RATIO': 0.85,
        'SEMANTIC_THRESHOLD': 0.75,
        'EMBEDDING_MODEL': 'all-MiniLM-L6-v2',
        'TOP_N_MATCHES': 20,
        'ENABLE_SEMANTIC': False,  # Disable for faster tests
        'LOWERCASE': True,
    }


@pytest.fixture
def sample_text_1():
    """First sample text."""
    return """This is a test document for comparison.
It contains several paragraphs and sentences.
We will use this to test the matching algorithms.
The quick brown fox jumps over the lazy dog."""


@pytest.fixture
def sample_text_2():
    """Second sample text."""
    return """This is another document for comparison.
It contains similar content and phrases.
We use this to test matching algorithms.
The quick brown fox jumped over the lazy dog."""


@pytest.fixture
def completely_different_text():
    """Text with no similarities."""
    return """This is completely different content.
It has nothing in common with the other texts.
No shared phrases or concepts exist here."""


class TestMatcher:
    """Test cases for document matcher."""
    
    def test_compare_similar_documents(self, matcher_config, sample_text_1, sample_text_2):
        """Test comparison of similar documents."""
        matcher = Matcher(matcher_config)
        overall_score, matches, stats = matcher.compare_documents(sample_text_1, sample_text_2)
        
        assert overall_score > 0
        assert isinstance(matches, list)
        assert len(matches) > 0
        assert 'left_word_count' in stats
        assert 'right_word_count' in stats
        assert stats['left_word_count'] > 0
        assert stats['right_word_count'] > 0
    
    def test_compare_different_documents(self, matcher_config, sample_text_1, completely_different_text):
        """Test comparison of completely different documents."""
        matcher = Matcher(matcher_config)
        overall_score, matches, stats = matcher.compare_documents(sample_text_1, completely_different_text)
        
        assert overall_score < 0.5  # Should be low similarity
        assert isinstance(matches, list)
    
    def test_compare_identical_documents(self, matcher_config, sample_text_1):
        """Test comparison of identical documents."""
        matcher = Matcher(matcher_config)
        overall_score, matches, stats = matcher.compare_documents(sample_text_1, sample_text_1)
        
        assert overall_score >= 0.9  # Should be very high
        assert len(matches) > 0
    
    def test_match_types(self, matcher_config, sample_text_1, sample_text_2):
        """Test that different match types are returned."""
        matcher = Matcher(matcher_config)
        overall_score, matches, stats = matcher.compare_documents(sample_text_1, sample_text_2)
        
        if len(matches) > 0:
            match_types = set(m['type'] for m in matches)
            # Should have at least exact or fuzzy matches
            assert 'exact' in match_types or 'fuzzy' in match_types
            for match in matches:
                assert match['type'] in ['exact', 'fuzzy', 'semantic']
                assert 0 <= match['score'] <= 1
    
    def test_matches_have_required_fields(self, matcher_config, sample_text_1, sample_text_2):
        """Test that matches have all required fields."""
        matcher = Matcher(matcher_config)
        overall_score, matches, stats = matcher.compare_documents(sample_text_1, sample_text_2)
        
        if len(matches) > 0:
            required_fields = ['left_text', 'left_start', 'left_end', 'right_text', 
                             'right_start', 'right_end', 'type', 'score']
            for match in matches:
                for field in required_fields:
                    assert field in match


class TestPreprocessor:
    """Test cases for text preprocessor."""
    
    def test_preprocess_normalizes_whitespace(self):
        """Test whitespace normalization."""
        preprocessor = Preprocessor(lowercase=False)
        text = "This   has   multiple     spaces"
        result = preprocessor.preprocess(text)
        assert "  " not in result  # No multiple spaces
    
    def test_preprocess_lowercase(self):
        """Test lowercase conversion."""
        preprocessor = Preprocessor(lowercase=True)
        text = "This Has Capital Letters"
        result = preprocessor.preprocess(text)
        assert result == "this has capital letters"
    
    def test_preprocess_no_lowercase(self):
        """Test that lowercase can be disabled."""
        preprocessor = Preprocessor(lowercase=False)
        text = "This Has Capital Letters"
        result = preprocessor.preprocess(text)
        assert "Has" in result
    
    def test_preprocess_removes_control_chars(self):
        """Test that control characters are removed."""
        preprocessor = Preprocessor(lowercase=False)
        text = "Text\x00with\x01control\x02chars"
        result = preprocessor.preprocess(text)
        assert '\x00' not in result
        assert '\x01' not in result
        assert '\x02' not in result
    
    def test_split_sentences(self):
        """Test sentence splitting."""
        preprocessor = Preprocessor()
        text = "This is sentence one. This is sentence two! Is this sentence three?"
        sentences = preprocessor.split_sentences(text)
        
        assert len(sentences) >= 3
        for sentence in sentences:
            assert len(sentence.strip()) > 0

