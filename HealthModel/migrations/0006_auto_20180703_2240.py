# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2018-07-03 22:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HealthModel', '0005_doctorinfo_rank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='productprice',
            field=models.FloatField(),
        ),
    ]