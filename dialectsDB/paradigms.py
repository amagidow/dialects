__author__ = 'Alex'
from dialectsDB.models import LanguageDatum
from dialectsDB import utilityfuncs


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
    #If inherit is false, top-level columns (and rows?) are NOT inherited for purposes of glossing- this makes it easier when glosses don't differ
    #If inherit is true, top-level colunns are inherited for purposes of glossing. Look at 'pronoun suffixes' versus 'demonstratives' to understand the difference
    def __init__(self, paradigmname, sharedtags, columns, rows, glosses, glosslang="en", annotation =True, subcolumns=True,subrows=True, inherit = False):
        self.paradigmname = paradigmname
        #self.paradigmnid = paradigmid #TIMPORTNANT: his should be identical to the variable name!!!
        self.sharedtags = sharedtags
        self.annotation = annotation
        self.subcolumns= subcolumns
        self.subrows = subrows
        self.columns = columns
        self.rows = rows
        self.inherit = inherit #If inherit is false, top-level columns (and rows?) are NOT inherited for purposes of glossing
        self.glosses = {}
        for key, value in glosses.items(): #makes all keys alphabetized
            #print("Key: {}, value: {}".format(key, value))
            newKey = list(filter(None,key.split("_")))
            newKey.sort() #this doesn't return anything
            #print("New key:{}".format(newKey))
            newKey = "_".join(newKey)
           # print("New key:{}".format(newKey))
            self.glosses.update({newKey : value})
        self.glosslang = glosslang

    def getGloss(self,tags):
        tags.sort()
        tags = list(filter(None,tags))
        #print("Tags in getGloss:{}".format(tags))
        if "_".join(tags) in self.glosses:
            return self.glosses["_".join(tags)]
        else:
            return "NoGloss"

    def getDatumsFromTags(self,dialect, tags, user=None): #utilty function for in templates
        #print("DialectCode is: {}".format(dialect))
        dialect = dialect.strip() #clear whitespace
        #Add User argument with default "none", hit the permission function first, filter on that
        myQuery = utilityfuncs.permissionwrapper(user)
        myQuery = myQuery.filter(dialect__dialectCode=dialect) #Need to have some user filtering here
        #print("Base languageDatum: {}".format(str(myQuery).encode('ascii', errors='backslashreplace')))
        tags = set(tags)
        tags = filter(None, tags) #remove blanks
        #print("Tags to Retrieve are: {}".format(tags))
        #print("getDatumFromTags:{}".format(tags))
        for tag in tags:
            tag = tag.strip()
            myQuery = myQuery.filter(entryTags__tagText=tag)
            #print("QueryReturned: {}".format(str(myQuery).encode('ascii', errors='backslashreplace')))
        return myQuery


pronounsuffixes = StructuredTable(paradigmname="Pronoun Suffixes", glosslang="en", sharedtags= ['closed-class', 'pronoun.suffix'],
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
                   TableAxis("2nd Person","person.2", subheaders=[
                       TableAxis("Masculine", "masculine"),
                       TableAxis("Feminine", "feminine")
                   ]),
                   TableAxis("3rd Person","person.3", subheaders=[
                       TableAxis("Masculine", "masculine"),
                       TableAxis("Feminine", "feminine")
                   ]),
               ],
                #In this case, it's very inconvenient to have different glosses for different super-headers
               glosses={#underscore connected tag lists, but will be alphabetized so always works the same
                   "singular_1st-person" : "My",
                   "plural_1st-person" : "Our",
                   "singular_person.2_masculine" : "Your (m.)",
                   "singular_person.2_feminine" : "Your (f.)",
                   "plural_person.2_masculine" : "You all's (m.)",
                   "plural_person.2_feminine" : "You all's (f.)",
                   "singular_person.3_masculine" : "His",
                   "singular_person.3_feminine" : "Her",
                   "plural_person.3_masculine" : "Their (m.)",
                   "plural_person.3_feminine" : "Their (f.)",
                        }
                )
independentpronouns = StructuredTable(paradigmname="Independent Pronouns",  glosslang="en", sharedtags= ['closed-class', 'pronoun.independent'],
               columns= [
                    TableAxis("Singular","singular"),
                    TableAxis("Plural", "plural")
               ],
                rows = [
                   TableAxis("1st Person","1st-person"),
                   TableAxis("2nd Person","person.2", subheaders=[
                       TableAxis("Masculine", "masculine"),
                       TableAxis("Feminine", "feminine")
                   ]),
                   TableAxis("3rd Person","person.3", subheaders=[
                       TableAxis("Masculine", "masculine"),
                       TableAxis("Feminine", "feminine")
                   ]),
                ],
               glosses={
                   "singular_1st-person" : "I",
                   "plural_1st-person" : "We",
                   "singular_person.2_masculine" : "You (m.)",
                   "singular_person.2_feminine" : "You (f.)",
                   "plural_person.2_masculine" : "You all (m.)",
                   "plural_person.2_feminine" : "You all (f.)",
                   "singular_person.3_masculine" : "He",
                   "singular_person.3_feminine" : "She",
                   "plural_person.3_masculine" : "They (m.)",
                   "plural_person.3_feminine" : "They (f.)",
               })

interrogatives = StructuredTable(paradigmname="Interrogatives", glosslang="en", sharedtags=['closed-class'],
                columns=[
                    TableAxis("General", ""),
                    TableAxis("Masculine", "masculine"),
                    TableAxis("Feminine", "feminine"),
                    TableAxis("Masculine Plural", ["plural", "masculine"]),
                    TableAxis("Feminine Plural", ["plural", "feminine"])

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
                    "interr.who_masculine_plural": "Who (mp)",
                    "interr.who_feminine_plural": "Who (fp)",

                    "interr.what": "What",
                    "interr.what_masculine": "What (m)",
                    "interr.what_feminine": "What (f)",
                    "interr.what_masculine_plural": "What (mp)",
                    "interr.what_feminine_plural": "What (fp)",

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
                    "interr.which_masculine_plural": "Which (mp)",
                    "interr.which_feminine_plural": "Which (fp)",

                    "interr.polar": "Interrogative Particle",

                } #	Interrogative Particle
                )

demonstratives = StructuredTable(paradigmname="Demonstratives",  glosslang="en", sharedtags= ['closed-class'], inherit=True,
               columns= [
                    TableAxis("Proximal","demonstrative.proximal", subheaders=[
                        TableAxis("Adnominal","demonstrative.adnominal"),
                        TableAxis("Pronominal", "demonstrative.pronoun"),
                        TableAxis("Here", "demonstrative.adverb.place")
                    ]),
                    TableAxis("Distal", "demonstrative.distal",subheaders=[
                        TableAxis("Adnominal","demonstrative.adnominal"),
                        TableAxis("Pronominal", "demonstrative.pronoun"),
                        TableAxis("There", "demonstrative.adverb.place")
                    ]),
                   TableAxis("Manner", "demonstrative.adverb.manner")
               ],
                rows = [
                   TableAxis("All Genders and Nums","demonstrative.allgendersnums"),
                   TableAxis("Singular","singular", subheaders=[
                       TableAxis("Masculine", "masculine"),
                       TableAxis("Feminine", "feminine")
                   ]),
                   TableAxis("Plural","plural", subheaders=[
                       TableAxis("Masculine", "masculine"),
                       TableAxis("Feminine", "feminine")
                   ]),
                ],
                #In this case, we NEED inheritance of superheaders to properly gloss, so inherit=true
               glosses={
                   #Proximal
                    "demonstrative.proximal_demonstrative.adnominal_demonstrative.allgendersnums" : "This, these",
                    "demonstrative.proximal_demonstrative.adnominal_singular_masculine" : "This (m.)",
                    "demonstrative.proximal_demonstrative.adnominal_singular_feminine" : "This (f.)",
                    "demonstrative.proximal_demonstrative.pronoun_singular_masculine" : "This (m.)",
                    "demonstrative.proximal_demonstrative.pronoun_singular_feminine" : "This (f.)",
                    "demonstrative.proximal_demonstrative.adverb.place_demonstrative.allgendersnums" : "Here",
                    "demonstrative.proximal_demonstrative.adnominal_plural_masculine" : "These (m.)",
                    "demonstrative.proximal_demonstrative.adnominal_plural_feminine" : "These (f.)",
                    "demonstrative.proximal_demonstrative.pronoun_plural_masculine" : "These (m.)",
                    "demonstrative.proximal_demonstrative.pronoun_plural_feminine" : "These (f.)",
                   
                   #Distal
                   
                    "demonstrative.distal_demonstrative.adnominal_demonstrative.allgendersnums" : "That, those",
                    "demonstrative.distal_demonstrative.adnominal_singular_masculine" : "That (m.)",
                    "demonstrative.distal_demonstrative.adnominal_singular_feminine" : "That (f.)",
                    "demonstrative.distal_demonstrative.pronoun_singular_masculine" : "That (m.)",
                    "demonstrative.distal_demonstrative.pronoun_singular_feminine" : "That (f.)",
                    "demonstrative.distal_demonstrative.adverb.place_demonstrative.allgendersnums" : "There",
                    "demonstrative.distal_demonstrative.adnominal_plural_masculine" : "Those (m.)",
                    "demonstrative.distal_demonstrative.adnominal_plural_feminine" : "Those (f.)",
                    "demonstrative.distal_demonstrative.pronoun_plural_masculine" : "Those (m.)",
                    "demonstrative.distal_demonstrative.pronoun_plural_feminine" : "Those (f.)",

                   #Manner
                    "demonstrative.adverb.manner_demonstrative.allgendersnums" : "Thusly"

                    })

#Verbal suffixes: Want suffixes only, for sound verbs
pastverbsuffixes = StructuredTable(paradigmname="Past Tense Verb Suffixes", glosslang="en", sharedtags=['closed-class', 'tense.past', 'affix.verbal', 'suffix'],
                columns=[
                    TableAxis("Sound Verbs", "verb.sound"),
                    #TableAxis("IIIw", "verb.IIIw"),
                    #TableAxis("IIIy", "verb.IIIy"),
                    #TableAxis("Geminate", "verb.geminate")

                ],
                rows=[
                   TableAxis("First Person","person.1", subheaders=[
                       TableAxis("Singular", "singular"),
                       TableAxis("Plural", "plural")
                   ]),
                    TableAxis("2nd Singular",["person.2","singular"], subheaders=[
                        TableAxis("Masculine", ["masculine"]),
                        TableAxis("Feminine", ["feminine"]),

                   ]), #There seems to be a bug that I can only have two items per row
                    TableAxis("2nd Plural", ["person.2","plural"], subheaders=[
                        TableAxis("Masculine", ["masculine"]),
                        TableAxis("Feminine", ["feminine"]),
                             ]),
                    TableAxis("3rd Singular",["person.3","singular"], subheaders=[
                        TableAxis("Masculine", ["masculine"]),
                        TableAxis("Feminine", ["feminine"]),

                   ]),
                    TableAxis("3rd Plural", ["person.3","plural"], subheaders=[
                        TableAxis("Masculine", ["masculine"]),
                        TableAxis("Feminine", ["feminine"]),
                             ]),
                ],
                glosses={
                    "person.1_singular_verb.sound": "1s Sound Verb Suffix",
                    "person.1_plural_verb.sound": "1p Sound Verb Suffix",

                    "person.2_singular_masculine_verb.sound" : "2ms Sound Verb Suffix",
                    "person.2_singular_feminine_verb.sound" : "2fs Sound Verb Suffix",

                    "person.2_plural_masculine_verb.sound" : "2mp Sound Verb Suffix",
                    "person.2_plural_feminine_verb.sound" : "2fp Sound Verb Suffix",

                    "person.3_singular_masculine_verb.sound" : "3ms Sound Verb Suffix",
                    "person.3_singular_feminine_verb.sound" : "3fs Sound Verb Suffix",

                    "person.3_plural_masculine_verb.sound" : "3mp Sound Verb Suffix",
                    "person.3_plural_feminine_verb.sound" : "3fp Sound Verb Suffix",
                }
                )
paradigmDict = {'verbsuffixes' : pastverbsuffixes,  'independentpronouns': independentpronouns, 'pronounsuffixes': pronounsuffixes, 'interrogatives': interrogatives, 'demonstratives': demonstratives} #Need to keep paradigms in here