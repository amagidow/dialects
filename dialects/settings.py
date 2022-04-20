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
from dialects.localsettings import *
BASE_DIR = os.path.dirname(os.path.dirname(__file__))




# Application definition

INSTALLED_APPS = (
        'django.contrib.contenttypes',
    'autocomplete_light',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'django.contrib.gis',
    'django.contrib.postgres',
     'dialectsDB',
    #'leaflet',
    #'geojson',
  'django_jinja'
)

if LOCAL_INSTALLED_APPS: #Allows for having extra apps installed only on one of the servers
    INSTALLED_APPS = INSTALLED_APPS + LOCAL_INSTALLED_APPS




ROOT_URLCONF = 'dialects.urls'

WSGI_APPLICATION = 'dialects.wsgi.application'


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
                'django.template.context_processors.csrf'

            ],
        }
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'templates/',
            'dialectsDB/templates/'
        ],
        #'APP_DIRS': True,
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
                'django.template.context_processors.csrf'

            ],
            'loaders' : [
                'django_jinja.loaders.FileSystemLoader',
                'django_jinja.loaders.AppLoader',
                'django.template.loaders.app_directories.Loader'
            ]
    },
    },

]
# TEMPLATE_LOADERS = (
#     'django_jinja.loaders.FileSystemLoader',
#     'django_jinja.loaders.AppLoader',
# )

# TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
# "django.core.context_processors.debug",
# "django.core.context_processors.i18n",
# "django.core.context_processors.media",
# "django.core.context_processors.static",
# "django.core.context_processors.tz",
# "django.contrib.messages.context_processors.messages",
# "django.core.context_processors.request",
# 'django.core.context_processors.csrf'
#                                )

LEAFLET_CONFIG = {
    'TILES': [('OpenStreetMap.Mapnik', 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
               {
                   'type': 'map',
	                'attribution': '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'#,
	                #'subdomains': '1234'
               })]
}

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