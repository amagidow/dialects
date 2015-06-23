__author__ = 'Alex'
#This function works pretty well, but does not seem to load from within pycharm. Had to do it at console.
import bibtexparser, codecs

import django
django.setup()

from dialectsDB.models import BiblioEntryBibTex
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.customization import convert_to_unicode

def bibTexIn(filename):
    #load database into bibtexdatabase object
    with codecs.open(filename, 'r', 'utf-8') as bibtex_file:
        parser = BibTexParser()
        parser.customization = convert_to_unicode
        bibtex_database = bibtexparser.load(bibtex_file,parser)

    #load all the keys we want to add into the dialectsDB database
    dbbibtexkeys = [x.bibTexKey for x in BiblioEntryBibTex.objects.all()]
    btdbdict = bibtex_database.entries_dict

    for item in dbbibtexkeys:
        try:
            currentbtitem = btdbdict[item]
            currentBEobject = BiblioEntryBibTex.objects.get(bibTexKey=item)
            writer = BibTexWriter()
            bibtexofentry = writer._entry_to_bibtex(currentbtitem)
            currentBEobject.fullBibtex = bibtexofentry
            print("Currently saving: {}".format(item))
            currentBEobject.save() #The saving function should put the relevant info into the other fields
        except KeyError:
            print("No bibliography entry for: {}".format(item))



bibTexIn("D:\\Dropbox\\AlexDocs\\bibtex\\Arabic.bib")



