# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2018-11-11 11:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HealthModel', '0008_membership_deleteadminuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='membershipType',
            field=models.CharField(default='0', max_length=1),
        ),
    ]
