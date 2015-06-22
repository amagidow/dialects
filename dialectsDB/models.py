__author__ = 'Magidow'
# coding=UTF-8
#from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models  #I think this makes django.db unnecessary
from django.contrib.postgres.fields import HStoreField
import collections



#from django.contrib.auth import models
NORM_STYLES = (
    ('IPA', 'International Phonetic Alphabet'),#Alex uses IPA for his data input, like raised pharyngeals for emphatics
    ('BnW', 'Arabist Transcription from WAD'), #B&W use Arabist conventions like underdots
    ('BW', 'Buckwalter') #Buckwalter standard among NLP
)

LANGUAGES = (
    ('en', 'English'),
    ('fr', 'French'),
    ('de', 'German')
)

class LanguageDatum(models.Model):

    normalizedEntry = models.TextField("arabic language entry in normalized roman format")
    normalizationStyle = models.CharField(max_length = 5, choices=NORM_STYLES)
    originalOrthography = models.TextField("arabic language entry in the original orthography in the source", blank=True)
    gloss = models.TextField("brief translation of entry")
    multigloss = HStoreField("multi-lingual gloss")
    annotation = models.TextField("additional information on the entry", blank=True)
    lingRelationship = models.ManyToManyField('self', through='LingRelationship', blank=True, symmetrical=False, related_name='relationships')
    entryTags = models.ManyToManyField('EntryTag',blank=True, null=True)
    dialect = models.ForeignKey('Dialect')
    #source = models.ForeignKey('SourceIndex')#This is too normalized and annoying to deal with, replaced it with direct fields below
    sourceDoc = models.ForeignKey('BiblioEntryBibTex', null=True)
    sourceLocation = models.TextField('location of datum in page or map number (p. or m. XX)', null=True)
    contributor = models.ForeignKey('Contributor') #once logged in, all activity will be related to contributors, or when data is imported.
    PERMISSION_TYPES = (
        ('Public', 'Fully public'),
        ('PubNoE', 'Public no export'),
        ('Private', 'Private, viewable only by uploader'),
    )
    permissions = models.CharField(max_length=8, choices=PERMISSION_TYPES)
    def __str__(self):
        displayDialectCode = str(self.dialect.dialectCode)
        return ", ".join([self.normalizedEntry, self.glossesString(), displayDialectCode, self.annotation])

    def myserializer(self):  #for the moment, just using this for important stuff, not every single column
        dialectName = str(self.dialect.dialectCode)
        dialectCoordsX = self.dialect.centerLoc.coords[0]
        dialectCoordsY = self.dialect.centerLoc.coords[1]
        sourceName = self.sourceDoc.bibTexKey
        sourceLoc = self.sourceLocation
        #tagsListObj = EntryTag.objects.filter(LanguageDatum=self)
        tagsListObj = self.entryTags.all()
        tagsListArray = []
        tagsListStr = ','
        for tag in tagsListObj:
            tagsListArray.append(tag.tagText)
        tagsListStr = ','.join(tagsListArray)

        lingRelats = LingRelationship.objects.filter(entryIsRelated=self)
        lingRelatsArr = []
        lingRelatStr = ''
        for rel in lingRelats:
            lingRelatsArr.append(rel.outBoundStr())
            #lingRelatStr += rel.outBoundStr()
        lingRelatStr = ','.join(lingRelatsArr)

        serializerReturn = collections.OrderedDict([
            ('id', str(self.id)),
            ('normEntry' , str(self.normalizedEntry)),
            ('gloss' , self.gloss),
            ('annotation' , self.annotation),
            ('dialectName' , dialectName),
            ('lat' , dialectCoordsY),
            ('long' , dialectCoordsX),
            ('sourceName' , sourceName),
            ('sourceLoc' , sourceLoc),
            ('tagsList' , tagsListStr),
            ('relations',lingRelatStr)
        ])
        #TSVreturn = "\t".join("{}".format(v) for (k,v) in serializerReturn.items)
        return serializerReturn

    def TSVserializer(self): #returns a dictionary
        serialData = self.myserializer()
       # print(serialData)
        tabChar = "\t"
        tabChar.join(serialData)
        returnData = "|".join("{}".format(v) for (k,v) in serialData.items())#Tab not working
        headerReturn = "|".join("{}".format(k) for (k,v) in serialData.items())
        toReturn = {'returnData': returnData, 'header' : headerReturn}
        return returnData

    def TSVheader(self):
        serialData = self.myserializer()
        headerReturn = "|".join("{}".format(k) for (k,v) in serialData.items())
        return headerReturn

    #wraps Multigloss so that you can easily get a string with the glosses, sorted in order by language but only
    #returns the glosses themselves, not the language tag, e.g. "wo?, where?, ou?"
    def glossesString(self):
        #first sort order by key so that glosses always show in the same order
        glossitems = collections.OrderedDict(sorted(self.multigloss.items(), key = lambda t : t[0])) #copied from python docs
        #pull out only the values
        glosslist = [y for x,y in glossitems.items()]
        return ", ".join(glosslist)

    #retrieves a list of all glosses
    @staticmethod
    def glossesList():
        allLanguageDatums = LanguageDatum.objects.all() #note no permissions here
        glosslist = []
        for item in allLanguageDatums:
            for key, value in item.multigloss.items():
                glosslist.append(value)
        return glosslist

    class Meta:
        app_label = 'dialectsDB' #these have to be here

class Contributor(models.Model):
    user = models.OneToOneField(User)
    blurb = models.CharField(max_length=500, blank=True)
    affiliation = models.CharField("academic affiliation",max_length=200, blank=True)
    webaddress = models.URLField("academic website", blank=True)
    physicalAddress = models.CharField("physical academic address",max_length=500, blank=True)
    defaultPermission = models.CharField("default permission setting for data input",max_length=8, choices=LanguageDatum.PERMISSION_TYPES)
    defaultEncoding = models.CharField("default transliteration style", max_length = 5, choices=NORM_STYLES)
    defaultLanguage = models.CharField("default language used for glosses", max_length = 5, choices=LANGUAGES)
    class Meta:
        app_label = 'dialectsDB'
    def __str__(self):
        return self.user.__str__()

class Dialect(models.Model):
    dialectCode = models.CharField("short code for location", max_length=10, unique=True, primary_key=True)
    dialectNameEn = models.TextField("human readable name of the dialect")
    dialectTag = models.ManyToManyField('DialectTag',blank=True, null=True)
    #dialectGroup = models.TextField("name of the type of group, e.g. Tribe.XXX, Sect.Shii", blank=True) #We'll use MainThing.Subthing terminology throughout
    #dialectLocation = models.ForeignKey('Location')
    #No need to normalize out location at this point - the overlap of two dialects in one specific location can be dealt with via cut and paste, too much of an edge case
    locationName = models.TextField("human readable location name", blank=True)
    locationNameAr = models.TextField("Arabic name of location if available", blank=True)
    centerLoc = models.PointField("a point representing this dialect", srid=4326)
    #centerLat = models.FloatField("Latitude of center", blank=True, null=True)
   #centerLong = models.FloatField("Longitude of center",  blank=True, null=True)
    regionLoc = models.MultiPolygonField("multipolygon geometry", blank=True,  null=True) #optional regional info
    objects = models.GeoManager()
    def __str__(self):
        return self.dialectCode
    #def save(self, *args, **kwargs):
    #    self.centerLoc = Point(self.centerLong, self.centerLat)
    #    super().save(*args, **kwargs)
    class Meta:
        app_label = 'dialectsDB'
        ordering = ['dialectCode']

#class Location(models.Model): #This needs to be polymorphic to support the different kinds of geometry we'll be using.
  #  LOC_TYPE = (
   #     ('Country', 'Country'),
    #    ('City', 'City'),
     #   ('Region', 'Region'), #Region is a unit that can be larger or smaller than a country, but is just a geographical expanse that does not necessarily match the boundaries of a country
   # ) #Not sure if I really need tuples?
   # locationName = models.TextField("human readable location name")
  #  centerLoc = models.PointField("point geometry")
  #  regionLoc = models.MultiPolygonField("multipolygon geometry", blank=True) #optional regional info
 #   locationType = models.CharField("type of location", max_length=10)
# objects = models.GeoManager()

#class LocationCity(Location):
   # locGeometry = models.PointField("point geometry") #Hope this stores lat long and can store points

#class LocationRegion(Location):
   # locGeometry = models.MultiPolygonField("multipolygon geometry")




class LingRelationship(models.Model):
    entryIsRelated = models.ForeignKey('LanguageDatum', related_name='+')
    relateTag = models.ForeignKey('RelateTag')
    entryRelatedTo = models.ForeignKey('LanguageDatum', related_name='+')
    def __str__(self):
        return self.entryIsRelated.normalizedEntry + " is a "  + self.relateTag.tagText + " of " +  self.entryRelatedTo.normalizedEntry
        #return self.relateTag.tagText
    def outBoundStr(self):
        return self.relateTag.tagText + ":" +  str(self.entryRelatedTo.id)
    class Meta:
        app_label = 'dialectsDB'

class AbstractTag(models.Model):
    tagText = models.CharField("Tag: Tags may have parts separated by . or -, but not _", max_length=50, unique=True) #Need to add a validator to restrict use of underscores
    tagExplanation = models.TextField("Tag Explanation")
    class Meta:
        abstract = True
        app_label = 'dialectsDB'
        ordering = ['tagText']
    def __str__(self):
        return self.tagText


class EntryTag(AbstractTag):
    class Meta:
        abstract= False
        app_label = 'dialectsDB'
        ordering = ['tagText']

class RelateTag(AbstractTag):
    class Meta:
        abstract= False
        app_label = 'dialectsDB'
    def __str__(self):
        return self.tagText

class DialectTag(AbstractTag):
    class Meta:
        abstract= False
        app_label = 'dialectsDB'

#class SourceIndex(models.Model): #This class is probably a bit too much normalization, but eh
    #bibliosource should be a polymorphic relationship, so ANY type of bibliographic field will be appropriate
#    biblioSource = models.ForeignKey('BiblioEntryBibTex')
#    index = models.TextField("page or map numbers") #where in the source this is found
#    class Meta:
 #       app_label = 'dialectsDB'


class BiblioEntryBibTex(models.Model): #Apparently cannot be abstract, but leaving its name to emphasize that it shouldn't be used
    bibTexKey = models.CharField(max_length=50, unique=True)
    date = models.SmallIntegerField(max_length=4, blank=True, null=True) #not the most elegant solution, but we don't need full date fields
    author = models.TextField("author(s), multiple names separated by ;", blank=True)
    title = models.TextField("Optionally include title of work", blank=True)
    annotation = models.TextField("additional annotations", blank=True)
    fullBibtex = models.TextField("Full Bibtex entry", blank=True)
    class Meta:
        app_label = 'dialectsDB'
        ordering = ['bibTexKey']
    def __str__(self):
        return self.bibTexKey
   # class Meta:
      #  abstract = True

#class JournalArticle(BiblioEntryAbstract):
    #articleTitle = models.TextField("title of article")
    #journalTitle = models.TextField("full title of journal")
    #volumeNo = models.PositiveSmallIntegerField("volume number")
    #issueNo = models.PositiveSmallIntegerField("issue number", blank=True, null=True)
    #pages = models.CharField("page numbers of article",max_length=15) #Actual max length probably like 10: XXXX--YYYY

#class Book(BiblioEntryAbstract):
 #   title = models.TextField("book title")
  #  publisher = models.TextField("publisher name")
   # address = models.TextField("publisher address")

#class InBook(BiblioEntryAbstract):
 #   articleTitle = models.TextField("article title")
  #  bookTitle = models.TextField("volume title")
   # editor = models.TextField("editor(s), multiple names separated by ;")
    #publisher = models.TextField("publisher name")
    #address = models.TextField("publisher address")
    #pages = models.CharField("page numbers of article",max_length=15) #Actual max length probably like 10: XXXX--YYYY

#class WebsiteBib(BiblioEntryAbstract):
 #   websiteTitle = models.TextField("website title")
  #  websiteURL = models.URLField("website address")
   # dateRetrieved = models.DateField("retrieval date")

#class ElicitedData(BiblioEntryAbstract):
#Not sure what data exactly needs to be included here, but it is a possibility

