from pathlib import Path
import dj_database_url
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ===================== Media (uploads) =====================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ===================== Básico =====================
# Em produção: defina SECRET_KEY no ambiente
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-inseguro-altere')

DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Ex.: "seuapp.onrender.com,www.seudominio.com"
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h.strip()]

# ===================== Apps =====================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # terceiros
    'django.contrib.humanize',

    # seus apps
    'cartoes_app',
]

# ===================== Auth redirects =====================
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'   # para voltar à home (acesso). Use '/login/' se preferir.

# ===================== Middleware =====================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise deve vir logo após SecurityMiddleware (antes de Session)
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'creditmanager.urls'

# ===================== Templates =====================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Se você mantém templates fora dos apps, deixe aqui:
        'DIRS': [BASE_DIR / 'cartoes_app' / 'templates'],
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

WSGI_APPLICATION = 'creditmanager.wsgi.application'

# ===================== Banco de Dados =====================
# Local (default): sqlite
# Produção: use DATABASE_URL (Postgres)
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,           # pooling
        ssl_require=not DEBUG       # exige SSL em produção
    )
}

# ===================== Validação de senha =====================
AUTH_PASSWORD_VALIDATORS = [
    # Deixamos vazio durante a fase de validação visual.
    # Em produção real, reative os validadores recomendados do Django.
]

# ===================== i18n / Locale =====================
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Formatação estilo BR
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = '.'
DECIMAL_SEPARATOR = ','

# (Django 5 ignora USE_L10N; pode remover se quiser)
# USE_L10N = True

# ===================== Staticfiles =====================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Django 5: configurar via STORAGES (substitui STATICFILES_STORAGE)
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}
# Se você tiver uma pasta 'static' na raiz com arquivos próprios:
# STATICFILES_DIRS = [BASE_DIR / 'static']

# ===================== Segurança (produção) =====================
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True').lower() == 'true'

    # Origem CSRF precisa do esquema (https)
    # Ex.: "https://seuapp.onrender.com,https://www.seudominio.com"
    CSRF_TRUSTED_ORIGINS = [
        o.strip() for o in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()
    ]

# ===================== Logging simples =====================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
}
