# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dialectsDB', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contributor',
            name='defaultEncoding',
            field=models.CharField(choices=[('IPA', 'International Phonetic Alphabet'), ('BnW', 'Arabist Transcription from WAD'), ('BW', 'Buckwalter')], max_length=5, default='IPA', verbose_name='default transliteration style'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contributor',
            name='defaultLanguage',
            field=models.CharField(choices=[('IPA', 'International Phonetic Alphabet'), ('BnW', 'Arabist Transcription from WAD'), ('BW', 'Buckwalter')], max_length=5, default='en', verbose_name='default language used for glosses'),
            preserve_default=False,
        ),
    ]
