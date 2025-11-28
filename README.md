# Document Comparison Tool

A Django web application that compares two documents and identifies matching sections using multiple algorithms: exact matching, fuzzy matching, and semantic similarity with sentence embeddings.

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2-green.svg)

## Features

- **Multiple File Formats**: Supports PDF, DOCX, and TXT files
- **Smart Comparison**: Uses three matching strategies:
  - **Exact Matching**: Finds identical substrings
  - **Fuzzy Matching**: Detects similar text using RapidFuzz (configurable threshold, default 85%)
  - **Semantic Matching**: Uses sentence embeddings (all-MiniLM-L6-v2) for meaning-based comparison (threshold 75%)
- **Interactive Frontend**: Side-by-side document view with highlighted matches
- **RESTful API**: Clean JSON API for programmatic access
- **Comprehensive Testing**: Unit tests for extraction and matching logic
- **Configurable**: Easily adjust thresholds, models, and settings via environment variables

## Requirements

- Python 3.11+
- Django 4.2+
- Node.js (optional, for installing packages if needed)

## Installation

1. **Clone the repository** (or navigate to project directory):
   ```bash
   cd G:/DjangoProject
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional):
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   MAX_FILE_SIZE_MB=10
   FUZZY_MIN_RATIO=0.85
   SEMANTIC_THRESHOLD=0.75
   EMBEDDING_MODEL=all-MiniLM-L6-v2
   TOP_N_MATCHES=20
   ENABLE_SEMANTIC=true
   LOWERCASE=true
   TEMP_FILE_RETENTION_HOURS=24
   ```

5. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser** (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   - Web UI: http://127.0.0.1:8000/
   - API endpoint: http://127.0.0.1:8000/api/compare/
   - Admin panel: http://127.0.0.1:8000/admin/

## Usage

### Web Interface

1. Open http://127.0.0.1:8000/ in your browser
2. Upload two documents (PDF, DOCX, or TXT)
3. Click "Compare Documents"
4. View results:
   - Overall similarity score
   - Side-by-side document view with highlighted matches
   - List of top matches with scores
   - Toggle different match types

### API Usage

#### Endpoint: `POST /api/compare/`

**Request** (multipart/form-data):
```
left_file: [file]
right_file: [file]
fuzzy_min_ratio: 0.85 (optional)
semantic_threshold: 0.75 (optional)
top_n: 20 (optional)
enable_semantic: true (optional)
lowercase: true (optional)
```

**Response**:
```json
{
  "overall_score": 0.72,
  "matches": [
    {
      "left_text": "This is a matching section...",
      "left_start": 123,
      "left_end": 172,
      "right_text": "This is a matching section...",
      "right_start": 45,
      "right_end": 94,
      "type": "semantic",
      "score": 0.88
    }
  ],
  "stats": {
    "left_word_count": 2340,
    "right_word_count": 1980,
    "total_matches": 47,
    "left_chars": 12345,
    "right_chars": 10123
  }
}
```

#### Example using cURL:
```bash
curl -X POST http://127.0.0.1:8000/api/compare/ \
  -F "left_file=@document1.pdf" \
  -F "right_file=@document2.pdf"
```

#### Example using Python:
```python
import requests

url = 'http://127.0.0.1:8000/api/compare/'
files = {
    'left_file': open('document1.pdf', 'rb'),
    'right_file': open('document2.pdf', 'rb')
}
data = {
    'fuzzy_min_ratio': 0.85,
    'semantic_threshold': 0.75,
    'top_n': 20
}

response = requests.post(url, files=files, data=data)
result = response.json()

print(f"Overall similarity: {result['overall_score'] * 100:.1f}%")
print(f"Found {len(result['matches'])} matches")
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | *(generated)* | Django secret key for production |
| `MAX_FILE_SIZE_MB` | 10 | Maximum file size in MB |
| `FUZZY_MIN_RATIO` | 0.85 | Minimum fuzzy match ratio (0-1) |
| `SEMANTIC_THRESHOLD` | 0.75 | Semantic similarity threshold (0-1) |
| `EMBEDDING_MODEL` | all-MiniLM-L6-v2 | Sentence transformer model |
| `TOP_N_MATCHES` | 20 | Maximum matches to return |
| `ENABLE_SEMANTIC` | true | Enable semantic matching |
| `LOWERCASE` | true | Convert text to lowercase before comparison |
| `TEMP_FILE_RETENTION_HOURS` | 24 | Hours to keep temp files |

### Adjusting Matching Thresholds

**Higher fuzzy_min_ratio (e.g., 0.9)**: Fewer, more precise fuzzy matches
**Lower fuzzy_min_ratio (e.g., 0.7)**: More fuzzy matches, including less similar text

**Higher semantic_threshold (e.g., 0.85)**: Only strong semantic similarities
**Lower semantic_threshold (e.g., 0.65)**: More semantic matches with related concepts

## Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

Run specific test files:
```bash
pytest tests/test_extractor.py
pytest tests/test_matcher.py
```

## Project Structure

```
DjangoProject/
├── document_compare/          # Main Django project settings
│   ├── settings.py            # Configuration
│   ├── urls.py                # URL routing
│   └── ...
├── uploader/                  # Upload and extraction app
│   ├── extractor.py          # Text extraction (PDF, DOCX, TXT)
│   ├── utils.py              # File validation and utilities
│   └── ...
├── compare/                   # Comparison logic app
│   ├── matcher.py            # Document matching algorithms
│   ├── preprocessor.py       # Text preprocessing
│   ├── views.py              # API views
│   ├── serializers.py        # DRF serializers
│   └── urls.py               # API URLs
├── frontend/                  # Frontend assets
│   ├── index.html            # Main UI
│   └── static/               # CSS/JS files
├── tests/                     # Test suite
│   ├── test_extractor.py     # Extraction tests
│   └── test_matcher.py       # Matching tests
├── requirements.txt           # Python dependencies
├── manage.py                  # Django management script
└── README.md                  # This file
```

## Architecture

### Matching Pipeline

1. **Text Extraction**: Extract text from PDF/DOCX/TXT using appropriate libraries
2. **Preprocessing**: Normalize whitespace, remove control chars, optional lowercase
3. **Exact Matching**: Find identical substrings (min 3 words)
4. **Fuzzy Matching**: Use RapidFuzz to find similar sentences (>85% similarity)
5. **Semantic Matching**: Compute sentence embeddings and cosine similarity
6. **Deduplication**: Remove overlapping matches
7. **Ranking**: Sort by score and return top N matches

### Security & Privacy

- Files are deleted immediately after processing
- Filenames are sanitized to prevent directory traversal
- File types and sizes are validated
- Uploads stored in non-public directory
- Ready for rate limiting / CAPTCHA integration

## Limitations & Future Enhancements

### Current Limitations
- Large files (>10MB) may take time to process
- Semantic matching requires sentence-transformers download (~80MB)
- UI shows match summary, not full document highlighting (text extraction on frontend needed)

### Future Enhancements
- [ ] PDF report export with matched snippets
- [ ] Diff-like inline view showing insertions/deletions
- [ ] Language detection and multilingual embeddings
- [ ] Async processing with Celery for large files
- [ ] Full document highlighting in UI
- [ ] Threshold slider on frontend
- [ ] Support for more file formats (RTF, ODT)

## Troubleshooting

### "No module named 'sentence_transformers'"
```bash
pip install sentence-transformers
```
Note: First run will download the model (~80MB)

### Torch Installation Issues

If torch installation fails or is too large, use CPU-only version:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

Or install requirements with CPU torch:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

### "Unable to extract PDF"
- Ensure pdfminer.six is installed
- Check file isn't password-protected
- Try converting PDF to text using an external tool

### Semantic matching not working
- Check `ENABLE_SEMANTIC=true` in environment
- Ensure internet connection for model download
- Verify sentence-transformers is installed correctly

### Tests failing
```bash
# Recreate database
rm db.sqlite3
python manage.py migrate
pytest --create-db
```

## License

This project is provided as-is for demonstration purposes.

## Contributing

Contributions welcome! Please ensure:
1. All tests pass
2. Code follows PEP 8
3. New features include tests
4. Documentation is updated

## Credits

Built with:
- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [sentence-transformers](https://www.sbert.net/)
- [RapidFuzz](https://github.com/maxbachmann/RapidFuzz)
- [pdfminer.six](https://github.com/pdfminer/pdfminer.six)
- [python-docx](https://python-docx.readthedocs.io/)

## Support

For issues or questions, please open an issue in the repository or contact the development team.

