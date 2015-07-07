# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stears', '0003_reportmodel_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='articleimagemodel',
            name='description',
            field=models.CharField(default=b'', max_length=100),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='articleimagemodel',
            name='source',
            field=models.CharField(default=b'', max_length=100),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='articleimagemodel',
            name='title',
            field=models.CharField(default=b'', max_length=50),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='reportmodel',
            name='summary',
            field=models.CharField(default=b'', max_length=200),
        ),
    ]
