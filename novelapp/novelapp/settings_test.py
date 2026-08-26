"""
Test settings for Novel-It.

Inherits everything from the main settings module except where overridden
below. In particular, DATABASES stays pointed at Postgres (via the same
DATABASE_URL read in .env) rather than SQLite, because SQLite silently
masks bulk-UPDATE ordering issues that Postgres's query planner does not
-- exactly the class of bug already found in the reorder views.

Django's test runner creates and destroys a disposable `test_<name>`
database on the same Postgres server automatically for each run -- it
never touches the real dev database. This requires the DATABASE_URL role
to have CREATEDB privilege; see project notes for the check/grant command.
"""

from .settings import *

# Override SECRET_KEY for testing -- never used outside test runs.
SECRET_KEY = 'test-secret-key-for-ci-cd-testing-only-not-for-production'

# Run tests closer to production behaviour (also matches how the app is
# actually deployed, rather than the DEBUG=True dev default).
DEBUG = False

# Speed up user-creation-heavy tests -- characters, locations, items all
# scope to a user, so many tests create one. Hasher security doesn't
# matter for throwaway test data.
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# No lingering connections between short-lived test runs.
DATABASES['default']['CONN_MAX_AGE'] = 0
