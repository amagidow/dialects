# coding=UTF-8
"""
Django settings for dialects project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DIALECTDBSK']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = [
    "database-of-arabic-dialects.org"
]


# Application definition

INSTALLED_APPS = (
    'autocomplete_light',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.postgres',
     'dialectsDB',
    'leaflet',
    'djgeojson'
  ,'django_jinja'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'dialects.urls'

WSGI_APPLICATION = 'dialects.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'arabicDialectProject',
        'USER': 'Magidow',
        'PASSWORD': 'arabic',
        'HOST': '127.0.0.1',
        'PORT': '5432',

    }
}

TEMPLATES = [
      {
        "BACKEND": "django_jinja.backend.Jinja2",
        "APP_DIRS": True,

        "OPTIONS": {
            "match_extension": ".jinja",
            "app_dirname": "templates/",
             'context_processors': [

                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.core.context_processors.csrf'

            ],
        }
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'templates/',
            'dialectsDB/templates/'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.core.context_processors.csrf'

            ],
    },
    },


]
TEMPLATE_LOADERS = (
    'django_jinja.loaders.FileSystemLoader',
    'django_jinja.loaders.AppLoader',
)

TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
"django.core.context_processors.debug",
"django.core.context_processors.i18n",
"django.core.context_processors.media",
"django.core.context_processors.static",
"django.core.context_processors.tz",
"django.contrib.messages.context_processors.messages",
"django.core.context_processors.request",
'django.core.context_processors.csrf'
                               )


#DEFAULT_JINJA2_TEMPLATE_INTERCEPT_RE = r'.*jinja$'
#jinja2.Environment(trim_blocks=True)
# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/


#SOUTH_MIGRATION_MODULES = {
#'taggit': 'taggit.south_migrations',
#}

LOGIN_REDIRECT_URL = "/about.html"

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
#GEOS_LIBRARY_PATH = 'C:/OSGeo4W/bin/geos_c.dll'
#GDAL_LIBRARY_PATH = 'C:/OSGeo4W/bin/gdal111.dll'
#GDAL_DATA = 'C:/Program Files/PostgreSQL/9.3/gdal-data/'
PYTHONIOENCODING='utf-8'