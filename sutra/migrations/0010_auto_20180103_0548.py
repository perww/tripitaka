# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-02 21:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('sutra', '0009_auto_20171228_1423'),
    ]

    operations = [
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sub_date', models.DateField()),
                ('org', models.CharField(max_length=128)),
                ('des', models.CharField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='Column',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=128)),
                ('img_path', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='OCut',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=128)),
                ('cut_data', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='OTxt',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=128)),
                ('txt', models.TextField(blank=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='line',
            name='page',
        ),
        migrations.RemoveField(
            model_name='page',
            name='cut_data',
        ),
        migrations.RemoveField(
            model_name='page',
            name='txt',
        ),
        migrations.AlterField(
            model_name='page',
            name='r_page_no',
            field=models.IntegerField(blank=True, default=1),
        ),
        migrations.DeleteModel(
            name='Line',
        ),
        migrations.AddField(
            model_name='otxt',
            name='page',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sutra.Page'),
        ),
        migrations.AddField(
            model_name='ocut',
            name='page',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sutra.Page'),
        ),
        migrations.AddField(
            model_name='column',
            name='page',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sutra.Page'),
        ),
    ]
