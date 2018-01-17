# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-04 14:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sutra', '0010_auto_20180103_0548'),
    ]

    operations = [
        migrations.CreateModel(
            name='LQSutra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=128)),
                ('name', models.CharField(max_length=128)),
                ('total_reel_no', models.IntegerField(blank=True, default=0)),
            ],
        ),
        migrations.AddField(
            model_name='page',
            name='column_ready',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='page',
            name='cut_ready',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='page',
            name='image_ready',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='page',
            name='ready',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='page',
            name='txt_ready',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='reel',
            name='column_ready',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='reel',
            name='cut_ready',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='reel',
            name='image_ready',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='reel',
            name='ready',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='reel',
            name='txt_ready',
            field=models.BooleanField(default=False),
        ),
    ]
