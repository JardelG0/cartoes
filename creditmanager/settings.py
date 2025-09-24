from pathlib import Path
import dj_database_url
import os
from dotenv import load_dotenv

load_dotenv()  # carrega variáveis do .env

BASE_DIR = Path(__file__).resolve().parent.parent

# ===================== Media (uploads) =====================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ===================== Básico =====================
# Em produção: defina SECRET_KEY no ambiente
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-unsafe-change-me')

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

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
# Lógica robusta para DATABASE_URL (mantida)
DATABASE_URL = os.getenv('DATABASE_URL', '').strip()

if DATABASE_URL:
    try:
        db_config = dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=not DEBUG)
    except Exception as e:
        import sys
        print("ERRO ao parsear DATABASE_URL:", e, file=sys.stderr)
        db_config = None

    if db_config:
        engine = db_config.get('ENGINE', '')
        if engine and 'sqlite' in engine:
            options = db_config.get('OPTIONS')
            if isinstance(options, dict):
                if 'sslmode' in options:
                    options.pop('sslmode', None)
                for key in ('sslrootcert', 'sslcert', 'sslkey'):
                    options.pop(key, None)
                if not options:
                    db_config.pop('OPTIONS', None)
        if 'conn_max_age' not in db_config and 'CONN_MAX_AGE' in db_config:
            db_config['conn_max_age'] = db_config.pop('CONN_MAX_AGE')

        DATABASES = {'default': db_config}
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'creditmanager',
                'USER': 'postgres',
                'PASSWORD': 'postgres',
                'HOST': 'localhost',
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'creditmanager',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': 'localhost',
        }
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

# ===================== Staticfiles =====================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# ===================== Segurança / SSL (ajustada) =====================
# Explicação rápida:
#  - Em DEBUG (desenvolvimento) NÃO forçamos HTTPS nem cookies secure.
#  - Em produção (DEBUG=False) ativamos os controles apenas se as env vars solicitarem.
#
# Variáveis de ambiente relacionadas:
#  - SECURE_SSL_REDIRECT (True/False)   -> se True e DEBUG=False, força redirecionamento HTTP->HTTPS
#  - FORCE_SESSION_COOKIE_SECURE (True/False) -> se True e DEBUG=False, seta SESSION_COOKIE_SECURE=True
#  - FORCE_CSRF_COOKIE_SECURE (True/False) -> se True e DEBUG=False, seta CSRF_COOKIE_SECURE=True
#  - CSRF_TRUSTED_ORIGINS -> lista separada por vírgula com domínio(s) https://...
#  - USE_X_FORWARDED_HOST (True/False) -> se usando proxy, pode ser útil

# Por padrão, em produção NÃO ativamos SSL redirect a menos que env diga.
SECURE_SSL_REDIRECT = False
if not DEBUG:
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False').lower() == 'true'

# Cookies seguros (setados apenas em produção e se explicitamente solicitado)
if not DEBUG:
    if os.getenv('FORCE_SESSION_COOKIE_SECURE', 'False').lower() == 'true':
        SESSION_COOKIE_SECURE = True
    else:
        SESSION_COOKIE_SECURE = False

    if os.getenv('FORCE_CSRF_COOKIE_SECURE', 'False').lower() == 'true':
        CSRF_COOKIE_SECURE = True
    else:
        CSRF_COOKIE_SECURE = False
else:
    # Em dev, garantir que cookies não estejam marcados como 'secure' para evitar problemas com HTTP local
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# Se estiver atrás de um proxy/terminador TLS (nginx, heroku, render), use:
# Ex.: SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# (Ative apenas em produção / quando seu proxy realmente envia esse header.)
SECURE_PROXY_SSL_HEADER = None
if os.getenv('USE_X_FORWARDED_PROTO', 'False').lower() == 'true':
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HSTS (apenas em produção e quando SECURE_SSL_REDIRECT=True)
# Se ativar, configure também SECURE_HSTS_SECONDS via env (ex: 31536000)
if not DEBUG and SECURE_SSL_REDIRECT:
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '0'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'False').lower() == 'true'
    SECURE_HSTS_PRELOAD = os.getenv('SECURE_HSTS_PRELOAD', 'False').lower() == 'true'
else:
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False

# CSRF trusted origins (apenas em produção — inclua esquema "https://")
CSRF_TRUSTED_ORIGINS = []
if not DEBUG:
    ct = os.getenv('CSRF_TRUSTED_ORIGINS', '')
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in ct.split(',') if o.strip()]

# ===================== Logging simples =====================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
}
