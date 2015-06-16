__author__ = 'Alex'
from django.forms import widgets
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.html import format_html

class TagAutoWidget(widgets.Textarea):
    def __init__(self, queryset,field, multi=True, attrs=None):
        super(TagAutoWidget,self).__init__(attrs)
        self.queryset = queryset
        self.queryfield = field
        self.itemlist = set()
        self.multi = multi

        for item in queryset:
            self.itemlist.add(getattr(item,field))
        self.itemlist = sorted(self.itemlist)
        #self.itemlist = set(self.itemlist) #Removes duplicates - just did a set from the start, more efficient
        self.itemlist = ",".join(self.itemlist)

    def render(self,name,value,attrs=None):
        widgetclasses = 'acwidgetmulti' if self.multi else 'acwidget'
        if attrs:
            attrs['acsource'] = self.itemlist
            attrs['class'] = widgetclasses
        else:
            attrs = {}
            attrs['acsource'] = self.itemlist
            if attrs['class']:
                attrs['class'] = attrs['class'] + " " + widgetclasses
            else:
                attrs['class'] = widgetclasses

        initialHTML = super(TagAutoWidget,self).render(name,value,attrs)
        #javascript = render_to_string('autotagwidgetJQ.html',{'widgetID':name,'widgetIDJS': str.replace(name,"-","_"), 'itemlist':self.itemlist, 'multiInput':self.multi})
       # return mark_safe(initialHTML + javascript)
        return mark_safe(initialHTML)