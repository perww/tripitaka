# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-06 12:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sutra', '0014_auto_20180106_2050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sutra',
            name='tripitaka',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sutras', to='sutra.Tripitaka'),
        ),
    ]
