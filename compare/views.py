"""
API views for document comparison.
"""
import os
import shutil
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from uploader.extractor import Extractor
from uploader.utils import validate_file, sanitize_filename, ensure_upload_dir
from compare.matcher import Matcher
from compare.serializers import DocumentComparisonSerializer


class DocumentCompareView(APIView):
    """API endpoint for comparing two documents."""
    
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """
        Compare two uploaded documents.
        
        Expected form data:
        - left_file: First document file
        - right_file: Second document file
        - (optional) mode: Comparison mode
        - (optional) fuzzy_min_ratio: Minimum fuzzy match ratio
        - (optional) semantic_threshold: Semantic similarity threshold
        - (optional) top_n: Maximum number of matches to return
        - (optional) enable_semantic: Enable semantic matching (true/false)
        - (optional) lowercase: Convert to lowercase (true/false)
        
        Returns:
            JSON response with comparison results
        """
        # Validate files
        if 'left_file' not in request.FILES or 'right_file' not in request.FILES:
            return Response(
                {'error': 'Both left_file and right_file are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        left_file = request.FILES['left_file']
        right_file = request.FILES['right_file']
        
        # Validate files
        left_valid, left_error = validate_file(left_file)
        if not left_valid:
            return Response({'error': f'Left file: {left_error}'}, status=status.HTTP_400_BAD_REQUEST)
        
        right_valid, right_error = validate_file(right_file)
        if not right_valid:
            return Response({'error': f'Right file: {right_error}'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Ensure upload directory exists
        ensure_upload_dir()
        
        # Save files temporarily
        left_filename = sanitize_filename(left_file.name)
        right_filename = sanitize_filename(right_file.name)
        
        left_path = os.path.join(settings.MEDIA_ROOT, left_filename)
        right_path = os.path.join(settings.MEDIA_ROOT, right_filename)
        
        # Save uploaded files
        try:
            with open(left_path, 'wb+') as dest:
                for chunk in left_file.chunks():
                    dest.write(chunk)
            
            with open(right_path, 'wb+') as dest:
                for chunk in right_file.chunks():
                    dest.write(chunk)
            
            # Extract text from both files
            left_text, left_metadata = Extractor.extract(left_path, left_file.content_type)
            right_text, right_metadata = Extractor.extract(right_path, right_file.content_type)
            
            # Get comparison configuration (use request params if provided, otherwise use defaults)
            config = settings.COMPARISON_CONFIG.copy()
            if 'fuzzy_min_ratio' in request.data:
                config['FUZZY_MIN_RATIO'] = float(request.data['fuzzy_min_ratio'])
            if 'semantic_threshold' in request.data:
                config['SEMANTIC_THRESHOLD'] = float(request.data['semantic_threshold'])
            if 'top_n' in request.data:
                config['TOP_N_MATCHES'] = int(request.data['top_n'])
            if 'enable_semantic' in request.data:
                config['ENABLE_SEMANTIC'] = request.data['enable_semantic'].lower() == 'true'
            if 'lowercase' in request.data:
                config['LOWERCASE'] = request.data['lowercase'].lower() == 'true'
            
            # Perform comparison
            matcher = Matcher(config)
            overall_score, matches, stats = matcher.compare_documents(left_text, right_text)
            
            # Build response
            stats.update({
                'left_chars': len(left_text),
                'right_chars': len(right_text),
                'left_format': left_metadata.get('format'),
                'right_format': right_metadata.get('format'),
            })
            
            response_data = {
                'overall_score': overall_score,
                'matches': matches,
                'stats': stats,
                'left_text': left_text,
                'right_text': right_text
            }
            
            serializer = DocumentComparisonSerializer(data=response_data)
            if serializer.is_valid():
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except ValueError as e:
            return Response(
                {'error': f'Unsupported file type: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except IOError as e:
            return Response(
                {'error': f'File processing error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {'error': f'Unexpected error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            # Clean up uploaded files
            if os.path.exists(left_path):
                os.remove(left_path)
            if os.path.exists(right_path):
                os.remove(right_path)

