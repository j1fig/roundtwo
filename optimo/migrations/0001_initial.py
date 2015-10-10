# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Aircraft',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('model_name', models.CharField(max_length=255)),
                ('flight_number', models.CharField(max_length=255)),
                ('percentage', models.DecimalField(default=0, max_digits=10, decimal_places=9)),
                ('linear_speed', models.DecimalField(default=0, max_digits=20, decimal_places=10)),
                ('heading', models.DecimalField(default=0, max_digits=10, decimal_places=3)),
                ('taxi_speed', models.DecimalField(default=7.71666667, max_digits=20, decimal_places=10)),
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.AddField(
            model_name='aircraft',
            name='course',
            field=models.ManyToManyField(to='optimo.Node'),
        ),
        migrations.AddField(
            model_name='aircraft',
            name='destination',
            field=models.ForeignKey(related_name='destination', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='optimo.Node', null=True),
        ),
        migrations.AddField(
            model_name='aircraft',
            name='last_node',
            field=models.ForeignKey(related_name='last_node', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='optimo.Node', null=True),
        ),
        migrations.AddField(
            model_name='aircraft',
            name='next_node',
            field=models.ForeignKey(related_name='next_node', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='optimo.Node', null=True),
        ),
    ]
