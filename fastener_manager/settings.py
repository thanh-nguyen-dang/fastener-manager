import os
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key and debug settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'fastener-app-secret-key')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Application definition
INSTALLED_APPS = [
    # Default Django apps...
    'django.contrib.auth',
    'django.contrib.contenttypes',  # Ensure this line is present
    'django.contrib.sessions',
    'django.contrib.messages',

    'fastener_app.apps.FastenerAppConfig',
    'rest_framework',
]

MIDDLEWARE = [
    # Default middleware...
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # Other middleware...
]

ROOT_URLCONF = 'fastener_manager.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # Directory for your project-level templates
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Default context processors
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Add custom context processors here
            ],
            # 'loaders': [  # Optionally customize template loaders
            #     ('django.template.loaders.cached.Loader', [
            #         'django.template.loaders.filesystem.Loader',
            #         'django.template.loaders.app_directories.Loader',
            #     ]),
            # ],
        },
    },
]

WSGI_APPLICATION = 'fastener_manager.wsgi.application'

DB_SCHEMA = os.environ.get('DB_SCHEMA', 'fastener_manager')

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'ingest_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'options': f"-c search_path={DB_SCHEMA},public",
        },
    }
}

DB_SCHEMA = "fastener_manager"

# Cache configuration (Redis)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f"redis://{os.environ.get('REDIS_HOST', 'localhost')}:{os.environ.get('REDIS_PORT', '6379')}/1",
    }
}

# Password validation, internationalization, static files, etc.

# Rest Framework settings
REST_FRAMEWORK = {
    # DRF settings...
}
