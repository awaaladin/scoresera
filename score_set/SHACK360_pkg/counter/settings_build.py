"""
Minimal Django settings for Vercel build process.
This avoids importing any database backends during collectstatic.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "build-secret-key"
DEBUG = False
ALLOWED_HOSTS = ['*']

# Minimal apps needed for collectstatic
INSTALLED_APPS = [
    'django.contrib.staticfiles',
]

MIDDLEWARE = []

ROOT_URLCONF = "counter.urls"

TEMPLATES = []

# Dummy database - won't be used during collectstatic
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.dummy',
    }
}

# Static files
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "theme" / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
