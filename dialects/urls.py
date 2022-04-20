from django.urls import include, re_path
from dialectsDB.views import *
from django.contrib import admin
from django.contrib.auth import views as auth_views
#from djgeojson.views import GeoJSONLayerView
#from django.views.generic import TemplateView
from dialectsDB import paradigms
admin.autodiscover()

urlpatterns = [

    # Examples:
    # url(r'^$', 'dialects.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    re_path(r'^admin/', admin.site.urls),
    #url('^auth/', include('django.contrib.auth.urls')),
    re_path(r'login/', auth_views.LoginView.as_view(), name="login"),#, {'extra_context':
                                    #{'pageTitle': 'Login', 'paradigmDict': paradigmDict.items()}}),
    re_path(r'logout/', mylogout),
    re_path(r'^search/(list)/', searchMultiType),
    re_path(r'^search/(map)/', searchMultiType),
    #url(r'^search/map2/', search_Map2),
    #url(r'^search/map/([0-9]+)/$',searchMulti), #pre_JS way to have multiple searches
    #url(r'^inputForm/([0-9]+)/$', inputForm),#hack way to have a custom number of items
    re_path(r'^TSV', tsvView),
    #rl(r'^tableview/',dtview),
    re_path(r'^inputForm/', inputForm),
    re_path(r'^complexIn/(\w+)/(\w+)', complexTableInput),
    re_path(r'^complexIn/(\w+)/', complexTableInput),
    re_path(r'^complexOut/', complexTableView),
    re_path(r'^search/cross/', crossSearchView),
    re_path(r'^list/tags/', taglistview),
    re_path(r'^list/dialects/', dialectlistview),
    re_path(r'^list/contributors/', contributorslistview),
    re_path(r'^list/biblio/', bibliolistview),
    re_path('^index.html$', aboutview),
    re_path(r'^$', aboutview),
    re_path(r'^about.html$', aboutview),
    re_path(r'^versions.html$', versionview),
    re_path(r'^mapcsv/', csvMap),

    #url(r'^autocomplete/', include('autocomplete_light.urls')) #required by autocomplete

]
