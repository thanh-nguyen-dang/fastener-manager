from .settings import *  # Import all settings from the main settings.py

DEBUG = False
TESTING = True

# Override the database configuration to use PostgreSQL with a different database for testing
# Use a different database name for testing

# Optionally, use a different schema for testing
DB_SCHEMA = os.environ.get('DB_SCHEMA', 'fasten_manager')
DB_NAME = os.environ.get('TEST_DB_NAME', 'ingest_db_test')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,  # Use your desired test database name
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'options': f"-c search_path={DB_SCHEMA},public",
        },
        'TEST': {
            'NAME': DB_NAME,  # Specify the test database name
        },
    }
}
DATABASES['default']['OPTIONS']['options'] = f"-c search_path={DB_SCHEMA},public"

# Set a different secret key for testing
SECRET_KEY = 'test-secret-key'

# Optionally, you can adjust other settings as needed for testing
