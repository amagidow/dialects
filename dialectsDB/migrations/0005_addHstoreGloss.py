# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.postgres.operations import HStoreExtension
from django.db import models, migrations
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
        ('dialectsDB', '0004_auto_20150620_0859'),
    ]
    HStoreExtension(),
    operations = [
        migrations.AddField(
            model_name='languagedatum',
            name='multigloss',
            field=django.contrib.postgres.fields.hstore.HStoreField(null=True),
        ),
    ]
