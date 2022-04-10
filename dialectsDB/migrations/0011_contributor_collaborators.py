# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dialectsDB', '0010_auto_20150623_0837'),
    ]

    operations = [
        migrations.AddField(
            model_name='contributor',
            name='collaborators',
            field=models.ManyToManyField(to='dialectsDB.Contributor', db_constraint='collaborators who can view your private data', help_text='note that this is NOT a symmetrical relationship- by making someone a collaborator, you are not able to see their private data'),
        ),
    ]
