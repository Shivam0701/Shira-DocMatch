"""
Tests for text extraction module.
"""
import pytest
import os
import tempfile
from pathlib import Path
from uploader.extractor import Extractor


@pytest.fixture
def sample_txt_content():
    """Sample text content for testing."""
    return """This is a test document.
It contains multiple paragraphs.

This is the second paragraph with some more content.
We will use this to test document comparison.
"""


@pytest.fixture
def temp_txt_file(sample_txt_content):
    """Create a temporary TXT file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_txt_content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)


class TestExtractor:
    """Test cases for text extractor."""
    
    def test_extract_txt(self, temp_txt_file, sample_txt_content):
        """Test TXT file extraction."""
        text, metadata = Extractor.extract(temp_txt_file, 'text/plain')
        
        assert text is not None
        assert len(text) > 0
        assert metadata['format'] == 'txt'
        assert 'chars_extracted' in metadata
        # Compare without whitespace differences
        assert text.strip() == sample_txt_content.strip()
    
    def test_extract_nonexistent_file(self):
        """Test extraction of non-existent file raises error."""
        with pytest.raises(IOError):
            Extractor.extract('/path/that/does/not/exist.txt', 'text/plain')
    
    def test_extract_unsupported_type(self, temp_txt_file):
        """Test extraction of unsupported file type raises error."""
        # Create a file with unsupported extension
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
            f.write("test content")
            bad_path = f.name
        
        try:
            with pytest.raises(ValueError):
                Extractor.extract(bad_path, 'application/unsupported')
        finally:
            if os.path.exists(bad_path):
                os.remove(bad_path)
    
    def test_extract_by_extension(self, temp_txt_file):
        """Test extraction using file extension."""
        text, metadata = Extractor.extract(temp_txt_file, 'application/unknown')
        assert text is not None  # Should work based on .txt extension
    
    def test_extract_utf8_encoding(self):
        """Test UTF-8 encoding handling."""
        unicode_content = "Hello 世界. こんにちは."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(unicode_content)
            temp_path = f.name
        
        try:
            text, metadata = Extractor.extract(temp_path, 'text/plain')
            assert '世界' in text
            assert 'こんにちは' in text
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

