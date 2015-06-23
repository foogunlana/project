# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stears', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pdf', models.FileField(upload_to=b'reports/%Y/%m/%d')),
                ('author', models.CharField(max_length=50)),
                ('industry', models.BooleanField(default=False)),
                ('summary', models.CharField(default=b'', max_length=b'200')),
                ('week_ending', models.DateField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
