# Generated by Django 2.2.6 on 2019-10-12 01:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0002_auto_20191012_1337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timelineentry',
            name='url',
            field=models.TextField(blank=True, null=True),
        ),
    ]