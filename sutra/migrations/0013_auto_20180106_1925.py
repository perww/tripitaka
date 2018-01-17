# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-06 11:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('sutra', '0012_auto_20180105_1312'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lqsutra',
            options={'verbose_name': '龙泉经目', 'verbose_name_plural': '龙泉经目管理'},
        ),
        migrations.AlterModelOptions(
            name='sutra',
            options={'verbose_name': '实体经目', 'verbose_name_plural': '实体经目管理'},
        ),
        migrations.AlterModelOptions(
            name='tripitaka',
            options={'verbose_name': '实体藏经', 'verbose_name_plural': '实体藏经管理'},
        ),
        migrations.RemoveField(
            model_name='lqsutra',
            name='id',
        ),
        migrations.RemoveField(
            model_name='lqsutra',
            name='total_reel_no',
        ),
        migrations.RemoveField(
            model_name='sutra',
            name='qianziwen',
        ),
        migrations.RemoveField(
            model_name='sutra',
            name='total_reel_no',
        ),
        migrations.RemoveField(
            model_name='tripitaka',
            name='id',
        ),
        migrations.AddField(
            model_name='lqsutra',
            name='total_reels',
            field=models.IntegerField(blank=True, default=1, verbose_name='总卷数'),
        ),
        migrations.AddField(
            model_name='sutra',
            name='lqsutra',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sutra.LQSutra', verbose_name='龙泉经目编码'),
        ),
        migrations.AddField(
            model_name='sutra',
            name='sid',
            field=models.CharField(default=django.utils.timezone.now, max_length=32, verbose_name='实体藏经|唯一经号编码'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sutra',
            name='total_reels',
            field=models.IntegerField(blank=True, default=1, verbose_name='总卷数'),
        ),
        migrations.AddField(
            model_name='sutra',
            name='variant_code',
            field=models.CharField(default='0', max_length=1, verbose_name='别本编码'),
        ),
        migrations.AlterField(
            model_name='lqsutra',
            name='code',
            field=models.CharField(max_length=8, primary_key=True, serialize=False, verbose_name='龙泉经目编码'),
        ),
        migrations.AlterField(
            model_name='lqsutra',
            name='name',
            field=models.CharField(max_length=64, verbose_name='龙泉经目名称'),
        ),
        migrations.AlterField(
            model_name='sutra',
            name='code',
            field=models.CharField(max_length=5, verbose_name='实体经目编码'),
        ),
        migrations.AlterField(
            model_name='sutra',
            name='name',
            field=models.CharField(blank=True, max_length=64, verbose_name='实体经目名称'),
        ),
        migrations.AlterField(
            model_name='sutra',
            name='tripitaka',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sutras', to='sutra.Tripitaka'),
        ),
        migrations.AlterField(
            model_name='tripitaka',
            name='code',
            field=models.CharField(max_length=4, primary_key=True, serialize=False, verbose_name='实体藏经版本编码'),
        ),
        migrations.AlterField(
            model_name='tripitaka',
            name='name',
            field=models.CharField(max_length=32, verbose_name='实体藏经名称'),
        ),
    ]