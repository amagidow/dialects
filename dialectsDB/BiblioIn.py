__author__ = 'Alex'
import bibtexparser, sys, os, codecs

import django
django.setup()
from dialectsDB.models import BiblioEntryBibTex
from bibtexparser.bwriter import BibTexWriter

def bibTexIn(filename):
    #load database into bibtexdatabase object
    with codecs.open(filename, 'r', 'utf-8') as bibtex_file:
        bibtex_database = bibtexparser.load(bibtex_file)

    #load all the keys we want to add into the dialectsDB database
    dbbibtexkeys = [x.bibTexKey for x in BiblioEntryBibTex.objects.all()]
    btdbdict = bibtex_database.entries_dict

    for item in dbbibtexkeys:
        try:
            currentbtitem = btdbdict[item]
            currentBEobject = BiblioEntryBibTex.objects.get(bibTexKey=item)
            writer = BibTexWriter()
            bibtexofentry = writer._entry_to_bibtex(currentbtitem)
            currentBEobject.bibTexKey = bibtexofentry
        except KeyError:
            pass






