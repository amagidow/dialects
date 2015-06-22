# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def glossToMulti(apps, schema_editor):
    LanguageDatum = apps.get_model("dialectsDB", "LanguageDatum")
    for datum in LanguageDatum.objects.all():
        datum.multigloss = {"en" : datum.gloss}
        datum.save()

class Migration(migrations.Migration):

    dependencies = [
        ('dialectsDB', '0005_addHstoreGloss'),
    ]

    operations = [
        migrations.RunPython(glossToMulti)
    ]
