from .settings import *

# Override SECRET_KEY for testing
SECRET_KEY = 'test-secret-key-for-ci-cd-testing-only-not-for-production'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}
