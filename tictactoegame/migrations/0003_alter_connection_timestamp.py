# Generated by Django 3.2.3 on 2021-05-23 11:18

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tictactoegame', '0002_alter_connection_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connection',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]