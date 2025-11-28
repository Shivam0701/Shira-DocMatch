"""
Text extraction module for various document types.
"""
import os
import re
from pathlib import Path
from typing import Tuple, Optional

from docx import Document
from pdfminer.high_level import extract_text as pdf_extract


class Extractor:
    """Extracts text from various document formats."""
    
    @staticmethod
    def extract(file_path: str, file_type: str) -> Tuple[str, dict]:
        """
        Extract text from a file.
        
        Args:
            file_path: Path to the file
            file_type: MIME type of the file
            
        Returns:
            Tuple of (extracted_text, metadata_dict)
            
        Raises:
            ValueError: If file type is not supported
            IOError: If file cannot be read
        """
        if not os.path.exists(file_path):
            raise IOError(f"File not found: {file_path}")
        
        file_ext = Path(file_path).suffix.lower()
        
        # Check if both MIME type and extension are valid (or if one matches)
        is_pdf = file_type == 'application/pdf' or file_ext == '.pdf'
        is_docx = file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' or file_ext == '.docx'
        is_txt = file_type == 'text/plain' or file_ext == '.txt'
        
        # If MIME type is completely unknown and extension doesn't match, reject
        if not is_pdf and not is_docx and not is_txt:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        if is_pdf:
            return Extractor._extract_pdf(file_path)
        elif is_docx:
            return Extractor._extract_docx(file_path)
        elif is_txt:
            return Extractor._extract_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    @staticmethod
    def _extract_pdf(file_path: str) -> Tuple[str, dict]:
        """Extract text from PDF file."""
        try:
            text = pdf_extract(file_path)
            return text, {'format': 'pdf', 'chars_extracted': len(text)}
        except Exception as e:
            raise IOError(f"Error extracting PDF: {str(e)}")
    
    @staticmethod
    def _extract_docx(file_path: str) -> Tuple[str, dict]:
        """Extract text from DOCX file."""
        try:
            doc = Document(file_path)
            paragraphs = []
            for para in doc.paragraphs:
                paragraphs.append(para.text)
            text = '\n'.join(paragraphs)
            return text, {'format': 'docx', 'chars_extracted': len(text)}
        except Exception as e:
            raise IOError(f"Error extracting DOCX: {str(e)}")
    
    @staticmethod
    def _extract_txt(file_path: str) -> Tuple[str, dict]:
        """Extract text from TXT file."""
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return text, {'format': 'txt', 'chars_extracted': len(text)}
        except UnicodeDecodeError:
            # Fallback to latin-1
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    text = f.read()
                return text, {'format': 'txt', 'chars_extracted': len(text)}
            except Exception as e:
                raise IOError(f"Error extracting TXT: {str(e)}")

