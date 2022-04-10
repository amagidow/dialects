# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dialectsDB', '0008_auto_20150622_1624'),
    ]

    operations = [
        migrations.AlterField(
            model_name='biblioentrybibtex',
            name='date',
            field=models.CharField(null=True, blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='biblioentrybibtex',
            name='volume',
            field=models.TextField(blank=True, verbose_name='journal volume:issue or book volume'),
        ),
    ]
