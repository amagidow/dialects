# coding=UTF-8
from django.contrib import admin
from django.contrib.gis import admin
from dialectsDB.models import *
#from geoposition import widgets
from django import forms
from django.contrib.gis import forms
from django.contrib.gis.db import models
from django.contrib.auth.admin import UserAdmin
from dialectsDB.utilityfuncs import permissionwrapper

# Register your models here.

class LingRelationshipInline(admin.TabularInline):
    model = LingRelationship
    fk_name = 'entryRelatedTo'
    extra = 1


class LanguageDatumAdmin(admin.ModelAdmin):
    search_fields = ['normalizedEntry', 'gloss', 'annotation', 'dialect__dialectCode', 'entryTags__tagText']
    list_display = ['normalizedEntry', 'gloss', 'annotation', 'dialect', 'sourceDoc', 'sourceLocation', 'contributor']
    inlines = (LingRelationshipInline,)
    def get_queryset(self, request): #tutorials say to use function 'queryset' but that's not true, get_queryset seems to be the on that actually works
        qs = super(LanguageDatumAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs #super user can see everyone's to allow for removal of bad data
        else:
            contributor = Contributor.objects.get(user=request.user)
            qs= qs.filter(contributor=contributor) #normal users can only see their own contributions
            return qs

 #   fieldsets = (
  #      (None, {
 #           'fields': ('normalizedEntry', 'gloss', 'annotation', 'dialect', 'sourceDoc', 'sourceLocation', 'contributor', 'permissions')}),
#        ('Optional Fields', {
#            'classes' : ('collapse',),
#            'fields': ('originalOrthography', 'lingRelationship')
#                    }
#        ),
#    )
    #list_editable = ['gloss', 'annotation', 'dialect', 'sourceDoc', 'sourceLocation']
    #list_display_links = ('normalizedEntry',)

class EntryTagAdmin(admin.ModelAdmin):
    list_display = ['tagText', 'tagExplanation']

class DialectAdminForm(forms.ModelForm):
    class Meta:
        model = Dialect
        centerLoc = forms.PointField(widget=forms.OSMWidget(attrs={
            'display_raw': True}))
        fields = '__all__'

        #widgets = {
        #    'centerLoc' : widgets.GeopositionWidget #doesn't work :-(
       # }


class DialectAdmin(admin.GeoModelAdmin):
    form = DialectAdminForm

    #formfield_overrides = {models.PointField: {'widget' : widgets.GeopositionWidget}}

class RelTagsAdmin(admin.ModelAdmin): #really don't know if this is necessary
    pass

class BiblioAdmin(admin.ModelAdmin):
    pass


#This class wraps contributor
class ContribInline(admin.StackedInline):
    model = Contributor
    can_delete = False

#This class wraps User into contributor
class UserAdmin(UserAdmin):
    inlines = (ContribInline, )

#These lines should replace user with contributor
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(LanguageDatum, LanguageDatumAdmin)
admin.site.register(Dialect, admin.OSMGeoAdmin)
admin.site.register(EntryTag, EntryTagAdmin)
admin.site.register(RelateTag,RelTagsAdmin)
admin.site.register(BiblioEntryBibTex, BiblioAdmin)
