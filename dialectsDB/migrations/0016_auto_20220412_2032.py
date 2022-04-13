# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def pointtolatlong(apps, schema_editor):
    oldDialect = apps.get_model("dialectsDB", "Dialect")
    for datum in oldDialect.objects.all():
        datum.centerLat = datum.centerLoc.coords[1] #lat is Y axis
        datum.centerLong = datum.centerLoc.coords[0] #long is X axis
        datum.save()


class Migration(migrations.Migration):

    dependencies = [
        ('dialectsDB', '0015_auto_20220412_2028'),
    ]

    operations = [
        migrations.RunPython(pointtolatlong)
    ]
