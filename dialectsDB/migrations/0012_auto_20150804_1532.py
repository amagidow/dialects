# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dialectsDB', '0011_contributor_collaborators'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contributor',
            name='collaborators',
            field=models.ManyToManyField(blank=True, help_text='note that this is NOT a symmetrical relationship- by making someone a collaborator, you are not able to see their private data', to='dialectsDB.Contributor', db_constraint='collaborators who can view your private data'),
        ),
        migrations.AlterField(
            model_name='languagedatum',
            name='sourceLocation',
            field=models.TextField(blank=True, verbose_name='location of datum in page or map number (p. or m. XX)', null=True),
        ),
    ]
