# inventix_project/settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ⚠️ CAMBIA ESTA CLAVE POR UNA SEGURA
SECRET_KEY = 'django-insecure-xyz123-cambia-esta-clave'

DEBUG = True

# ==========================================
# CONFIGURACIÓN DE HOSTS Y CSRF (ACTUALIZADO)
# ==========================================

# Permitir todas las IPs para desarrollo
ALLOWED_HOSTS = ['*']

# CSRF Trusted Origins - IMPORTANTE PARA NGORK
CSRF_TRUSTED_ORIGINS = [
    # Ngrok (tu URL actual)
    'https://photo-fried-sierra.ngrok-free.dev',
    # Todas las de ngrok
    'https://*.ngrok-free.dev',
    'https://*.ngrok.io',
    # Local
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://192.168.1.73:8000',
    'http://192.168.1.73',
    'http://0.0.0.0:8000',
]

# Configuración para desarrollo con ngrok
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SAMESITE = 'Lax'

SESSION_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = 'Lax'
SECURE_SSL_REDIRECT = False

# ==========================================
# APLICACIONES INSTALADAS
# ==========================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Nuestras aplicaciones
    'productos',
    'ventas',
    'usuarios',
    'dashboard',
    # Terceros
    'crispy_forms',
    'crispy_bootstrap5',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Para archivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'inventix_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'inventix_project.wsgi.application'

# ==========================================
# CONFIGURACIÓN DE POSTGRESQL
# ==========================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'inventix_db',
        'USER': 'postgres',
        'PASSWORD': 'Nutri/Roquia/2026.',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# ==========================================
# VALIDACIÓN DE CONTRASEÑAS
# ==========================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==========================================
# IDIOMA Y ZONA HORARIA
# ==========================================
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# ==========================================
# ARCHIVOS ESTÁTICOS
# ==========================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Configuración para WhiteNoise (archivos estáticos en producción)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==========================================
# CRISPY FORMS
# ==========================================
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ==========================================
# AUTENTICACIÓN
# ==========================================
LOGIN_URL = '/login/'  # Usar URL global
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

STOCK_MINIMO = 5