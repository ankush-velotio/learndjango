# Generated by Django 3.2.6 on 2021-08-16 05:23

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0003_todo_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todo',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='todo',
            name='editors',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=100), blank=True, null=True, size=5),
        ),
        migrations.AlterField(
            model_name='todo',
            name='updated_by',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
