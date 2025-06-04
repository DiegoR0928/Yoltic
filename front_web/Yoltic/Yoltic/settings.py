from pathlib import Path
import os

# Construcción de rutas base dentro del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración para archivos de medios (subidas de usuario)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# ------------------------------------------
# Configuración general y seguridad
# ------------------------------------------

# Clave secreta de Django para criptografía, ¡no compartir en producción!
SECRET_KEY = (
    'django-insecure-o1*p#3@z03cb%g&hh_9f@-s4#'
    ')8gi6q+pvyb922v$-$+)($s6('
)

DEBUG = True
ALLOWED_HOSTS = []

# ------------------------------------------
# Aplicaciones instaladas
# ------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'front',
    'usuarios',
    'channels',
]

# ------------------------------------------
# Middleware
# ------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'whitenoise.middleware.WhiteNoiseMiddleware',
]

# ------------------------------------------
# Configuración de URLs y plantillas
# ------------------------------------------
ROOT_URLCONF = 'Yoltic.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'Yoltic.wsgi.application'

# ------------------------------------------
# Base de datos
# ------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER_ADMIN'),
        'PASSWORD': os.environ.get('DB_ROOT_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': '3306',
    }
}



# ------------------------------------------
# Validadores de contraseña
# ------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'MinimumLengthValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'CommonPasswordValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'NumericPasswordValidator'
        ),
    },
]

# ------------------------------------------
# Internacionalización
# ------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ------------------------------------------
# Archivos estáticos
# ------------------------------------------
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# ------------------------------------------
# Django Channels
# ------------------------------------------
ASGI_APPLICATION = "Yoltic.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_REDIRECT_URL = 'login'
