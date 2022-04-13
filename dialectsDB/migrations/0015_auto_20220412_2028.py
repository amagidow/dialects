# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dialectsDB', '0014_auto_20171108_1554'),
    ]

    operations = [
        migrations.AddField(
            model_name='dialect',
            name='centerLat',
            field=models.FloatField(verbose_name='Latitude of center', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dialect',
            name='centerLong',
            field=models.FloatField(verbose_name='Longitude of center', blank=True, null=True),
        ),
    ]
