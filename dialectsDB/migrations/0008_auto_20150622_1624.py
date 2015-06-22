# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dialectsDB', '0007_auto_20150622_1606'),
    ]

    operations = [
        migrations.AddField(
            model_name='biblioentrybibtex',
            name='publisher',
            field=models.TextField(verbose_name='publisher', blank=True),
        ),
        migrations.AddField(
            model_name='biblioentrybibtex',
            name='secondauthor',
            field=models.TextField(verbose_name='editors or other authors', blank=True),
        ),
        migrations.AddField(
            model_name='biblioentrybibtex',
            name='secondtitle',
            field=models.TextField(verbose_name='journal or volume title', blank=True),
        ),
        migrations.AddField(
            model_name='biblioentrybibtex',
            name='volume',
            field=models.TextField(verbose_name='journal volume:issue or book', blank=True),
        ),
        migrations.AlterField(
            model_name='biblioentrybibtex',
            name='author',
            field=models.TextField(verbose_name='author(s)', blank=True),
        ),
        migrations.AlterField(
            model_name='biblioentrybibtex',
            name='title',
            field=models.TextField(verbose_name='title of work', blank=True),
        ),
    ]
