# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dialectsDB', '0016_auto_20220412_2032'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dialect',
            name='centerLoc',
        ),
        migrations.RemoveField(
            model_name='dialect',
            name='regionLoc',
        ),
    ]
