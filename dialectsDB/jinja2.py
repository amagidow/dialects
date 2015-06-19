__author__ = 'Alex'
from jinja2 import Environment
from django.template.context_processors import csrf
from django.contrib.staticfiles.storage import staticfiles_storage
from dialects.settings import STATIC_URL

def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'STATIC_URL' : STATIC_URL, #Tag as key, result as value - accessed like {{ KEY }}
        'csrf_token': csrf
    })
    return env