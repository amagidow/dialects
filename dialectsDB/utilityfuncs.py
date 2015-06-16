__author__ = 'Magidow'
from django.core.exceptions import ObjectDoesNotExist
from dialectsDB.models import *
from itertools import groupby
import geojson
from colour import *

def mergeObjectProperties(objectToMergeFrom, objectToMergeTo):
    """
    Used to copy properties from one object to another if there isn't a naming conflict;
    """
    for property in objectToMergeFrom.__dict__:
        #Check to make sure it can't be called... ie a method.
        #Also make sure the objectobjectToMergeTo doesn't have a property of the same name.
        if not callable(objectToMergeFrom.__dict__[property]) and not hasattr(objectToMergeTo, property):
            setattr(objectToMergeTo, property, getattr(objectToMergeFrom, property))

    return objectToMergeTo


def splitDatums(datumInput):
    #Need to split my idiosyncratically entered data
    #e.g. ʃ(u)-/(w)eːʃ - needs to become four items: ʃ- ʃu- weːʃ eːʃ
    #or: (ha)ðoːl(a) needs to become four items hadol, hadola, dol, dola
    #or: ti(y(ya)) needs to become ti, tiy, tiyya <- this is too difficult, just remove nested parens in the data
    #First, split along / marks:
    splitOnSlashes = datumInput.split('/')
    dataOutput = []
    for item in splitOnSlashes:
        dataOutput = dataOutput + parse_string(item)
    return dataOutput #This returns a list



def parse_string(st): #from Yonatan, test this out
    inside = False
    cur_opt = ''
    variants = ['']
    for c in st:
        if c == '(':
            inside = True
        elif c == ')':
            inside = False
            variants = variants + [v + cur_opt for v in variants]
            cur_opt = ''
        elif inside:
            cur_opt += c
        else:
            variants = [v + c for v in variants]
    return variants

def datumsToObjs(genericInfo, datumsList): #generic info is a LanguageDatume object, datumsDict is my own dictionary
    for item in datumsList:
        newObject = LanguageDatum()
        #These are all the basic pieces of information derived from the model form
        newObject.dialect = genericInfo.dialect
        newObject.normalizationStyle = genericInfo.normalizationStyle
        newObject.dialect = genericInfo.dialect
        newObject.sourceDoc = genericInfo.sourceDoc
        newObject.contributor = genericInfo.contributor
        newObject.permissions = genericInfo.permissions
        newObject.sourceLocation = genericInfo.sourceLocation
       # item = datumsList[item] #this should just give me the entire subdict
        newObject.normalizedEntry = item['datum'] #each item is itself a dictionary
        newObject.annotation = item['annotation']
        newObject.gloss = item['gloss']
        newObject.save()
        #probably need to save here for it to work in the tags section below
        #also, need to have relationships
        tags = item['tags']
        for tag in tags:
            addTagstoLanguageDatum(newObject,tags)
        item["object"] = newObject #once the object is created, add it back into the data structure so I can use it
    for itemagain in datumsList: #this is inefficient perhaps, but must wait till all objects created
        if "relationship" in itemagain:
            relTarget = itemagain["relationship"]["target"]
            relTag = itemagain["relationship"]["reltag"]
            #relatedObjects = (relObj["object"] for relOjb in datumsList if relOjb["orighead"] is relTarget) #I'm not even relating this to a real object
            relatedObjects = []
            for findObj in datumsList:
                if findObj["orighead"] == relTarget:
                    relatedObjects.append(findObj["object"])
            for obj in relatedObjects:
                try:
                    isRelatedToTag = RelateTag.objects.get(tagText=relTag)
                    isRelatedToObject = LingRelationship(entryIsRelated = itemagain["object"],relateTag=isRelatedToTag, entryRelatedTo=obj)
                    isRelatedToObject.save()
                except ObjectDoesNotExist:
                    print('Tag doesn\'t have an entry!?!')
                    print('current tag:')
                    print(relTag)



def addTagstoLanguageDatum(languagedatum,tags): #tags is a list
    for tag in tags:
            try:
                currentTag = EntryTag.objects.get(tagText=tag.strip())
                languagedatum.entryTags.add(currentTag)
            except ObjectDoesNotExist:
                print('Tag doesn\'t have an entry!?!')
                print('current tag:')
                print(tag.strip())



    ####SPECIFICATION FOR FORMAT FOR INPUT BOX IDs#####
    #Gloss information is as Gloss:TAGS
    #Tags separated by _
    #Relationship information is included before a >, relatedHeader>relationshipType|GlossForDatum:Tags
    # annotation| -> following the pipe is the related column, e.g annotation|Gloss
    #For relationship columns, the annotation column would be annotation|relatedHeader>relationship|gloss:tags_separated_by_underscores
    #relationship should look like: header>relationship| - but we could have identical glosses, e.g. -ii, -ya
    #The nature of the relationship could just be whatever is before the | separated by _ ??
def processInputForm(sharedTags, querydata):
    combinedDict = []
    for key, value in querydata.items():
        if "*" in key and "annotation" not in key: #asterisks skip data from other forms!
            if value: #this sufficient to check a blank string
                key = key.replace("*","") #strip out extra asterisk
                if "|" in key:
                    relationshipPart = key.split("|")[0] #everything before | is about relationships
                    headerRelated = relationshipPart.split(">")[0] # before > is the header for the related object
                    relationship = relationshipPart.split(">") [1] # after > is relationship itself
                    headerpart = key.split("|")[1]
                    firstsplit = headerpart.split(":")
                    gloss = firstsplit[0]
                    individualTags = firstsplit[1].split("_")
                    alltags = sharedTags + individualTags
                    annotation = querydata.get("*annotation|"+key, "") #this works, what about variants?
                    value = splitDatums(value) #should return just a single item if there's no annotation
                    for singleDatum in value: #loops through
                        datumDict = {"datum" : singleDatum, "annotation" : annotation, "gloss" : gloss, "tags" : alltags,
                                 "relationship" : {"target" : headerRelated, "reltag" : relationship}, "orighead": key}
                        combinedDict.append(datumDict)
                else:
                    firstsplit = key.split(":")
                    gloss =  firstsplit[0] #this allows me to run through this even if it's only one
                    value = splitDatums(value)
                    individualTags = firstsplit[1].split("_")
                    alltags = sharedTags + individualTags
                    annotation = querydata.get("*annotation|"+key, "") #this works, what about variants?
                    for singleDatum in value:
                        datumDict = {"datum" : singleDatum, "annotation" : annotation, "gloss" : gloss, "tags" : alltags, "orighead":key}
                        combinedDict.append(datumDict)
    return combinedDict

class MarkerInfo():#Class for storing information for markers
    def __init__(self,location,entry,entrygloss,dialectname, sourcedoc,color,sourceloc = None, annotation=None, contributor = None, tags = None):
        self.geomLat = location.get_coords()[1] #have to extract out of this cause my life sucks
        self.geomLong = location.get_coords()[0]
        self.location = geojson.Point((self.geomLong, self.geomLat))
        self.entry = entry #the actual Arabic data
        self.entrygloss = entrygloss
        self.dialectname = dialectname
        self.intsourcedoc = sourcedoc
        self.intsourceloc = sourceloc
        self.intcolor = Color(color).get_hex_l() #internal color - passed in as English
        self.annotation = annotation
        self.contributor = contributor
        self.tags = tags
        #self.hexcolor = Color(self.intcolor).get_hex_l().replace("#","")
        extrainfotitle = '"Annotation: {} ; Tags: {} ; Contributor: {}"'.format(annotation,self.commatags, contributor)
        self.popupstring = r'<p title = {} style="border-style:solid; border-width:3px; border-color:{};"><i>{}</i>, "{}" <br> <b>{}</b>, {} </p>'.format(extrainfotitle,self.color,self.entry, self.entrygloss, self.dialectname, self.intsourcedoc)

    def appendpopup(self, newstring):
        self.popupstring += newstring
        return self.popupstring

    @property
    def sourcedoc(self):
        if self.intsourceloc:
            return "{}: {}".format(str(self.intsourcedoc), self.intsourceloc) #This works great, but the data sucks -change the popupstring above to fix this
        else:
            return str(self.intsourcedoc)

    @property
    def popupinfo(self):
        return self.popupstring

    @property
    def color(self): #returns the hex color no hash mark
        return self.intcolor

    @color.setter
    def color(self,newcolor):
        self.intcolor = newcolor

    @property
    def colorname(self):
        return hex2web(self.intcolor) #This will no longer be accurate once color is changed

    @property
    def commatags(self):
        taglist = [str(x) for x in self.tags]
        return ", ".join(taglist)


    @property
    def geoJson(self):
        return {'type': 'Feature',
        'properties':
            {
                'popupinfo':self.popupinfo,
                'color' : self.color
            },
        'coordinates': {"type": "Point", "coordinates": [self.geomLong,self.geomLat]}}

    @property
    def __geo_interface__(self):
        return geojson.Feature(geometry=self.location,properties={'color':self.color, 'popupinfo': self.popupinfo})
        #{'type': 'Feature',
               # 'properties':
               #     {
               #         'popupinfo':self.popupinfo,
               #         'color' : self.color
               #     },
               # 'geometry': geojson.dumps(self.location)}
    @property
    def dtarray(self): #returns list
        return [self.entry,self.entrygloss,self.annotation,self.dialectname, self.commatags, self.sourcedoc,self.colorname]

    @property
    def csvserialized(self): #returns one line of a CSV
        return "{},{},{},{}".format(self.dialectname, self.color, self.geomLat, self.geomLong)

def searchText(request):
    wordSearchText = request['wordSearch']
    glossSearchText = request['glossSearch']
    annotSearchText = request['annotationSearch']
    tagSearchText = None or request['tagSearch']
    return "Aw: {} G: {} An: {} T: {}".format(wordSearchText,glossSearchText,annotSearchText,tagSearchText)

def searchLanguageDatum(request):
    queryToReturn = LanguageDatum.objects.exclude(permissions="Private") #ensures that private records are not show, test this!
    wordSearchText = request['wordSearch']
    glossSearchText = request['glossSearch']
    annotSearchText = request['annotationSearch']
    tagSearchText = None or request['tagSearch']
    #no idea how to handle tags just yet
    if wordSearchText:
        queryToReturn = queryToReturn.filter(normalizedEntry__regex=wordSearchText)
    if glossSearchText:
        queryToReturn = queryToReturn.filter(gloss__contains=glossSearchText) #NO LONGER REGEX SEARCH!
    if annotSearchText:
        queryToReturn = queryToReturn.filter(annotation__regex=annotSearchText)
    if tagSearchText:
        tokenizedSearchText = tagSearchText.split(",")
        tokenizedSearchText = filter(None,tokenizedSearchText)
        for queryItem in tokenizedSearchText:
            queryItem = queryItem.strip()
            queryToReturn = queryToReturn.distinct().filter(entryTags__tagText__contains=queryItem)#can't be regex b/c of periods in tags
    return queryToReturn

def searchLanguageDatumColor(request): #Utility function to process a request based on the search bar
    color = request['colorinput']
    queryToReturn = searchLanguageDatum(request)
    return (queryToReturn, color) #returns a tuple with the query and the expected color


def generateMarkers(queryset):#Takes a tuple of (queryset,color) of language datums and returns a list of MakerInfo objects
    objectlist = []
    for item in queryset[0]:
        newObject = MarkerInfo(location=item.dialect.centerLoc,entry=item.normalizedEntry,entrygloss=item.gloss,dialectname=item.dialect.dialectCode,sourcedoc=item.sourceDoc,sourceloc=item.sourceLocation,color=queryset[1], contributor=str(item.contributor), annotation=item.annotation, tags=item.entryTags.all())
        #print(newObject)
        objectlist.append(newObject)
    return objectlist

def cleanupMarkers(markers):
    newobjectlist = []
    markers.sort(key=lambda obj: obj.dialectname)
    for key, group in groupby(markers, lambda x: x.dialectname):
        #key should equal the shared location, group is an iterable of all the members of that location
        first = True
        mainMember = None
        collectedcolors = set()
        for member in group:
            if first == True:
                mainMember = member
                collectedcolors.add(member.colorname)
                #print("First member is: {} in dialect".format(member.entry.encode('ascii', errors='backslashreplace')),member.dialectname)
                first = False
            else:
                #print("Non-first member is: {} in dialect".format(member.entry.encode('ascii', errors='backslashreplace')),member.dialectname)
                mainMember.appendpopup(member.popupinfo)
                collectedcolors.add(member.colorname)
                #print("Mainmember pop reads: ")
            if len(collectedcolors) > 1:
                ravg = 0
                gavg = 0
                bavg = 0
                for item in collectedcolors:
                    ravg += float(Color(item).get_red())
                    gavg += float(Color(item).get_green())
                    bavg += float(Color(item).get_blue())
                mainMember.color = Color(rgb=(ravg/len(collectedcolors),gavg/len(collectedcolors),bavg/len(collectedcolors))).get_hex_l()
                #Do something to blend colors
            newobjectlist.append(mainMember) #once we have its info, we cut it out
    #print(newobjectlist)
    return newobjectlist
        #Need to append all the data from duplicates to the properties of the first one

def removeJustIntag():
    justintag = EntryTag.objects.get(tagText="justin")
    taggedItems = LanguageDatum.objects.filter(entryTags=justintag)
    for item in taggedItems:
        item.entryTags.remove(justintag)


#This function wraps a called to LanguageDatum.objects.all() in such a way that it correctly handles permissions
#Only handles whether something can be displayed, not for export
#If contributor is not defined, it only export
def permissionwrapperdisplay(contrib=None):
    if contrib:
        #Second clause should get even stuff that is private
        queryreturn = LanguageDatum.objects.filter(permissions__contains="pub") | LanguageDatum.objects.filter(contributor=contrib)
        #This will have duplicates, handle later
        #queryreturn = queryreturn.distinct()
    else:
        queryreturn = LanguageDatum.objects.filter(permissions__contains="pub")
    return queryreturn




