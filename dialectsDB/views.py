from django.shortcuts import render, render_to_response
from django.forms.models import modelformset_factory, formset_factory
from django.contrib.gis.shortcuts import render_to_kml
from django.http import HttpResponseRedirect
from dialectsDB.models import *
from dialectsDB.forms import *
from django.views.generic import ListView
from dialectsDB.utilityfuncs import *
from dialectsDB.paradigms import *
from itertools import groupby
import json


def map_search(request):
     return render_to_response('mapSearch.html')

def dtview(request):
    return render(request,"DTview.html", {"pageTitle": "Datatables view of data"} )

def table_view(request):
    #just all data right now
    data = LanguageDatum.objects.all()
    return render_to_response('tableView.html', {'object_list' : data, 'pageTitle' : "Table View of Data"})

class TableView(ListView):
    model = LanguageDatum
    def get_queryset(self):
        queryToReturn = searchLanguageDatum(self.request)
        return queryToReturn

def search_List(request):
    form = NonModelSearchForm()
    return render_to_response('searchTemp.html', {'pageTitle':"List-Style Search Page" ,'targetPage' : "/tableDJ", 'initialSource': "/tableDJ", 'searchForm' : form })

def search_Map2(request): #renders a search to leafletmap
    form = NonModelSearchFormColor()
    return render_to_response('searchTemp.html', {'pageTitle':"Map-Style Search Page", 'targetPage' : "/leafletmap", 'initialSource': "/map", 'searchForm' : form })

def search_Map_Comp(request):
    form = NonModelSearchForm()
    return render_to_response('searchTemp.html', {'pageTitle':"Map-Style Search Page", 'targetPage' : "/mapSearchComp", 'initialSource': "/map", 'searchForm' : form })

#Basic free input form view and validation
def inputForm(request,numSets=1): #default is one, but can be sent more
    numSets = int(numSets) #didn't know I have to cast this, but apparently I do, otherwise it throws an error
    datumForms = formset_factory(DatumIndividualInfo, extra=numSets)
    if request.method == 'POST':#validate
        dialectForm = DatumBasicInfo(request.POST) #dialectForm holds the basic dialect information
        datumForms = datumForms(request.POST, request.FILES)
        initialObject = LanguageDatum()
        finalObjectList = []
        if dialectForm.is_valid():
            initialObject = dialectForm.save(commit=False)
            print("DialectForm: Valid")
            #print(deliberatelybreakingit)
            if datumForms.is_valid():
                print("DatumForm:Valid")
                for form in datumForms:
                    finalObject = form.save(commit=False)
                    finalObject.normalizationStyle = initialObject.normalizationStyle
                    finalObject.dialect = initialObject.dialect
                    finalObject.sourceDoc = initialObject.sourceDoc
                    finalObject.contributor = initialObject.contributor
                    finalObject.permissions = initialObject.permissions
                    tags = form.cleaned_data['itemTags']
                    print(tags)
                    #finalObject =  mergeObjectProperties(initialObject,finalObject) #I think this is where it is failing
                    finalObject.save()
                    addTagstoLanguageDatum(finalObject,tags)
                    form.save_m2m() #THE FORM SAVES THE M2M relationship!
                    finalObjectList.append(finalObject)
            return render(request, 'tableView.html', {'object_list' : finalObjectList})
        #datumForms = datumForms(request.GET) saw this in a tutorial, no idea what it means
        #test
       # pass
        return render(request, 'inputForm.html',{'pageTitle': "Single Dialect Multi-Datum Input Form", 'paradigmDict': paradigmDict.items(),  'dialectForm' : dialectForm, 'dataFormset': datumForms})
    else:
        dialectForm = DatumBasicInfo()
        #datumForms = formset_factory(DatumIndividualInfo, extra=numSets)
        return render(request, 'inputForm.html',{'pageTitle': "Single Dialect Multi-Datum Input Form", 'paradigmDict': paradigmDict.items(), 'dialectForm' : dialectForm, 'dataFormset': datumForms})


def searchMulti(request, numSets=1):
    numSets = int(numSets)
    searchForms = formset_factory(NonModelSearchFormColor, extra=numSets)
    searchquery = ''
    searchQuery = ''
    if request.method == "POST":
        searchresults = searchForms(request.POST, request.FILES)
        request.session['geojson'] = 'GotToPost'
        if searchresults.is_valid():
            formResults = []
            markers = []
            #print(searchresults)
            for form in searchresults:
                #iterate through forms
                formTuple = searchLanguageDatumColor(form.cleaned_data)#This no longer works
                wordSearchText = form.cleaned_data['wordSearch']
                glossSearchText = form.cleaned_data['glossSearch']
                annotSearchText = form.cleaned_data['annotationSearch']
                tagSearchText = form.cleaned_data['tagSearch']
                color = form.cleaned_data['colorinput']
                searchQuery += "Color: {} Word: {} Gloss: {} Annotation:{} Tags: {}\n".format(
                    color, wordSearchText, glossSearchText, annotSearchText, tagSearchText)
                #print("FormTuple:{}".format(formTuple))
                formResults.append(formTuple)
            searchquery = searchQuery
            formResults.sort(key=lambda x: x[1])
            for key, group in groupby(formResults, lambda x: x[1]):
                #print("Key: {}, Group:{}".format(key,group))
                groupcolor = key #I think this is right
                finalqueryset = None
                first = True
                print("Group:{})".format(group))
                for member in group:
                    #print(member)
                    if first == True:
                        finalqueryset = member[0] #fill first member
                        #print("Queryset:{}".format(finalqueryset))
                        first = False
                    else:
                        print("Finalquery set {}".format(finalqueryset.encode('ascii', errors='backslashreplace')))
                        finalqueryset = finalqueryset & member[0]

                    markers += generateMarkers((finalqueryset,groupcolor))
            #print("Markers: {}".format(markers))
            #print(finalqueryset)
            serialized = []
            markers = cleanupMarkers(markers)
            for myobject in markers:
                serialized.append(geojson.dumps(myobject))
            serialized = ",".join(serialized)
            #print(serialized)
            request.session['geojson'] = serialized
        return render(request, 'searchMulti.html', {'pageTitle': 'Map search', 'paradigmDict': paradigmDict.items(),  'dataFormset': searchForms, 'targetPage' : "/leafletmap/", 'initialSource': "/leafletmap/"})
    else:
        request.session['geojson'] = ""
        searchForms = formset_factory(NonModelSearchFormColor, extra=numSets,)
        return render(request, 'searchMulti.html', {'pageTitle': 'Map search', 'paradigmDict': paradigmDict.items(),  'dataFormset': searchForms, 'targetPage' : "/leafletmap/", 'initialSource': "/leafletmap/"})


def searchMultiType(request, type="map"):
    numSets = 1
    searchForms = formset_factory(NonModelSearchFormColor)
    searchquery = ''
    results = ''
    targetpage = ""
    pagetitle = ""
    results = ''
    if type == "map":
        targetPage = "/leafletmap/"
        pagetitle = "Map Search"
        csvLink = "/mapcsv/"
    elif type == "list":
        targetPage = "/tableview/"
        pagetitle = "List Search"
        csvLink = ""
        results = '[]'
    sq = ''
    if request.method == "POST":
        searchresults = searchForms(request.POST, request.FILES, prefix='ms')
        #request.session['output'] = 'GotToPost'
        if searchresults.is_valid():
            formResults = []
            markers = []
            #print(searchresults)
            for form in searchresults:
                #iterate through forms
                formTuple = searchLanguageDatumColor(form.cleaned_data)
                wordSearchText = form.cleaned_data['wordSearch']
                glossSearchText = form.cleaned_data['glossSearch']
                annotSearchText = form.cleaned_data['annotationSearch']
                tagSearchText = form.cleaned_data['tagSearch']
                color = form.cleaned_data['colorinput']
                sq += "Color: {} Word: {} Gloss: {} Annotation:{} Tags: {}\n".format(
                    color, wordSearchText, glossSearchText, annotSearchText, tagSearchText)
                #print("FormTuple:{}".format(formTuple))
                formResults.append(formTuple)
            searchquery = sq
            formResults.sort(key=lambda x: x[1])
            for key, group in groupby(formResults, lambda x: x[1]):
                #print("Key: {}, Group:{}".format(key,group))
                groupcolor = key #I think this is right
                finalqueryset = None
                dialectQS = None
                first = True
                print("Group:{})".format(group))
                for member in group:
                    #print(member)

                    if first == True:
                        dialectQS = Dialect.objects.filter(languagedatum__in=member[0])
                        finalqueryset = member[0]
                        #print("Finalquery set1: {}".format(str(finalqueryset).encode('ascii', errors='backslashreplace')))
                        first= False
                    else:
                        dialectQS = dialectQS & Dialect.objects.filter(languagedatum__in=member[0]) #only AND the dialects, not the data itself
                        finalqueryset = finalqueryset.distinct() | member[0].distinct() #combine results, the ANDing happens at the level of the dialect
                        #print("Finalquery set2: {}".format(str(finalqueryset).encode('ascii', errors='backslashreplace')))
                #This has to be after all the member functions are over, outside of that loop, otherwise the QS actions are pointless
                #print("Final dialectQS: {}".format(str(dialectQS).encode('ascii', errors='backslashreplace')))
                finalqueryset = finalqueryset.filter(dialect__in=dialectQS)
                #print("Finalquery set final: {}".format(str(finalqueryset).encode('ascii', errors='backslashreplace')))
                markers += generateMarkers((finalqueryset,groupcolor)) #Up to here works for both map and list
            #print("Markers: {}".format(markers))
            #print(finalqueryset)
            serialized = []
            csvserialized = []
            if type=="map":
                markers = cleanupMarkers(markers)
                for myobject in markers:
                    serialized.append(geojson.dumps(myobject))
                    csvserialized.append(myobject.csvserialized)
                serialized = ",".join(serialized)
                #print(serialized)
                results = serialized
                request.session['csvout'] = "\n".join(csvserialized)
                request.session['csvheader'] = "Dialect,Color,Lat,Long" # "self.dialectname, self.color, self.geomLat, self.geomLong"
            elif type=="list":
                arraylist = [x.dtarray for x in markers]
                resultsformatted = json.dumps(arraylist)
                results = resultsformatted
        return render(request, 'searchMulti2.html', {'pageTitle': pagetitle, 'paradigmDict': paradigmDict.items(),
                                                     'dataFormset': searchresults, 'targetPage' : targetPage, 'initialSource': targetPage,
                                                     'csvlink' : csvLink, 'results' : results, 'searchquery' : searchquery}) #searchresults has to be passed to retain data
    else:
        #results = ""
        searchForms = searchForms(prefix='ms')
        return render(request, 'searchMulti2.html', {'pageTitle': pagetitle, 'paradigmDict': paradigmDict.items(),  'dataFormset': searchForms,
                                                     'targetPage' : targetPage, 'initialSource': targetPage, 'csvlink': csvLink, 'results': results,
                                                     'searchquery': searchquery})

def csvMap(request):
    return render(request, 'genericCSV.csv')

def tsvView(request):
    dialectData = LanguageDatum.objects.all()
    return render(request, 'export.tsv', {'dialectData': dialectData})



def leafletMap(request):

    #queryTuple = searchLanguageDatum(request)
    #resultsObj = generateMarkers(queryTuple)
    #serialized = []

    #for object in resultsObj:
    #    serialized.append(geojson.dumps(object))
    #serialized = ",".join(serialized)

    #request.session['geojson'] = serialized
    #return render(request, 'LeafletMap.html', {'serialized':serialized})
    return render(request,'LeafletMap.html')

def tableInput(request):

    #Logic for this must be as follows:
    #Get shared datum information
    #Retrieve individual datums
    #Retrieve related datums, relate to default/head data
    #   This should include variant entry with ~ and () #NOT IMPLEMENTING THIS FOR THE MOMENT
    #   Honestly, could implement this -> for each datum with targeted header, create the relationship
    #   Annotation data is kind of a special case
    #* distinguishes the input data from other form data
    #Get everything into database-updatable format


    if request.method == 'GET':
        dialectForm = DatumBasicInfoPgNo(request.GET)
        querydata = request.GET.copy()
        tags = ""
        combinedDict = []
        sharedTags = querydata.get("sharedtags", "").split("_") #wish I could just pop it

        #for each piece of linguistic data, create a list of dictionaries. Each dictionary should contain: "datum", "gloss", "annotation", "tags" (as list?), "relationships"
        #Relationships: what should they point at? They should point at datum I guess, but only one of them
        if dialectForm.is_valid():
            initialObject = dialectForm.save(commit=False)
            combinedDict = processInputForm(sharedTags, querydata)
            datumsToObjs(initialObject,combinedDict)
        return render(request, 'tableInputTest.html', {'output': combinedDict, 'dialectForm': dialectForm})
    else:
        dialectForm = DatumBasicInfo()
        return render(request, 'tableInputTest.html', {'output': "", 'dialectForm': dialectForm})


def complexTable(request,paradigmname,toggleAnnot="A"):
    combinedDict = []
    retrievedParadigm = paradigmDict[paradigmname]
    if request.method == 'POST':
        dialectForm = DatumBasicInfoPgNo(request.POST)
        querydata = request.POST.copy()
        tags = ""
        combinedDict = []
        if toggleAnnot == "NA":
            retrievedParadigm.annotation = False
        sharedTags = querydata.get("sharedtags", "").split("_") #wish I could just pop it

        #for each piece of linguistic data, create a list of dictionaries. Each dictionary should contain: "datum", "gloss", "annotation", "tags" (as list?), "relationships"
        #Relationships: what should they point at? They should point at datum I guess, but only one of them
        if dialectForm.is_valid():
            initialObject = dialectForm.save(commit=False)
            combinedDict = processInputForm(sharedTags, querydata)
            datumsToObjs(initialObject,combinedDict)
        return render(request, 'ComplexTableInput.jinja', {'pageTitle': retrievedParadigm.paradigmname,'paradigmDict': paradigmDict.items(),  'output': combinedDict, 'dialectForm': dialectForm, 'dataStruct': retrievedParadigm})
    else:
        dialectForm = DatumBasicInfoPgNo()
    return render(request,'ComplexTableInput.jinja', {'pageTitle': retrievedParadigm.paradigmname,'paradigmDict': paradigmDict.items(), 'output': combinedDict, 'dialectForm': dialectForm, 'dataStruct': retrievedParadigm})

def complexTableView(request):
    retrievedParadigm = paradigmDict['independentpronouns'] #random default since something needs to be passed
    if request.method == 'POST':
        dialectForm = ParadigmSearchForm(request.POST, request.FILES)
        if dialectForm.is_valid():
            result = dialectForm.cleaned_data
            #dialects = list(filter(None, result.get("dialectSearch").split(",")))
            dialects = [x for x in result.get("dialectSearch").split(",") if x.strip()]
            print("DialectsCleaned: {}".format(dialects))
            paradigmname = result.get("paradigm")
            retrievedParadigm = paradigmDict[paradigmname]
            return render(request, 'ComplexTableView.jinja', {'pageTitle': retrievedParadigm.paradigmname, 'paradigmDict': paradigmDict.items(),'dataStruct': retrievedParadigm, 'dialectForm': dialectForm, 'dialectList' : dialects})
    else:
        dialectForm = ParadigmSearchForm()
    return render(request, 'ComplexTableView.jinja', {'pageTitle': retrievedParadigm.paradigmname, 'paradigmDict': paradigmDict.items(),'dataStruct': retrievedParadigm, 'dialectForm': dialectForm, 'dialectList' : []})

def crossSearchView(request):
    mainSearch = formset_factory(NonModelSearchForm, extra=1)
    crossSearch = formset_factory(NonModelSearchForm, extra=1)
    if request.method == 'POST':
        mainresults = mainSearch(request.POST, request.FILES, prefix="ms")
        crossresults = crossSearch(request.POST, request.FILES, prefix = "cs")
        if mainresults.is_valid() and crossresults.is_valid():
            first = True
            mainQS = "" #is this necessary? Don't understand python scope
            mainsearchtext = ""
            headerRows = ["Dialect"]
            bodyRows = [] #Going to be a list of lists
            for msform in mainresults: #Everything from this section should be 'anded' to produce the final main query
                if first:
                    mainQS = searchLanguageDatum(msform.cleaned_data)
                    mainsearchtext = searchText(msform.cleaned_data) + "\n"
                    first = False
                else:
                    mainQS = mainQS & searchLanguageDatum(msform.cleaned_data)#Fix this, it won't work correctly, see above
                    mainsearchtext + searchText(msform.cleaned_data) + "\n"
            headerRows.append("Main:" + mainsearchtext)
            dialectsList = Dialect.objects.filter(languagedatum__in=mainQS).distinct().order_by('dialectCode')
            first = True
            columnQSs = [mainQS,]
            for csform in crossresults: #every one of these things is its own search
                headerRows.append(searchText(csform.cleaned_data))
                columnQSs.append(searchLanguageDatum(csform.cleaned_data)) #Each of these queries should include all of the results of these searches
            for dl in dialectsList:
                thisRow = [dl.dialectCode, ]
                for cqs in columnQSs:
                    filteredQS = cqs.filter(dialect=dl)
                    textofQS = ", ".join([x.normalizedEntry for x in filteredQS]) #converts queryset into list, thence into breaklined text
                    thisRow.append(textofQS)
                bodyRows.append(thisRow)
        return render(request, "Cross_search.html", {'pageTitle' : 'Cross Search', 'paradigmDict': paradigmDict.items(), 'mainFormset' : mainresults, 'relatedFormset': crossresults, 'headerRows' : headerRows, 'bodyRows': bodyRows})
    else:
        mainSearchFS = mainSearch(prefix="ms")
        crossSearchFS = crossSearch(prefix="cs")
        return render(request, "Cross_search.html", {'pageTitle' : 'Cross Search', 'paradigmDict': paradigmDict.items(), 'mainFormset' : mainSearch(prefix="ms"), 'relatedFormset': crossSearchFS})

def taglistview(request):
    headers = ['Tag', 'Explanation']
    allTags = EntryTag.objects.all()
    listOut = [[x.tagText, x.tagExplanation] for x in allTags]
    #print("Alltags: {}".format(listOut))
    return render(request, "infotable.html", {'pageTitle' : 'Datum Tags', 'paradigmDict': paradigmDict.items(),
                                              'tableCaption' : "Datum Tags", 'headerList': headers, 'allItems': listOut
                                              })


def dialectlistview(request):
    headers = ['Dialect Code', 'Longform Name', 'Latitude', 'Longitude'] #Leaving out dialect tags for now
    allTags = Dialect.objects.all()
    dialectCount = allTags.count()
    extrainfo = "Database contains a total of {} dialects".format(dialectCount)
    listOut = [[a.dialectCode, a.dialectNameEn, a.centerLoc.y, a.centerLoc.x] for a in allTags]

    #print("Alltags: {}".format(listOut))
    return render(request, "infotable.html", {'pageTitle' : 'Dialect List', 'paradigmDict': paradigmDict.items(),
                                              'tableCaption' : "Dialect List", 'headerList': headers, 'allItems': listOut,
                                              'extraInfo' : extrainfo
                                              })

def contributorslistview(request):
    headers = ['First name', 'Last Name', 'Number of Public Datums Contributed', 'Number of All Datums Contributed', 'Total Datums in Database']
    allUsers = Contributor.objects.all()
    listOut = [[a.user.first_name,a.user.last_name,LanguageDatum.objects.filter(contributor=a).exclude(permissions='Private').count(), LanguageDatum.objects.filter(contributor=a).count(), LanguageDatum.objects.all().count()]
               for a in allUsers]
    return render(request, "infotable.html", {'pageTitle' : 'Contributors', 'paradigmDict': paradigmDict.items(),
                                          'tableCaption' : "Contributors", 'headerList': headers, 'allItems': listOut
                                          })
def aboutview(request):
    return render(request, 'about.html', {'pageTitle' : 'About', 'paradigmDict': paradigmDict.items()})
##################INACTIVE VIEWS KEPT FOR ARCHIVAL PURPOSES#########################################


def all_kml(request):
    #hardcoding this for fun
    datumsWithN = LanguageDatum.objects.all()
    #datumsWithN = LanguageDatum.objects.filter(normalizedEntry__contains='n', entryTags__tagText="interr.what")
    #datumsWithN = LanguageDatum.objects.filter(entryTags__tagText="interr.what")
    locationsOfns = []
    for item in datumsWithN:
        locationsOfns.append(item.dialect.dialectCode) #there's got to be a more python way to do this
    locations  = Dialect.objects.filter(dialectCode__in=locationsOfns).kml()
    return render_to_kml("gis/kml/placemarks.kml", {'places' : locations})
# Create your views here.

def kml_from_langDatum_objects(request): #given a request, show the map
        initial_Queryset = searchLanguageDatum(request)
        locationOfns = []
        for item in initial_Queryset:
            locationOfns.append(item.dialect.dialectCode) #there's got to be a more python way to do this
        locationsSet = Dialect.objects.filter(dialectCode__in=locationOfns).kml() #I think I have to call this now, this .kml function is a PITA
        return render_to_kml("gis/kml/placemarks.kml", {'places' : locationsSet}) #This returns a KML object, is this a problem?

def kml_from_langDatum_objects_complementary(request): #given a request, show the results and the complementary result
        initial_Queryset = searchLanguageDatum(request)
        locationOfns = []
        for item in initial_Queryset:
            locationOfns.append(item.dialect.dialectCode) #there's got to be a more python way to do this

        locationsSet = Dialect.objects.filter(dialectCode__in=locationOfns).kml() #I think I have to call this now, this .kml function is a PITA
        for locItem in locationsSet:
            locItem.style = 'yellowSquare'

        excludedLocationsSet = Dialect.objects.exclude(dialectCode__in=locationOfns).kml()
        #Should check to see if any data exists so we don't just get every data point
        for locItem in excludedLocationsSet:
            locItem.style = 'whiteSquare'
        #locationsSet = locationsSet + excludedLocationsSet

        return render_to_kml("gis/kml/placemarksIcons2.kml", {'placeSets' : [locationsSet, excludedLocationsSet]}) #This returns a KML object, is this a problem?

def map_page(request):
     lcount = Dialect.objects.all().count() #don't do anything with this anymore
     return render_to_response('map.html', {'location_count' : lcount})

def mockup(request):
    #just all data right now
    dialectform  = DatumBasicInfo()
    return render_to_response('pronounmockup.html', {'dialectForm' : dialectform})

##This was used for an interrogative based input scheme
def interrInput(request):
    # if this is a POST request we need to process the form data
    interrTitles = ['Who?' , 'What?', 'When?','Why>', 'How?', 'Where?', 'Where to?', 'Where from?' , 'Which?', 'Interrogative Particle']
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DatumBasicInfo(request.POST)
        form2 = modelformset_factory(DatumIndividualInfo, extra=5) #DatumIndividualInfo(request.POST)
        # check whether it's valid:
        if form.is_valid() and form2.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            newDatumGen = form.save(commit=False)
            newDatumSpec = form2.save(commit=False)
            newDatum = LanguageDatum(normalizationStyle =newDatumGen.normalizationStyle,dialect=newDatumGen.dialect,
                                     sourceDoc=newDatumGen.sourceDoc, contributor=newDatumGen.contributor,
                                     permissions=newDatumGen.permissions)
            newDatum.gloss = "What?"
            newDatum.normalizedEntry = newDatumSpec.normalizedEntry
            newDatum.originalOrthography = newDatumSpec.originalOrthography
            newDatum.annotation = newDatumSpec.annotation
            newDatum.sourceLocation = newDatumSpec.sourceLocation
            newDatum.save()
            closedClassTag = EntryTag.objects.get(tagText="closed-class")
            newDatum.entryTags.add(closedClassTag)
            interrWhatTag = EntryTag.objects.get(tagText="interr.what")
            newDatum.entryTags.add(interrWhatTag)
            return HttpResponseRedirect('/map/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = DatumBasicInfo()
        form2 = DatumIndividualInfo()
    return render(request, 'interr.html', {'form': form, 'formset' :form2})


def search_Map(request):
    form = NonModelSearchForm()
    return render_to_response('searchTemp.html', {'pageTitle':"Map-Style Search Page", 'targetPage' : "/mapSearch", 'initialSource': "/map", 'searchForm' : form })