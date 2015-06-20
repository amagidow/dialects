# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dialectsDB', '0003_auto_20150619_1109'),
    ]

    operations = [
        migrations.AddField(
            model_name='contributor',
            name='affiliation',
            field=models.CharField(verbose_name='academic affiliation', max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='contributor',
            name='webaddress',
            field=models.URLField(verbose_name='academic website', blank=True),
        ),
    ]
