# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dialectsDB', '0013_dialect_dialectcodedisplay'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dialect',
            name='dialectCodeDisplay',
            field=models.CharField(verbose_name='changeable code for location', max_length=10, unique=True),
        ),
    ]
