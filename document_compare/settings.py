"""
Django settings for document_compare project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file (explicit path — safest)
load_dotenv(dotenv_path=BASE_DIR / '.env')


# -------------------
# Basic Settings
# -------------------

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key-change-in-production')

DEBUG = os.getenv("DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = ["*", "shira-docmatch.onrender.com"]



# -------------------
# Applications
# -------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',

    # Local apps
    'uploader',
    'compare',
]


# -------------------
# Middleware
# -------------------

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'document_compare.urls'


# -------------------
# Templates
# -------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'frontend'],   # your frontend folder
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'document_compare.wsgi.application'


# -------------------
# Database
# -------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# -------------------
# Password Validators
# -------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# -------------------
# Internationalization
# -------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# -------------------
# Static & Media Files
# -------------------

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'frontend' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'uploaded_files'


# -------------------
# Django REST Framework Settings
# -------------------

REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}


# -------------------
# File Upload Limits
# -------------------

FILE_UPLOAD_MAX_MEMORY_SIZE = int(os.getenv('MAX_FILE_SIZE_MB', '10')) * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = FILE_UPLOAD_MAX_MEMORY_SIZE

ALLOWED_FILE_TYPES = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain'
]

ALLOWED_FILE_EXTENSIONS = ['.pdf', '.docx', '.txt']


# -------------------
# Temp File Settings
# -------------------

TEMP_FILE_RETENTION_HOURS = int(os.getenv('TEMP_FILE_RETENTION_HOURS', '24'))


# -------------------
# Comparison Settings
# -------------------

COMPARISON_CONFIG = {
    'FUZZY_MIN_RATIO': float(os.getenv('FUZZY_MIN_RATIO', '0.85')),
    'SEMANTIC_THRESHOLD': float(os.getenv('SEMANTIC_THRESHOLD', '0.75')),
    'EMBEDDING_MODEL': os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2'),
    'TOP_N_MATCHES': int(os.getenv('TOP_N_MATCHES', '20')),
    'ENABLE_SEMANTIC': os.getenv('ENABLE_SEMANTIC', 'true').lower() == 'true',
    'LOWERCASE': os.getenv('LOWERCASE', 'true').lower() == 'true',
}


# -------------------
# Default Primary Key Field
# -------------------

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
