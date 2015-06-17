from django.conf.urls import patterns, include, url
from dialectsDB.views import *
from django.contrib import admin
from django.contrib.auth.views import login
from djgeojson.views import GeoJSONLayerView
from django.views.generic import TemplateView
from dialectsDB import paradigms
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dialects.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    #url('^auth/', include('django.contrib.auth.urls')),
    url(r'login/', login, {'extra_context':
                                    {'pageTitle': 'Login', 'paradigmDict': paradigmDict.items()}
                                }),
    url(r'^search/(list)/', searchMultiType),
    url(r'^search/(map)/', searchMultiType),
    #url(r'^search/map2/', search_Map2),
    #url(r'^search/map/([0-9]+)/$',searchMulti), #pre_JS way to have multiple searches
    #url(r'^inputForm/([0-9]+)/$', inputForm),#hack way to have a custom number of items
    url(r'^TSV', tsvView),
    #rl(r'^tableview/',dtview),
    url(r'^inputForm/', inputForm),
    url(r'^complexIn/(\w+)/(\w+)', complexTableInput),
    url(r'^complexIn/(\w+)/', complexTableInput),
    url(r'^complexOut/', complexTableView),
    url(r'^search/cross/', crossSearchView),
    url(r'^list/tags/', taglistview),
    url(r'^list/dialects/', dialectlistview),
    url(r'^list/contributors/', contributorslistview),
    url('^index.html$', aboutview),
    url(r'^$', aboutview),
    url(r'^about.html$', aboutview),
    url(r'^mapcsv/', csvMap),

    #url(r'^autocomplete/', include('autocomplete_light.urls')) #required by autocomplete

)
