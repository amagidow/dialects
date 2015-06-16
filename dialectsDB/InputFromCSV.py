__author__ = 'Magidow'
# coding=UTF-8
djangoProjHome = 'C:/AlexDocs/Django/dialects'

import sys,os,codecs
import re
sys.path.append(djangoProjHome)
os.environ['DJANGO_SETTINGS_MODULE'] = 'dialects.settings'
import django
django.setup()

from django.core.exceptions import ObjectDoesNotExist
import csv
from dialectsDB.models import *

generalTagsInterrogative = ['closed-class']
generalTagsPronouns = ['closed-class','pronoun.independent']

generalTagsProSuff = ['closed-class', 'pronoun.suffix', 'justin']

#sharedHeaderColumns = ['Code', 'Bibtex Key','Date', 'Author']
sharedHeaderColumns = ['Code', 'Bibtex Key', 'Notes', 'Page']
#Using a dictionary of lists as the general construct
#Not all conversions will need multiple tags/item
conversionTagsInterrogatives = {
    'What?': ['interr.what'],
    'Who?': ['interr.who'],
    'When?': ['interr.when'],
    'Where?': ['interr.whereto'],
    'Why?': ['interr.why'],
    'Wherefrom?': ['interr.wherefrom'],
    'Whereto?': ['interr.whereto'],
    'How?': ['interr.how'],
    'How many?': ['interr.howmuch', 'interr.howmany'], #Double mark these, fix later
    'Which?': ['interr.which'],
    'Interrogative Particle': ['interr.polar']
}
interrogativeFirstDataColumn = 'What?'
interrogativeLastDataColumn = 'Partical annot'

interrogativeLocation = 'C:/AlexDocs/Django/dialects/dialectsDB/data/InterrogativeData.csv'



def ImportToDatabase(conversionTags, firstdatacolumn, lastdatacolumn, fileLocation):
    #generalHeaderDict = {}
   with open(fileLocation) as theFile:
    dataReader = csv.reader(theFile, delimiter = '|')
    entryAuthor = Contributor.objects.get(id=3) #hardcoded, but this should get my name from the database #rewrite
    permission = entryAuthor.defaultPermission
    firstrow = True
    for row in dataReader:
        if firstrow:
            header = row
            generalHeaderDict = {}
            for headercolumn in sharedHeaderColumns:
                    generalHeaderDict.update({headercolumn: header.index(headercolumn)}) #Should create something like {Code: 1}
            print(generalHeaderDict)
            firstrow = False
        else:
            dialectCode =  row[generalHeaderDict['Code']]
            bibTex = row[generalHeaderDict['Bibtex Key']]
            bibDate = row[generalHeaderDict['Date']]
            bibAuthor = row[generalHeaderDict['Author']]
            dataSlice = row[header.index(firstdatacolumn):header.index(lastdatacolumn)+1] #just the data columns, none of the 'header'
            bibSource, created = BiblioEntryBibTex.objects.get_or_create(bibTexKey = bibTex)
            pageIndex, createdagain = SourceIndex.objects.get_or_create(biblioSource = bibSource, index = 'check page or map no')
            print(dialectCode)
            dialectForRow = Dialect.objects.get(dialectCode=dialectCode) #is this legit?

            for doubletIndex in range(0, len(dataSlice), 2): #this loads every other set of rows
                datum = dataSlice[doubletIndex]
                splitData = splitDatums(datum)
                datumAnnotation = dataSlice[doubletIndex+1]
                headerIndex = header.index(firstdatacolumn)+ doubletIndex
                datumTags = conversionTags[header[headerIndex]]

                for index, item in enumerate(splitData):
                    if item != '':
                        newEntry = LanguageDatum(normalizedEntry = item, normalizationStyle = 'IPA', gloss = header[headerIndex],
                                                 annotation = datumAnnotation, permissions = 'PubNoE', source = pageIndex,
                                                 originalOrthography = '',dialect = dialectForRow, contributor = entryAuthor )

                        print('{0} {1} {2}'.format(newEntry.normalizedEntry, newEntry.gloss, newEntry.annotation))
                        #newEntry.save() #DEFANGED
                        datumTags = datumTags + generalTagsPronouns
                        for tag in datumTags:
                            try:
                                currentTag = EntryTag.objects.get(tagText=tag)
                                newEntry.entryTags.add(currentTag)
                            except ObjectDoesNotExist:
                                print('Tag doesn\'t have an entry!?!')
                            print('current tag:')
                            print(currentTag)

                        if index == 0:
                            originalForm = newEntry
                        else: #the arbitrarily 'first' element does not that a 'is a variant of' tag.
                            isRelatedToTag = RelateTag.objects.get(tagText="variant.eq")
                            isRelatedToObject = LingRelationship(entryIsRelated = newEntry,relateTag=isRelatedToTag, entryRelatedTo=originalForm)
                            isRelatedToObject.save()
                            #newEntry.lingRelationship.add(isRelatedToObject)
                            print("Non-first form")


                            #print datum
               # print splitData
                #print datumTags
            #print dialectCode + ' ' + bibTex + ' ' + dataSlice[0] + ' ' +  dataSlice[-1]



def importStructuredToDB(fileLocation, generaltags):
    #generalHeaderDict = {}
   with codecs.open(fileLocation, 'r', 'utf-8') as theFile:
    dataReader = csv.reader(theFile, delimiter = '\t')
    entryAuthor = Contributor.objects.get(id=3) #hardcoded, but this should get my name from the database #rewrite
    firstrow = True
    for row in dataReader:
        if firstrow:
            header = row
            generalHeaderDict = {} #Lets make this a dictionary of dictionaries
            dataColDict = {}
            #for headercolumn in sharedHeaderColumns:
            #    generalHeaderDict.update({headercolumn: header.index(headercolumn)}) #Should create something like {Code: 1}
            for headColumn in header:
                if headColumn in sharedHeaderColumns: #only specified header columns become main header cols
                    headDict = {'headerTitle':  headColumn, 'idx' : header.index(headColumn) }
                    generalHeaderDict.update({headColumn: headDict}) #Puts a dictionary under the entry of the name of the head column
                elif headColumn.count(":") == 2: # This is simplistic, I think I need a condition for more complex ones
                    splitHeader = headColumn.split(":")
                    headerGloss = splitHeader[0]#First part is the gloss
                    headerTags = splitHeader[1].split(",")#Second is a comma separated list of tags
                    notesIdx = splitHeader[2]#This column is the index for the purposes of
                    headDict = {'headerTitle':  headColumn, 'idx' : header.index(headColumn), 'headGloss':headerGloss,
                                'headTags' : headerTags, 'noteIdx' : notesIdx}
                    mainName = "DataCol"+ str(headDict['idx'])#####something is broken here
                    dataColDict.update({mainName: headDict})
            generalHeaderDict.update({'DataCols' : dataColDict})
            #print(generalHeaderDict)
            firstrow = False
        else:
            dialectCode =  row[generalHeaderDict['Code']['idx']]
            bibTex = row[generalHeaderDict['Bibtex Key']['idx']]
            notes = row[generalHeaderDict['Notes']['idx']].split(";") #split at ;
            pageNo = row[generalHeaderDict['Page']['idx']]
            #make a loop for notes
            notesArray = []
            for annot in notes:
                if annot != '':
                    #print(annot)
                    indexList = re.search(r"\[(.+)\]",annot)#edgecase is that there are two [] in the notes or no []
                    annotText = annot[:indexList.start()] + annot[indexList.end():] #clever way to slice out the [XXX] - fails if no [] in note
                    indexList = indexList.group(0).replace('[','').replace(']','').split(',') #clean out [], split
                    notesArray.append({'indexList' : indexList, 'annotText' : annotText})
            datacolumns = generalHeaderDict['DataCols']
            for column in datacolumns:#Iterate through data columns - this returns the string index of each column,not the column itsself
                indexHere = datacolumns[column]['idx']
                notesIndexHere = datacolumns[column]['noteIdx']
                datum = row[indexHere]
                gloss = datacolumns[column]['headGloss']
                splitData = splitDatums(datum)
                tags = datacolumns[column]['headTags']
                thisItemsNotes =[]
                for note in notesArray: #if this has a note
                    if notesIndexHere in note['indexList'] or 0 in note['indexList']:
                        thisItemsNotes.append(note['annotText'])
                thisItemsNotes= ';'.join(thisItemsNotes)

                for index, item in enumerate(splitData):
                        if item != '':
                            bibSource, created = BiblioEntryBibTex.objects.get_or_create(bibTexKey = bibTex)
                            dialect = Dialect.objects.get(dialectCode = dialectCode)
                            newEntry = LanguageDatum(normalizedEntry = item, normalizationStyle = 'IPA', gloss = gloss, #STYLE HARDCODED
                                                     annotation = thisItemsNotes, permissions = 'PubNoE', sourceLocation = pageNo,
                                                     sourceDoc = bibSource,
                                                     originalOrthography = '',dialect = dialect, contributor = entryAuthor )

                            print('{0} {1} {2} {3}'.format(newEntry.normalizedEntry, newEntry.gloss, newEntry.annotation, dialectCode))
                            newEntry.save()
                            tags = tags + generaltags
                            for tag in tags:
                                print(tag)
                                try:
                                    currentTag = EntryTag.objects.get(tagText=tag.strip())
                                    newEntry.entryTags.add(currentTag)
                                except ObjectDoesNotExist:
                                    print('Tag doesn\'t have an entry!?!')
                                    print('current tag:')
                                    print(currentTag)

                            if index == 0:
                                originalForm = newEntry
                            else: #the arbitrarily 'first' element does not that a 'is a variant of' tag.
                                isRelatedToTag = RelateTag.objects.get(tagText="variant.eq")
                                isRelatedToObject = LingRelationship(entryIsRelated = newEntry,relateTag=isRelatedToTag, entryRelatedTo=originalForm)
                                isRelatedToObject.save()
                                #newEntry.lingRelationship.add(isRelatedToObject) #UNNECESSARY, THROWS ERROR "Cannot use add() on a ManyToManyField which specifies an intermediary model"
                                #    print("Non-first form")


                            #Do stuff

            #bibDate = row[generalHeaderDict['Date']]
            #bibAuthor = row[generalHeaderDict['Author']]
            #dataSlice = row[header.index(firstdatacolumn):header.index(lastdatacolumn)+1] #just the data columns, none of the 'header'

            #bibSource, created = BiblioEntryBibTex.objects.get_or_create(bibTexKey = bibTex)


            #dialectForRow = Dialect.objects.get(dialectCode=dialectCode) #is this legit?



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
    return dataOutput



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


#newEntry = LanguageDatum(normalizedEntry = "TEST", normalizationStyle = 'IPA', gloss = "TEST", annotation = "TEST ITEM", permissions = 'PubNoE', source = pageIndex, originalOrthography = '',dialect = dialectForRow, contributor = entryAuthor )

#This is the command that runs it
#ImportToDatabase(conversionTagsInterrogatives, interrogativeFirstDataColumn, interrogativeLastDataColumn, interrogativeLocation)

#codeCheckLoc = 'D:\Dropbox\AlexDocs\Documents\Dialect Database Material\CodesCheck.csv'
def checkCodes(fileLocation):
    missingCodes = []
    with open(fileLocation) as theFile:
         dataReader = csv.reader(theFile, delimiter = ',')
         for row in dataReader:
             try:
                 Dialect.objects.get(dialectCode=row[0])
                 #nothing happens, if it exists its good
             except ObjectDoesNotExist:
                missingCodes.append(row[0])
    print(missingCodes)

#checkCodes(codeCheckLoc)

importStructuredToDB('D:\\Dropbox\\AlexDocs\\Documents\\Dialect Database Material\\prosuffixexport.csv', generalTagsProSuff)

#def LoadHeader(header):
    #returnableHeader = []
    #for item in header:


