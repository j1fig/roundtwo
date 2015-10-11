# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('optimo', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aircraft',
            name='taxi_speed',
        ),
        migrations.AddField(
            model_name='node',
            name='latitude',
            field=models.DecimalField(default=0, max_digits=13, decimal_places=10),
        ),
        migrations.AddField(
            model_name='node',
            name='longitude',
            field=models.DecimalField(default=0, max_digits=13, decimal_places=10),
        ),
        migrations.AddField(
            model_name='node',
            name='type',
            field=models.CharField(default=b'move', max_length=10, choices=[(b'gate', b'gate'), (b'move', b'move'), (b'hold', b'hold'), (b'depart', b'depart')]),
        ),
    ]
