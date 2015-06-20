# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dialectsDB', '0002_auto_20150616_0845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contributor',
            name='defaultLanguage',
            field=models.CharField(choices=[('en', 'English'), ('fr', 'French'), ('de', 'German')], verbose_name='default language used for glosses', max_length=5),
        ),
    ]
