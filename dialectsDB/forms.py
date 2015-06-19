__author__ = 'Magidow'
# coding=UTF-8
from django import forms
from django.forms import ModelForm,TextInput, Textarea,ValidationError
from dialectsDB.models import LanguageDatum, EntryTag, Dialect
from dialectsDB import mywidgets, paradigms
from django.contrib.auth.models import User


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

    class Meta:
        model = LanguageDatum
        fields = ('normalizationStyle','dialect', 'sourceDoc', 'permissions')

class DatumBasicInfoPgNo(ModelForm): #This is just to get the basic information that will be shared on a page

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
    itemTags = TagField(EntryTag.objects.all(),'tagText', label="Item Tags")
    class Meta:
        model = LanguageDatum
        fields = ('normalizedEntry', 'originalOrthography','gloss', 'annotation', 'sourceLocation')
        widgets = {
            'normalizedEntry': TextInput(),
            'gloss' : mywidgets.TagAutoWidget(LanguageDatum.objects.all(),"gloss", multi=False),
            'originalOrthography': TextInput(),
            'annotation': Textarea(attrs={'cols': 60, 'rows': 1}),
            'sourceLocation': TextInput()#,
            #'entryTags': mywidgets.TagAutoWidget(EntryTag.objects.all(), "tagText")
            #'entryTags' : CheckboxSelectMultiple()
        }

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
    glossSearch = forms.CharField(required=False, label='Gloss', widget=mywidgets.TagAutoWidget(LanguageDatum.objects.all(),"gloss", multi=False,attrs={'cols': 15, 'rows': 1}))
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
    dialectSearch = forms.CharField(required=True, label='Dialects, comma split', widget=mywidgets.TagAutoWidget(Dialect.objects.all(), "dialectCode", attrs={'cols': 40, 'rows': 3}), )




