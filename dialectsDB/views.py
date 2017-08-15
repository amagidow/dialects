from django.shortcuts import render, render_to_response
from django.forms.models import modelformset_factory, formset_factory
from dialectsDB.models import *
from dialectsDB.forms import *
from django.views.generic import ListView
from dialectsDB.utilityfuncs import *
from dialectsDB.paradigms import *
from itertools import groupby
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
import json



############ Non-input or output form functions ##############
def mylogout(request):
    logout(request) #Sufficient to just log the person out
    return HttpResponseRedirect("/login/")

############ Input Forms should ALL be login required for the time being ###################

#Basic free input form view and validation. Allows a single dialect to have multiple datums input at once
#Use of this form by end users is strongly discouraged
#Not sure if I should require specific permissions at this point - having a login sufficient?
@login_required
def inputForm(request,numSets=1): #default is one, but can be sent more
    """
    Basic free input form view and validation. Allows a single dialect to have multiple datums input at once.
    Use of this form by end users is strongly discouraged.
    :param request:
    :param numSets: Number of initial datums shown. Basically depreciated with addition of dynamic-formsets.
    :return:
    """
    numSets = int(numSets) #didn't know I have to cast this, but apparently I do, otherwise it throws an error
    datumForms = formset_factory(DatumIndividualInfo, extra=numSets)
    contributor = Contributor.objects.get(user=request.user) #from user string, retrieve containing class of contributor
    if request.method == 'POST':#validate
        #dialectForm holds the basic dialect information
        #Populate appropriate fields according to contributor's preferences
        dialectForm = DatumBasicInfo(request.POST, initial={'normalizationStyle': contributor.defaultEncoding , 'permissions': contributor.defaultPermission,
                                                            'glosslang' : contributor.defaultLanguage}) #have not tested that auto-set glosslang works
        datumForms = datumForms(request.POST, request.FILES) #datumForms holds the actual datums themselves
        initialObject = LanguageDatum() #Assinging this to a languagedatum object may be unnecessary
        finalObjectList = []
        if dialectForm.is_valid():
            initialObject = dialectForm.save(commit=False) #populate initial object with the shared data. This object will not be saved
            initialObject.contributor = contributor #add contributor to shared data
            inputlang = dialectForm.cleaned_data["glosslang"] #retrieve gloss language - this is tested, works
            if datumForms.is_valid():
                for form in datumForms: #for each form with actual data
                    finalObject = form.save(commit=False)
                    glossdict = {inputlang : finalObject.gloss}
                    finalObject.multigloss = glossdict
                    #assign missing informaiton from initialObject form data
                    finalObject.normalizationStyle = initialObject.normalizationStyle
                    finalObject.dialect = initialObject.dialect
                    finalObject.sourceDoc = initialObject.sourceDoc
                    finalObject.contributor = initialObject.contributor
                    finalObject.permissions = initialObject.permissions
                    tags = form.cleaned_data['entryTags'] #this gives a list of tags
                    finalObject.save()
                    finalObject.entryTags = tags #simple as making it equal the list, good to know
                    form.save_m2m() #THE FORM SAVES THE M2M relationship!
                    finalObjectList.append(finalObject)
            return render(request, 'tableView.html', {'object_list' : finalObjectList}) #This needs to be replaced eventually
        return render(request, 'inputForm.html',{'pageTitle': "Single Dialect Multi-Datum Input Form", 'paradigmDict': paradigmDict.items(),  'dialectForm' : dialectForm, 'dataFormset': datumForms})
    else:
        dialectForm = DatumBasicInfo(initial={'normalizationStyle': contributor.defaultEncoding , 'permissions': contributor.defaultPermission, 'glosslang' : contributor.defaultLanguage})
        return render(request, 'inputForm.html',{'pageTitle': "Single Dialect Multi-Datum Input Form", 'paradigmDict': paradigmDict.items(), 'dialectForm' : dialectForm, 'dataFormset': datumForms})

#This view retrieves paradigmatic input via a complex jinja view which itself has a great deal of logic
#The paradigm itself is stored in paradigms.py and is rendered by the jinja template
#Like the inputForm view, a basic dialect information view is shown above the complex input
#Annotation in the table can be set to on (toggleAnnot=A) or off (toggleAnnot=b)
@login_required
def complexTableInput(request,paradigmname,toggleAnnot="A"):
    """
    This view retrieves paradigmatic input via a complex jinja view which itself has a great deal of logic.
    The paradigm itself is stored in paradigms.py and is rendered by the ComplexTableInput.jinja template.
    Like the :func:inputForm view, a basic dialect information view is shown above the complex input
    :param request:
    :param paradigmname: String containing the name of the paradigm from URL config
    :param toggleAnnot: Either `A` (include annotation columns) or `NA` (no annotation columns). To eventually be replaced with Javascript toggles.
    :return:
    """
    combinedDict = []
    retrievedParadigm = paradigmDict[paradigmname]
    contributor = Contributor.objects.get(user=request.user)
    if request.method == 'POST':
        dialectForm = DatumBasicInfoPgNo(request.POST, initial={'normalizationStyle': contributor.defaultEncoding , 'permissions': contributor.defaultPermission})
        querydata = request.POST.copy()
        tags = ""
        combinedDict = []
        if toggleAnnot == "NA":
            retrievedParadigm.annotation = False
        sharedTags = querydata.get("sharedtags", "").split("_") #wish I could just pop it

        #for each piece of linguistic data, create a list of dictionaries. Each dictionary should contain: "datum", "gloss", "annotation", "tags" (as list?), "relationships"
        #Relationships: what should they point at? They should point at datum I guess, but only one of them
        if dialectForm.is_valid():
            #Radio button based shared tags need to be added here
            radiosharedtags = [value.split("_") for key, value in querydata.items() if "optionsset" in key]
            radiosharedtags = [item for sublist in radiosharedtags for item in sublist] #Flattens out list in case there are lists of lists due to the split command above
            sharedTags = sharedTags + radiosharedtags
            initialObject = dialectForm.save(commit=False)
            initialObject.contributor = contributor
            inputlanguage = retrievedParadigm.glosslang
            combinedDict = processInputForm(sharedTags, querydata, retrievedParadigm.defaultvalue)
            datumsToObjs(initialObject,combinedDict)
        return render(request, 'ComplexTableInput.jinja', {'pageTitle': retrievedParadigm.paradigmname,'paradigmDict': paradigmDict.items(),  'output': combinedDict, 'dialectForm': dialectForm, 'dataStruct': retrievedParadigm})
    else:
        dialectForm = DatumBasicInfoPgNo(initial={'normalizationStyle': contributor.defaultEncoding , 'permissions': contributor.defaultPermission})
    return render(request,'ComplexTableInput.jinja', {'pageTitle': retrievedParadigm.paradigmname,'paradigmDict': paradigmDict.items(), 'output': combinedDict, 'dialectForm': dialectForm, 'dataStruct': retrievedParadigm})




############## View functions which are sensitive to permissions ###############

#Have not altered this to work with multilingual glosses, probably unnecessary
#This view shows a complex table using the same paradigms as in complexTableInput
#The actual form asks for the paradigm and for the dialects (comma separated list with autocompletion)
def complexTableView(request):
    """
    This view shows a complex table using the same paradigms as in complexTableInput and which are stored in the paradigms dictionary
    :param request:
    :return:
    """
    retrievedParadigm = paradigmDict['independentpronouns'] #random default since something needs to be passed
    if request.method == 'POST':
        dialectForm = ParadigmSearchForm(request.POST, request.FILES)
        querydata = request.POST.copy()
        if dialectForm.is_valid():
            result = dialectForm.cleaned_data
            #dialects = list(filter(None, result.get("dialectSearch").split(",")))
            dialects = [x for x in result.get("dialectSearch").split(",") if x.strip()] #If there's data, put it into a list of dialects
            #print("DialectsCleaned: {}".format(dialects))
            paradigmname = result.get("paradigm")
            retrievedParadigm = paradigmDict[paradigmname]
            #add in section here to retrieve within paradigm tags, then add another variable to export it out to the render request as a separate variable
            radiosharedtags = [value.split("_") for key, value in querydata.items() if "optionsset" in key]
            radiosharedtags = [item for sublist in radiosharedtags for item in sublist] #Flattens out list in case there are lists of lists due to the split command above
            print("Radio shared tags:")
            print(radiosharedtags)
            #print(radiosharedtags)
            return render(request, 'ComplexTableView.jinja', {'pageTitle': retrievedParadigm.paradigmname, 'paradigmDict': paradigmDict.items(),'dataStruct': retrievedParadigm,
                                                              'dialectForm': dialectForm, 'dialectList' : dialects, 'inparadigmtags' : radiosharedtags })
    else:
        dialectForm = ParadigmSearchForm()
    return render(request, 'ComplexTableView.jinja', {'pageTitle': retrievedParadigm.paradigmname, 'paradigmDict': paradigmDict.items(),'dataStruct': retrievedParadigm,
                                                      'dialectForm': dialectForm, 'dialectList' : [], 'inparadigmtags' : []})




#This view handles either map or list-style searches, since they are almost identical. Type is passed via the URLConfig
#List-type view actually includes 'color' as a convenient shortcut for ANDing queries, and to produce groups
def searchMultiType(request, type="map"):
    """
    This view handles either map or list-style searches, since they are almost identical. Type is passed via the URLConfig
    :param request: HTTP request
    :param type: String, either `map` or `list`, handled by URLConfig
    :return: render of `searchMulti.html`
    """
    searchForms = formset_factory(NonModelSearchFormColor)
    #initializing for scope
    searchquery = ''
    targetPage = ""
    pagetitle = ""
    results = ''
    if request.user.is_authenticated(): #If there's a user to get, make contributor equal to that user
        contributor = Contributor.objects.get(user=request.user)
    else: #If not, it's null, will get passed to permission functions as null.
        contributor = None
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
    #This need not be done with POST (no privacy concerns) but GET was causing problems with initial page loads giving "required" errors
    if request.method == "POST":
        searchresults = searchForms(request.POST, request.FILES, prefix='ms')
        #request.session['output'] = 'GotToPost'
        if searchresults.is_valid():
            formResults = []
            markers = []
            csvMarkers = []
            #print(searchresults)
            for form in searchresults:
                #These lines do the actual processing
                formTuple = searchLanguageDatumColor(form.cleaned_data, request.user) #Passing it the cleaned data, NOT the request
                formResults.append(formTuple)
                #These lines just create a small blurb under the search form
                wordSearchText = form.cleaned_data['wordSearch']
                glossSearchText = form.cleaned_data['glossSearch']
                annotSearchText = form.cleaned_data['annotationSearch']
                tagSearchText = form.cleaned_data['tagSearch']
                color = form.cleaned_data['colorinput']
                sq += "Color: {} Word: {} Gloss: {} Annotation:{} Tags: {}\n".format(
                    color, wordSearchText, glossSearchText, annotSearchText, tagSearchText)
                #print("FormTuple:{}".format(formTuple))
            searchquery = sq
            #Sort the results by color before grouping
            formResults.sort(key=lambda x: x[1])
            #Iterate through color groups
            for key, group in groupby(formResults, lambda x: x[1]):
                #print("Key: {}, Group:{}".format(key,group))
                groupcolor = key #I think this is right
                finalqueryset = None
                dialectQS = None
                first = True
                #print("Group:{})".format(group))
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
                #This has to be after all the member functions are over, outside of that loop, otherwise the QS actions are pointless
                finalqueryset = finalqueryset.filter(dialect__in=dialectQS)
                markers += generateMarkers((finalqueryset,groupcolor)) #Up to here works for both map and list

                #Doing permissions manually here, this is not the best way to do things but works for now
                if type=="map":
                    colorQS = finalqueryset.filter(contributor=contributor) | finalqueryset.exclude(contributor=contributor).exclude(permissions__contains="NoE") #This will also exclude things from the user - need to fix it
                    csvMarkers += generateMarkers((colorQS.distinct(), groupcolor))
            #print("Markers: {}".format(markers))
            #print(finalqueryset)
            serialized = []
            csvserialized = []
            if type=="map":
                markers = cleanupMarkers(markers)
                for myobject in markers:
                    serialized.append(geojson.dumps(myobject))
                for myobject in csvMarkers:
                    csvserialized.append(myobject.csvserialized)
                serialized = ",".join(serialized)
                #print(serialized)
                results = serialized
                request.session['csvout'] = "\n".join(csvserialized) #This is manually cleaned of PubNoE data
                request.session['csvheader'] = "Dialect,Color,Lat,Long" # "self.dialectname, self.color, self.geomLat, self.geomLong"
            elif type=="list":
                arraylist = [x.dtarray for x in markers]
                resultsformatted = json.dumps(arraylist)
                results = resultsformatted
        return render(request, 'searchMulti.html', {'pageTitle': pagetitle, 'paradigmDict': paradigmDict.items(),
                                                     'dataFormset': searchresults, 'targetPage' : targetPage, 'initialSource': targetPage,
                                                     'csvlink' : csvLink, 'results' : results, 'searchquery' : searchquery}) #searchresults has to be passed to retain data
    else:
        #results = ""
        searchForms = searchForms(prefix='ms')
        return render(request, 'searchMulti.html', {'pageTitle': pagetitle, 'paradigmDict': paradigmDict.items(),  'dataFormset': searchForms,
                                                     'targetPage' : targetPage, 'initialSource': targetPage, 'csvlink': csvLink, 'results': results,
                                                     'searchquery': searchquery})



def mapPageSearch(request):
    """
    This view handles either map or list-style searches, since they are almost identical. Type is passed via the URLConfig
    :param request: HTTP request
    :param type: String, either `map` or `list`, handled by URLConfig
    :return: render of `searchMulti.html`
    """
    searchForms = formset_factory(NonModelSearchFormColor)
    #initializing for scope
    searchquery = ''
    targetPage = ""
    pagetitle = ""
    results = ''
    if request.user.is_authenticated(): #If there's a user to get, make contributor equal to that user
        contributor = Contributor.objects.get(user=request.user)
    else: #If not, it's null, will get passed to permission functions as null.
        contributor = None
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
    #This need not be done with POST (no privacy concerns) but GET was causing problems with initial page loads giving "required" errors
    if request.method == "POST":
        searchresults = searchForms(request.POST, request.FILES, prefix='ms')
        #request.session['output'] = 'GotToPost'
        if searchresults.is_valid():
            formResults = []
            markers = []
            csvMarkers = []
            #print(searchresults)
            for form in searchresults:
                #These lines do the actual processing
                formTuple = searchLanguageDatumColor(form.cleaned_data, request.user) #Passing it the cleaned data, NOT the request
                formResults.append(formTuple)
                #These lines just create a small blurb under the search form
                wordSearchText = form.cleaned_data['wordSearch']
                glossSearchText = form.cleaned_data['glossSearch']
                annotSearchText = form.cleaned_data['annotationSearch']
                tagSearchText = form.cleaned_data['tagSearch']
                color = form.cleaned_data['colorinput']
                sq += "Color: {} Word: {} Gloss: {} Annotation:{} Tags: {}\n".format(
                    color, wordSearchText, glossSearchText, annotSearchText, tagSearchText)
                #print("FormTuple:{}".format(formTuple))
            searchquery = sq
            #Sort the results by color before grouping
            formResults.sort(key=lambda x: x[1])
            #Iterate through color groups
            for key, group in groupby(formResults, lambda x: x[1]):
                #print("Key: {}, Group:{}".format(key,group))
                groupcolor = key #I think this is right
                finalqueryset = None
                dialectQS = None
                first = True
                #print("Group:{})".format(group))
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
                #This has to be after all the member functions are over, outside of that loop, otherwise the QS actions are pointless
                finalqueryset = finalqueryset.filter(dialect__in=dialectQS)
                markers += generateMarkers((finalqueryset,groupcolor)) #Up to here works for both map and list

                #Doing permissions manually here, this is not the best way to do things but works for now
                if type=="map":
                    colorQS = finalqueryset.filter(contributor=contributor) | finalqueryset.exclude(contributor=contributor).exclude(permissions__contains="NoE") #This will also exclude things from the user - need to fix it
                    csvMarkers += generateMarkers((colorQS.distinct(), groupcolor))
            #print("Markers: {}".format(markers))
            #print(finalqueryset)
            serialized = []
            csvserialized = []
            if type=="map":
                markers = cleanupMarkers(markers)
                for myobject in markers:
                    serialized.append(geojson.dumps(myobject))
                for myobject in csvMarkers:
                    csvserialized.append(myobject.csvserialized)
                serialized = ",".join(serialized)
                #print(serialized)
                results = serialized
                request.session['csvout'] = "\n".join(csvserialized) #This is manually cleaned of PubNoE data
                request.session['csvheader'] = "Dialect,Color,Lat,Long" # "self.dialectname, self.color, self.geomLat, self.geomLong"
            elif type=="list":
                arraylist = [x.dtarray for x in markers]
                resultsformatted = json.dumps(arraylist)
                results = resultsformatted
        return render(request, 'searchMulti.html', {'pageTitle': pagetitle, 'paradigmDict': paradigmDict.items(),
                                                     'dataFormset': searchresults, 'targetPage' : targetPage, 'initialSource': targetPage,
                                                     'csvlink' : csvLink, 'results' : results, 'searchquery' : searchquery}) #searchresults has to be passed to retain data
    else:
        #results = ""
        searchForms = searchForms(prefix='ms')
        return render(request, 'searchMulti.html', {'pageTitle': pagetitle, 'paradigmDict': paradigmDict.items(),  'dataFormset': searchForms,
                                                     'targetPage' : targetPage, 'initialSource': targetPage, 'csvlink': csvLink, 'results': results,
                                                     'searchquery': searchquery})

def crossSearchView(request):
    """
    This view generates a implicational-type search where the results from one search are collated against an infinite number of secondary searches.
    If a criterion isn't met for the secondary searches, nothing shows up - which could indicated either no data at all, or no data matching the criterion.
    :param request:
    :return:
    """
    mainSearch = formset_factory(NonModelSearchForm, extra=1)
    crossSearch = formset_factory(NonModelSearchForm, extra=1)
    if request.method == 'POST':
        mainresults = mainSearch(request.POST, request.FILES, prefix="ms")
        crossresults = crossSearch(request.POST, request.FILES, prefix = "cs")
        if mainresults.is_valid() and crossresults.is_valid():
            first = True
            mainQS = "" #is this necessary? Don't understand python scope
            dialectQS = None
            mainsearchtext = ""
            headerRows = ["Dialect"]
            bodyRows = [] #Going to be a list of lists
            for msform in mainresults: #Everything from this section should be 'anded' to produce the final main query
                if first:
                    mainQS = searchLanguageDatum(msform.cleaned_data, request.user)
                    dialectQS = Dialect.objects.filter(languagedatum__in=mainQS)
                    mainsearchtext = searchText(msform.cleaned_data) + "\n"
                    first = False
                else:
                    currentQS = searchLanguageDatum(msform.cleaned_data, request.user)
                    dialectQS = dialectQS & Dialect.objects.filter(languagedatum__in=currentQS)
                    mainQS = mainQS.distinct() & currentQS.distinct()#Still need to 'and' to get only those forms that match the criteria
                    mainsearchtext + searchText(msform.cleaned_data) + "\n"
            finalQS = mainQS.filter(dialect__in=dialectQS)
            headerRows.append("Main:" + mainsearchtext)
            dialectsList = Dialect.objects.filter(languagedatum__in=finalQS).distinct().order_by('dialectCode') #only dialects which 'hit' for main query
            first = True
            columnQSs = [finalQS,]
            for csform in crossresults: #every one of these things is its own search
                headerRows.append(searchText(csform.cleaned_data))
                columnQSs.append(searchLanguageDatum(csform.cleaned_data, request.user)) #Each of these queries should include all of the results of these searches
            for dl in dialectsList: #For every dialect in the list returned, do
                thisRow = [(dl.dialectCode, dl.dialectNameEn), ]
                for cqs in columnQSs:
                    filteredQS = cqs.filter(dialect=dl) #queryset that only has that dialect per that query
                    dt = [] #datumtext
                    et = [] #extratext
                    for x in filteredQS: #Go through each returned item, add it to the lists
                        dt.append(x.normalizedEntry)
                        et.append(x.stringextra("&#013;&#010;")) #adds the title text using a model function
                    #textofQS = (", ".join([x.normalizedEntry for x in filteredQS]), "&#013;&#010;&#013;&#010;".join([x.stringextra("&#013;&#010;") for x in filteredQS])) #converts queryset into list, thence into comma joined text - here is where only the normalized entry is shown
                    thisRow.append((", ".join(dt),"&#013;&#010;&#013;&#010;".join(et))) #append it as a tupple
                bodyRows.append(thisRow)
        return render(request, "Cross_search.html", {'pageTitle' : 'Cross Search', 'paradigmDict': paradigmDict.items(), 'mainFormset' : mainresults, 'relatedFormset': crossresults, 'headerRows' : headerRows, 'bodyRows': bodyRows})
    else:
        mainSearchFS = mainSearch(prefix="ms")
        crossSearchFS = crossSearch(prefix="cs")
        return render(request, "Cross_search.html", {'pageTitle' : 'Cross Search', 'paradigmDict': paradigmDict.items(), 'mainFormset' : mainSearch(prefix="ms"), 'relatedFormset': crossSearchFS})

def tsvView(request):
    dialectData = LanguageDatum.objects.all()
    return render(request, 'export.tsv', {'dialectData': dialectData})


def csvMap(request):
    return render(request, 'genericCSV.csv') #This should be sensitive to PubNoE

############## View functions which are NOT sensitive to permissions ###############
def taglistview(request):
    headers = ['Tag', 'Explanation']
    allTags = EntryTag.objects.all()
    listOut = [[x.tagText, x.tagExplanation] for x in allTags]
    #print("Alltags: {}".format(listOut))
    return render(request, "infotable.html", {'pageTitle' : 'Datum Tags', 'paradigmDict': paradigmDict.items(),
                                              'tableCaption' : "Datum Tags", 'headerList': headers, 'allItems': listOut
                                              })


def dialectlistview(request):
    headers = ['Dialect Code', 'Longform Name', 'Latitude', 'Longitude', 'Tags', 'Sources'] #Leaving out dialect tags for now
    alldialects = Dialect.objects.all()
    dialectCount = alldialects.count()
    extrainfo = "Database contains a total of {} dialects".format(dialectCount)
    listOut = [[a.dialectCode, a.dialectNameEn, a.centerLoc.y, a.centerLoc.x, a.tagstring, a.sourceciting] for a in alldialects]

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

def bibliolistview(request):
    headers = ['Author(s)', 'Title', 'Year', 'Journal or Volume Title', 'Volume', 'Publisher', 'Additional Info', 'Unique ID']
    allBibs = BiblioEntryBibTex.objects.all()
    listOut = [[a.author,a.title, a.date, a.secondtitle, a.volume, a.publisher, a.annotation, a.bibTexKey]
               for a in allBibs]
    return render(request, "infotable.html", {'pageTitle' : 'Bibliographic Entries', 'paradigmDict': paradigmDict.items(),
                                          'tableCaption' : "Bibliographic Entries", 'headerList': headers, 'allItems': listOut
                                          })

def aboutview(request):
    return render(request, 'about.html', {'pageTitle' : 'About', 'paradigmDict': paradigmDict.items()})

def versionview(request):
    return render(request, 'versions.html', {'pageTitle' : 'Changes and Versions', 'paradigmDict': paradigmDict.items()})
