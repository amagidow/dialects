__author__ = 'Alex'
from dialectsDB.models import LanguageDatum
class TableAxis(object):
    def __init__(self, headername, headertags, uniqueID = False,subheaders=[], relatedTo=False, relatedHow = ""):
        self.headername = headername #This is identical to "GLOSS" in the processing function - must be unique - so subheaders must inherit from headers
        self.headertags = []
        self.relatedHow = relatedHow
        if isinstance(headertags,str): #Make headertags into a list
            self.headertags = [headertags]
        else:
            self.headertags = self.headertags + headertags
        #self.headertags = "_".join(headertags)

        self.subheaders = subheaders
        self.uniqueID = uniqueID
        self.relatedTo = relatedTo #This is expressed as the headername of the related column

    def getsubtags(self, searchname): #retrieves the tags of a subheader based on its name
        if self.subheaders:
            for header in self.subheaders:
                if header.headername == searchname:
                    return header.headertags
        else:
            return "NoSubHeads"


class StructuredTable(object):
    def __init__(self, paradigmname, sharedtags, columns, rows, glosses, annotation =True, subcolumns=True,subrows=True):
        self.paradigmname = paradigmname
        #self.paradigmnid = paradigmid #TIMPORTNANT: his should be identical to the variable name!!!
        self.sharedtags = sharedtags
        self.annotation = annotation
        self.subcolumns= subcolumns
        self.subrows = subrows
        self.columns = columns
        self.rows = rows
        self.glosses = {}
        for key, value in glosses.items(): #makes all keys alphabetized
            #print("Key: {}, value: {}".format(key, value))
            newKey = list(filter(None,key.split("_")))
            newKey.sort() #this doesn't return anything
            #print("New key:{}".format(newKey))
            newKey = "_".join(newKey)
           # print("New key:{}".format(newKey))
            self.glosses.update({newKey : value})

    def getGloss(self,tags):
        tags.sort()
        tags = list(filter(None,tags))
        print("Tags in getGloss:{}".format(tags))
        if "_".join(tags) in self.glosses:
            return self.glosses["_".join(tags)]
        else:
            return "NoGloss"

    def getDatumsFromTags(self,dialect, tags): #utilty function for in templates
        print("DialectCode is: {}".format(dialect))
        dialect = dialect.strip() #clear whitespace
        #Add User argument with default "none", hit the permission function first, filter on that
        myQuery = LanguageDatum.objects.all().filter(dialect__dialectCode=dialect) #Need to have some user filtering here
        print("Base languageDatum: {}".format(str(myQuery).encode('ascii', errors='backslashreplace')))
        tags = set(tags)
        tags = filter(None, tags) #remove blanks
        print("Tags to Retrieve are: {}".format(tags))
        #print("getDatumFromTags:{}".format(tags))
        for tag in tags:
            tag = tag.strip()
            myQuery = myQuery.filter(entryTags__tagText=tag)
            print("QueryReturned: {}".format(str(myQuery).encode('ascii', errors='backslashreplace')))
        return myQuery


pronounsuffixes = StructuredTable(paradigmname="Pronoun Suffixes", sharedtags= ['closed-class', 'pronoun.suffix'],
                columns= [
                   TableAxis("Singular","singular",subheaders=[
                       TableAxis("C__","cond.C-"), #For relationships,if we restrict to subheaders, we only need to know the appropriate subheader to find and we can figure out tags from there
                       TableAxis("V__", "cond.V-"), #tags CANNOT have an underscore in name
                       TableAxis("VV__", "cond.VV-")
                   ]),
                   TableAxis("Plural", "plural", subheaders=[
                       TableAxis("C__","cond.C-"), #For relationships,if we restrict to subheaders, we only need to know the appropriate subheader to find and we can figure out tags from there
                       TableAxis("V__", "cond.V-"), #tags CANNOT have an underscore in name
                       TableAxis("VV__", "cond.VV-")
                   ]),
               ],
               rows= [
                   TableAxis("1st Person","1st-person"),
                   TableAxis("2nd Person","2nd-person", subheaders=[
                       TableAxis("Masculine", "masculine"),
                       TableAxis("Feminine", "feminine")
                   ]),
                   TableAxis("3rd Person","3rd-person", subheaders=[
                       TableAxis("Masculine", "masculine"),
                       TableAxis("Feminine", "feminine")
                   ]),
               ],
               glosses={#underscore connected tag lists, but will be alphabetized so always works the same
                   "singular_1st-person" : "My",
                   "plural_1st-person" : "Our",
                   "singular_2nd-person_masculine" : "Your (m.)",
                   "singular_2nd-person_feminine" : "Your (f.)",
                   "plural_2nd-person_masculine" : "You all's (m.)",
                   "plural_2nd-person_feminine" : "You all's (f.)",
                   "singular_3rd-person_masculine" : "His",
                   "singular_3rd-person_feminine" : "Her",
                   "plural_3rd-person_masculine" : "Their (m.)",
                   "plural_3rd-person_feminine" : "Their (f.)",
                        }
                )
independentpronouns = StructuredTable(paradigmname="Independent Pronouns", sharedtags= ['closed-class', 'pronoun.independent'],
               columns= [
                    TableAxis("Singular","singular"),
                    TableAxis("Plural", "plural")
               ],
                rows = [
                   TableAxis("1st Person","1st-person"),
                   TableAxis("2nd Person","2nd-person", subheaders=[
                       TableAxis("Masculine", "masculine"),
                       TableAxis("Feminine", "feminine")
                   ]),
                   TableAxis("3rd Person","3rd-person", subheaders=[
                       TableAxis("Masculine", "masculine"),
                       TableAxis("Feminine", "feminine")
                   ]),
                ],
               glosses={
                   "singular_1st-person" : "I",
                   "plural_1st-person" : "We",
                   "singular_2nd-person_masculine" : "You (m.)",
                   "singular_2nd-person_feminine" : "You (f.)",
                   "plural_2nd-person_masculine" : "You all (m.)",
                   "plural_2nd-person_feminine" : "You all (f.)",
                   "singular_3rd-person_masculine" : "He",
                   "singular_3rd-person_feminine" : "She",
                   "plural_3rd-person_masculine" : "They (m.)",
                   "plural_3rd-person_feminine" : "They (f.)",
               })

interrogatives = StructuredTable(paradigmname="Interrogatives", sharedtags=['closed-class'],
                columns=[
                    TableAxis("General", ""),
                    TableAxis("Masculine", "masculine"),
                    TableAxis("Feminine", "feminine")
                ],
                rows=[
                    TableAxis("Who","interr.who"),
                    TableAxis("What","interr.what"),
                    TableAxis("When", "interr.when"),
                    TableAxis("Where", "interr.where"),
                    TableAxis("Where From", "interr.wherefrom"),
                    TableAxis("Where To","interr.whereto"),
                    TableAxis("Why", "interr.why"),
                    TableAxis("How", "interr.how"),
                    TableAxis("How many", "interr.howmany"),
                    TableAxis("How much", "interr.howmuch"),
                    TableAxis("Which", "interr.which"),
                    TableAxis("Polar particle", "interr.polar")
                ],
                glosses={
                    "interr.who": "Who",
                    "interr.who_masculine": "Who (m)",
                    "interr.who_feminine": "Who (f)",

                    "interr.what": "What",
                    "interr.what_masculine": "What (m)",
                    "interr.what_feminine": "What (f)",

                    "interr.when": "When",

                    
                    "interr.where": "Where",

                    
                    "interr.wherefrom": "Wherefrom",

                    "interr.whereto": "Whereto",

                    "interr.why": "Why",

                    
                    "interr.how": "How",

                    "interr.howmuch": "How much",

                    
                    "interr.howmany": "How many",

                    
                    "interr.which": "Which",
                    "interr.which_masculine": "Which (m)",
                    "interr.which_feminine": "Which (f)",

                    "interr.polar": "Interrogative Particle",

                } #	Interrogative Particle
                )



#ALWAYS CHECK THAT YOU DON'T HAVE ANY NOGLOSS IN THE OUTPUTTED HTML - IF YOU DO, FIX YOUR PARADIGM

paradigmDict = {'independentpronouns': independentpronouns, 'pronounsuffixes': pronounsuffixes, 'interrogatives': interrogatives} #Need to keep paradigms in here