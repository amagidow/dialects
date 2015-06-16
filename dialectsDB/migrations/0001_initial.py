# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BiblioEntryBibTex',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('bibTexKey', models.CharField(max_length=50, unique=True)),
                ('date', models.SmallIntegerField(blank=True, null=True, max_length=4)),
                ('author', models.TextField(blank=True, verbose_name='author(s), multiple names separated by ;')),
                ('title', models.TextField(blank=True, verbose_name='Optionally include title of work')),
                ('annotation', models.TextField(blank=True, verbose_name='additional annotations')),
                ('fullBibtex', models.TextField(blank=True, verbose_name='Full Bibtex entry')),
            ],
            options={
                'ordering': ['bibTexKey'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Contributor',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('blurb', models.CharField(blank=True, max_length=500)),
                ('physicalAddress', models.CharField(blank=True, verbose_name='physical academic address', max_length=500)),
                ('defaultPermission', models.CharField(verbose_name='default permission setting for data input', max_length=8, choices=[('Public', 'Fully public'), ('PubNoE', 'Public no export'), ('Private', 'Private, viewable only by uploader')])),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Dialect',
            fields=[
                ('dialectCode', models.CharField(verbose_name='short code for location', serialize=False, max_length=10, unique=True, primary_key=True)),
                ('dialectNameEn', models.TextField(verbose_name='human readable name of the dialect')),
                ('locationName', models.TextField(blank=True, verbose_name='human readable location name')),
                ('locationNameAr', models.TextField(blank=True, verbose_name='Arabic name of location if available')),
                ('centerLoc', django.contrib.gis.db.models.fields.PointField(srid=4326, verbose_name='a point representing this dialect')),
                ('regionLoc', django.contrib.gis.db.models.fields.MultiPolygonField(blank=True, srid=4326, null=True, verbose_name='multipolygon geometry')),
            ],
            options={
                'ordering': ['dialectCode'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DialectTag',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('tagText', models.CharField(verbose_name='Tag: Tags may have parts separated by . or -, but not _', max_length=50, unique=True)),
                ('tagExplanation', models.TextField(verbose_name='Tag Explanation')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EntryTag',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('tagText', models.CharField(verbose_name='Tag: Tags may have parts separated by . or -, but not _', max_length=50, unique=True)),
                ('tagExplanation', models.TextField(verbose_name='Tag Explanation')),
            ],
            options={
                'abstract': False,
                'ordering': ['tagText'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LanguageDatum',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('normalizedEntry', models.TextField(verbose_name='arabic language entry in normalized roman format')),
                ('normalizationStyle', models.CharField(max_length=5, choices=[('IPA', 'International Phonetic Alphabet'), ('BnW', 'Arabist Transcription from WAD'), ('BW', 'Buckwalter')])),
                ('originalOrthography', models.TextField(blank=True, verbose_name='arabic language entry in the original orthography in the source')),
                ('gloss', models.TextField(verbose_name='brief translation of entry')),
                ('annotation', models.TextField(blank=True, verbose_name='additional information on the entry')),
                ('sourceLocation', models.TextField(null=True, verbose_name='location of datum in page or map number (p. or m. XX)')),
                ('permissions', models.CharField(max_length=8, choices=[('Public', 'Fully public'), ('PubNoE', 'Public no export'), ('Private', 'Private, viewable only by uploader')])),
                ('contributor', models.ForeignKey(to='dialectsDB.Contributor')),
                ('dialect', models.ForeignKey(to='dialectsDB.Dialect')),
                ('entryTags', models.ManyToManyField(blank=True, null=True, to='dialectsDB.EntryTag')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LingRelationship',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('entryIsRelated', models.ForeignKey(related_name='+', to='dialectsDB.LanguageDatum')),
                ('entryRelatedTo', models.ForeignKey(related_name='+', to='dialectsDB.LanguageDatum')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RelateTag',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('tagText', models.CharField(verbose_name='Tag: Tags may have parts separated by . or -, but not _', max_length=50, unique=True)),
                ('tagExplanation', models.TextField(verbose_name='Tag Explanation')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='lingrelationship',
            name='relateTag',
            field=models.ForeignKey(to='dialectsDB.RelateTag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='languagedatum',
            name='lingRelationship',
            field=models.ManyToManyField(blank=True, to='dialectsDB.LanguageDatum', through='dialectsDB.LingRelationship', related_name='relationships'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='languagedatum',
            name='sourceDoc',
            field=models.ForeignKey(null=True, to='dialectsDB.BiblioEntryBibTex'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dialect',
            name='dialectTag',
            field=models.ManyToManyField(blank=True, null=True, to='dialectsDB.DialectTag'),
            preserve_default=True,
        ),
    ]
