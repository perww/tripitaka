# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-02 01:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=128)),
                ('name', models.CharField(max_length=128)),
                ('img_path', models.CharField(max_length=128)),
            ],
            options={
                'verbose_name': '页',
                'verbose_name_plural': '页',
            },
        ),
        migrations.CreateModel(
            name='Reel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=128)),
                ('name', models.CharField(max_length=128)),
            ],
            options={
                'verbose_name': '卷',
                'verbose_name_plural': '卷',
            },
        ),
        migrations.CreateModel(
            name='Sutra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=128)),
                ('name', models.CharField(max_length=128)),
            ],
            options={
                'verbose_name': '经名',
                'verbose_name_plural': '经名',
            },
        ),
        migrations.AddField(
            model_name='reel',
            name='sutra',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sutra.Sutra'),
        ),
        migrations.AddField(
            model_name='page',
            name='Reel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sutra.Reel'),
        ),
    ]
