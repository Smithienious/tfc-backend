# Generated by Django 3.2.6 on 2021-08-24 02:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('master_db', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='log',
            name='table',
        ),
        migrations.RemoveField(
            model_name='log',
            name='user',
        ),
        migrations.DeleteModel(
            name='Metatable',
        ),
    ]
