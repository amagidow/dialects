__author__ = 'Magidow'
# coding=UTF-8
from django import forms
from django.forms import ModelForm,TextInput, Textarea,ValidationError
from dialectsDB.models import LanguageDatum, EntryTag, Dialect, LANGUAGES
from dialectsDB import mywidgets, paradigms
from dialects.settings import STATIC_URL
from django.contrib.auth.models import User
from django.contrib.admin.widgets import FilteredSelectMultiple

######################FIELDS########################
class TagField(forms.Field):
    def __init__(self,modelQS, field,attrs = None,required=False, label=None):
        self.modelQS = modelQS
        self.field =field
        super(TagField, self).__init__(required=required, widget=mywidgets.TagAutoWidget(modelQS, field, attrs=attrs), label=label)

    def to_python(self, value):
        if not value:
            return []
        returnlist = list(set(value.split(',')))#remove duplicates
        returnlist = [x.strip() for x in returnlist] #strip whitespace
        return returnlist

    def validate(self, value):
        for item in value:
            print(item)
            if self.modelQS.filter(tagText=item).exists(): #This won't work - need a get(tagText=item)
                print("Validation Worked")
                pass #all is well with the world
            else:
                print("Debug:ValidationError")
                raise ValidationError(
                    ('Non-existent tag: %(value)'),
                    params= {'value': item},
                    code='dne' #does not exist
                )


########################FORMS#####################################
class DatumBasicInfo(ModelForm): #This is just to get the basic information that will be shared on a page
    glosslang = forms.ChoiceField(choices = LANGUAGES,label="Gloss language", required=True)
    dialect = forms.ModelChoiceField(queryset = Dialect.objects.order_by("dialectCodeDisplay"))
    class Meta:
        model = LanguageDatum
        fields = ('normalizationStyle','dialect', 'sourceDoc', 'permissions')

class DatumBasicInfoPgNo(DatumBasicInfo): #Would prefer to inherit this to DRY, but it's a PITA in django
    #Glosslang isn't really used, since paradigms aren't multilingual at this point
    #glosslang = forms.ChoiceField(choices = LANGUAGES,label="Gloss language", required=True)
    dialect = forms.ModelChoiceField(queryset = Dialect.objects.order_by("dialectCodeDisplay"))
    class Meta:
        model = LanguageDatum
        fields = ('normalizationStyle','dialect', 'sourceDoc', 'sourceLocation', 'permissions')
        widgets = {
            'sourceLocation' : TextInput()
        }

class DatumIndividualInfoNoTags(ModelForm):

    class Meta:
        model = LanguageDatum
        fields = ('normalizedEntry', 'originalOrthography', 'annotation', 'sourceLocation')
        widgets = {
            'normalizedEntry': TextInput(),
            'originalOrthography': TextInput(),
            'annotation': Textarea(attrs={'cols': 60, 'rows': 2}),
            'sourceLocation': TextInput()#,
            #'entryTags' : CheckboxSelectMultiple()
        }

class DatumIndividualInfo(ModelForm):
    #itemTags = TagField(EntryTag.objects.all(),'tagText', label="Item Tags")
    entryTags = forms.ModelMultipleChoiceField(queryset=EntryTag.objects.all(),
                                          label=('Select tags'),
                                          required=False,
                                          widget=FilteredSelectMultiple(verbose_name=('Tags'), is_stacked=False))
    class Meta:
        model = LanguageDatum
        fields = ('normalizedEntry', 'originalOrthography','gloss', 'annotation', 'sourceLocation', 'entryTags')
        widgets = {
            'normalizedEntry': TextInput(),
            'gloss' : mywidgets.TagAutoWidget(LanguageDatum.glossesList(), multi=False),
            'originalOrthography': TextInput(),
            'annotation': Textarea(attrs={'cols': 60, 'rows': 1}),
            'sourceLocation': TextInput()
            #,'entryTags' : FilteredSelectMultiple(verbose_name=('Tags'), is_stacked=False)

            #'entryTags': mywidgets.TagAutoWidget(EntryTag.objects.all(), "tagText")
            #'entryTags' : CheckboxSelectMultiple()
        }

    class Media: #Media for the Filtered select multiple -USELESS. Django does not maintain the order, so JS doesn't work.
        css = {
            'all':['admin/css/widgets.css', STATIC_URL+"admin/css/forms.css" ],
        }
        #Not sure which javascript is absolutely required, taking a kitchen sink approach
        #List comprehension adds the STATIC_URL to all of these paths
        #js = ("/admin/jsi18n/", STATIC_URL+ 'admin/js/core.js', STATIC_URL+ "admin/js/jquery.js")
        #js. (STATIC_URL + x for x in ['admin/js/core.js', "admin/js/admin/RelatedObjectLookups.js",
            #  "admin/js/jquery.js", "admin/js/jquery.init.js",
             # "admin/js/actions.js", "admin/js/SelectBox.js", "admin/js/related-widget-wrapper.js", "admin/js/SelectFilter2.js"])
        #js = tuple(js)
        #print(js)
        #js.append("/admin/jsi18n/") #Not under /static/


class SearchForm(ModelForm):
    wordSearch = forms.CharField(required=False, label='Regex Search of Words')
    glossSearch = forms.CharField(required=False, label='Regex Search of Gloss')
    annotationSearch = forms.CharField(required=False, label='Regex Search of Annotations')

    class Meta:
        model = LanguageDatum
        fields = ('entryTags',)

       # wordSearch = forms.Charfield(label = 'Regex Search of Words')
       # annotationSearch = forms.TextInput(label = 'Regex Search of Annotations')
        widgets = {
            'normalizedEntry': TextInput(),
            'annotation': TextInput()
        }


class LoginForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')


class NonModelSearchForm(forms.Form):
    wordSearch = forms.CharField(required=False, label='Arabic Word')
    #Queryset argument can be any iterable if no field is defined, so I'll just pass a list of all glosses to solve the 'multigloss' problem
    glossSearch = forms.CharField(required=False, label='Gloss',
                                  widget=mywidgets.TagAutoWidget(LanguageDatum.glossesList(), multi=False,attrs={'cols': 15, 'rows': 1}))
    annotationSearch = forms.CharField(required=False, label='Annotations')
    #tagSearch = forms.CharField(required=False, label='Tags, comma split')
    tagSearch = forms.CharField(required=False, label='Tags, comma split', widget=mywidgets.TagAutoWidget(EntryTag.objects.all(), "tagText", attrs={'cols': 30, 'rows': 1}))


class NonModelSearchFormColor(NonModelSearchForm):
        colorinput = forms.ChoiceField(choices=(
            ("Red", "Red"),
            ('Yellow', "Yellow"),
            ('Blue', "Blue"),
            ('Green', "Green"),
            ("Orange", "Orange"),
            ('Black', 'Black'),
            ('White', "White")
        ), label="Marker Color" )

#class InterrogativeForm()

#            ('FFFF00', "Yellow"),
            #('0000FF', "Blue"),
            #('008000', "Green"),
            #('000000', 'Black')
class ParadigmSearchForm(forms.Form):
    #def __init__(self):

    paradigmlist = [(key, paradigms.paradigmDict[key].paradigmname) for key in paradigms.paradigmDict]
    #print("paradigm list:{}".format(paradigmlist))
    #    super().__init__()
    paradigm = forms.ChoiceField(choices=paradigmlist, label="Paradigm")
    dialectSearch = forms.CharField(required=True, label='Dialects, comma split', widget=mywidgets.TagAutoWidget(Dialect.objects.all(), "dialectCodeDisplay", attrs={'cols': 40, 'rows': 3}), )





