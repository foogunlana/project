# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stears', '0002_reportmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportmodel',
            name='title',
            field=models.CharField(default=b'', max_length=50),
            preserve_default=True,
        ),
    ]
