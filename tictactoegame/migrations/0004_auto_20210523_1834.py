# Generated by Django 3.2.3 on 2021-05-23 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tictactoegame', '0003_alter_connection_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connection',
            name='p1',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='connection',
            name='p2',
            field=models.CharField(max_length=200),
        ),
    ]
