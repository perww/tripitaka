# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-14 09:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sutra', '0023_auto_20180114_1611'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ocut',
            name='col_gened',
            field=models.BooleanField(default=False, verbose_name='列输出'),
        ),
        migrations.AlterField(
            model_name='ocut',
            name='col_json',
            field=models.CharField(blank=True, max_length=200, verbose_name='列标准文件'),
        ),
        migrations.AlterField(
            model_name='ocut',
            name='col_no',
            field=models.SmallIntegerField(blank=True, default=1, verbose_name='列数'),
        ),
        migrations.AlterField(
            model_name='ocut',
            name='cut_code',
            field=models.CharField(blank=True, max_length=20, verbose_name='切分编码'),
        ),
        migrations.AlterField(
            model_name='ocut',
            name='cut_gened',
            field=models.BooleanField(default=False, verbose_name='输出'),
        ),
        migrations.AlterField(
            model_name='ocut',
            name='cut_json',
            field=models.CharField(blank=True, max_length=200, verbose_name='切分标准文件'),
        ),
        migrations.AlterField(
            model_name='ocut',
            name='cut_ori',
            field=models.CharField(blank=True, max_length=200, verbose_name='切分源文件'),
        ),
        migrations.AlterField(
            model_name='ocut',
            name='v_no',
            field=models.SmallIntegerField(blank=True, default=0, verbose_name='册号'),
        ),
        migrations.AlterField(
            model_name='ocut',
            name='v_page_no',
            field=models.SmallIntegerField(blank=True, default=0, verbose_name='正文页码'),
        ),
        migrations.AlterField(
            model_name='oimg',
            name='v_page_no',
            field=models.SmallIntegerField(blank=True, default=0, verbose_name='正文页码'),
        ),
    ]
