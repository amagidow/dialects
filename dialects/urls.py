from django.conf.urls import patterns, include, url
from dialectsDB.views import *
from django.contrib import admin
from djgeojson.views import GeoJSONLayerView
from django.views.generic import TemplateView
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dialects.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^map/', map_search), #No point for this page right now
    url(r'^mapSearch/', map_search),
    url(r'^interr/', interrInput),
    url(r'^table/', table_view),
    url(r'^tableDJ/', TableView.as_view(template_name="tableView.html")),
    url(r'^search/(list)/', searchMultiType),
    url(r'^search/(map)/', searchMultiType),
    #url(r'^search/map2/', search_Map2),
    #url(r'^search/map/([0-9]+)/$',searchMulti), #pre_JS way to have multiple searches
    #url(r'^inputForm/([0-9]+)/$', inputForm),#hack way to have a custom number of items
    url(r'^inputForm', inputForm),
    url(r'^TSV', tsvView),
    url(r'^leafletmap/', leafletMap),
    url(r'^tableview/',dtview),
    #url(r'[0-9]+/leafletmap', leafletMap),
   # url(r'^data.geojson$', GeoJSONLayerView.as_view(model=Dialect,geometry_field='centerLoc'), name='data'),
    #url(r'^test/$', tableInput),
    url(r'^complexIn/(\w+)/(\w+)', complexTable),
    url(r'^complexIn/(\w+)/', complexTable),
    url(r'^complexOut/', complexTableView),
    url(r'^search/cross/', crossSearchView),
    url(r'^list/tags/', taglistview),
    url(r'^list/dialects/', dialectlistview),
    url(r'^list/contributors/', contributorslistview),
    url('^index.html$', aboutview),
    url(r'^$', aboutview),
    url(r'^about.html$', aboutview),
    url(r'^mapcsv/', csvMap)
    #url(r'^autocomplete/', include('autocomplete_light.urls')) #required by autocomplete

)
