# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dialectsDB', '0009_auto_20150622_1732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='biblioentrybibtex',
            name='bibTexKey',
            field=models.CharField(unique=True, max_length=100),
        ),
    ]
