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



#Basic free input form view and validation
#Not sure if I should require specific permissions at this point - having a login sufficient?
@login_required
def inputForm(request,numSets=1): #default is one, but can be sent more
    numSets = int(numSets) #didn't know I have to cast this, but apparently I do, otherwise it throws an error
    datumForms = formset_factory(DatumIndividualInfo, extra=numSets)
    contributor = Contributor.objects.get(user=request.user)
    if request.method == 'POST':#validate
        #dialectForm holds the basic dialect information
        dialectForm = DatumBasicInfo(request.POST, initial={'normalizationStyle': contributor.defaultEncoding , 'permissions': contributor.defaultPermission,
                                                            'glosslang' : contributor.defaultLanguage}) #have not tested that auto-set glosslang works
        datumForms = datumForms(request.POST, request.FILES)
        initialObject = LanguageDatum()
        finalObjectList = []
        if dialectForm.is_valid():
            initialObject = dialectForm.save(commit=False)
            initialObject.contributor = contributor
            inputlang = dialectForm.cleaned_data["glosslang"]
            print("DialectForm: Valid")
            #print(deliberatelybreakingit)
            if datumForms.is_valid():
                print("DatumForm:Valid")
                for form in datumForms:
                    finalObject = form.save(commit=False)
                    glossdict = {inputlang : finalObject.gloss}
                    finalObject.multigloss = glossdict
                    finalObject.normalizationStyle = initialObject.normalizationStyle
                    finalObject.dialect = initialObject.dialect
                    finalObject.sourceDoc = initialObject.sourceDoc
                    finalObject.contributor = initialObject.contributor
                    finalObject.permissions = initialObject.permissions
                    tags = form.cleaned_data['entryTags'] #this gives a list of tags
                    #print(tags)
                    finalObject.save()
                    finalObject.entryTags = tags #simple as making it equal the list, good to know
                    form.save_m2m() #THE FORM SAVES THE M2M relationship!
                    finalObjectList.append(finalObject)
            return render(request, 'tableView.html', {'object_list' : finalObjectList})
        #datumForms = datumForms(request.GET) saw this in a tutorial, no idea what it means
        #test
       # pass
        return render(request, 'inputForm.html',{'pageTitle': "Single Dialect Multi-Datum Input Form", 'paradigmDict': paradigmDict.items(),  'dialectForm' : dialectForm, 'dataFormset': datumForms})
    else:
        dialectForm = DatumBasicInfo(initial={'normalizationStyle': contributor.defaultEncoding , 'permissions': contributor.defaultPermission})
        #datumForms = formset_factory(DatumIndividualInfo, extra=numSets)
        return render(request, 'inputForm.html',{'pageTitle': "Single Dialect Multi-Datum Input Form", 'paradigmDict': paradigmDict.items(), 'dialectForm' : dialectForm, 'dataFormset': datumForms})

@login_required
def complexTableInput(request,paradigmname,toggleAnnot="A"): #Input
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
            initialObject = dialectForm.save(commit=False)
            initialObject.contributor = contributor
            inputlanguage = retrievedParadigm.glosslang
            combinedDict = processInputForm(sharedTags, querydata)
            datumsToObjs(initialObject,combinedDict)
        return render(request, 'ComplexTableInput.jinja', {'pageTitle': retrievedParadigm.paradigmname,'paradigmDict': paradigmDict.items(),  'output': combinedDict, 'dialectForm': dialectForm, 'dataStruct': retrievedParadigm})
    else:
        dialectForm = DatumBasicInfoPgNo(initial={'normalizationStyle': contributor.defaultEncoding , 'permissions': contributor.defaultPermission})
    return render(request,'ComplexTableInput.jinja', {'pageTitle': retrievedParadigm.paradigmname,'paradigmDict': paradigmDict.items(), 'output': combinedDict, 'dialectForm': dialectForm, 'dataStruct': retrievedParadigm})




############## View functions which are sensitive to permissions ###############

#Have not altered this to work with multilingual glosses, probably unnecessary
def complexTableView(request):
    retrievedParadigm = paradigmDict['independentpronouns'] #random default since something needs to be passed
    if request.method == 'POST':
        dialectForm = ParadigmSearchForm(request.POST, request.FILES)
        if dialectForm.is_valid():
            result = dialectForm.cleaned_data
            #dialects = list(filter(None, result.get("dialectSearch").split(",")))
            dialects = [x for x in result.get("dialectSearch").split(",") if x.strip()] #If there's data, put it into a list of dialects
            print("DialectsCleaned: {}".format(dialects))
            paradigmname = result.get("paradigm")
            retrievedParadigm = paradigmDict[paradigmname]
            return render(request, 'ComplexTableView.jinja', {'pageTitle': retrievedParadigm.paradigmname, 'paradigmDict': paradigmDict.items(),'dataStruct': retrievedParadigm, 'dialectForm': dialectForm, 'dialectList' : dialects})
    else:
        dialectForm = ParadigmSearchForm()
    return render(request, 'ComplexTableView.jinja', {'pageTitle': retrievedParadigm.paradigmname, 'paradigmDict': paradigmDict.items(),'dataStruct': retrievedParadigm, 'dialectForm': dialectForm, 'dialectList' : []})





def searchMultiType(request, type="map"):
    numSets = 1
    searchForms = formset_factory(NonModelSearchFormColor)
    searchquery = ''
    results = ''
    targetpage = ""
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
                        #print("Finalquery set2: {}".format(str(finalqueryset).encode('ascii', errors='backslashreplace')))
                #This has to be after all the member functions are over, outside of that loop, otherwise the QS actions are pointless
                #print("Final dialectQS: {}".format(str(dialectQS).encode('ascii', errors='backslashreplace')))
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
            dialectsList = Dialect.objects.filter(languagedatum__in=finalQS).distinct().order_by('dialectCode')
            first = True
            columnQSs = [finalQS,]
            for csform in crossresults: #every one of these things is its own search
                headerRows.append(searchText(csform.cleaned_data))
                columnQSs.append(searchLanguageDatum(csform.cleaned_data, request.user)) #Each of these queries should include all of the results of these searches
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
