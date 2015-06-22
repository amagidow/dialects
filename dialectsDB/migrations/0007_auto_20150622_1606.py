# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
        ('dialectsDB', '0006_populateMultiGloss'),
    ]

    operations = [
        migrations.AlterField(
            model_name='languagedatum',
            name='multigloss',
            field=django.contrib.postgres.fields.hstore.HStoreField(verbose_name='multi-lingual gloss', default= {'en':'MULTIGLOSSFAIL'}),
            preserve_default=False,
        ),
    ]
