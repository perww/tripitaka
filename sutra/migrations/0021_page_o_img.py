# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-14 06:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sutra', '0020_auto_20180114_1247'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='o_img',
            field=models.ForeignKey(blank=True, default='cee749df430448c9a6134c2915505be6', on_delete=django.db.models.deletion.CASCADE, to='sutra.OImg'),
            preserve_default=False,
        ),
    ]
