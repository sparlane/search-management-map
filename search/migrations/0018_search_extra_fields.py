# Generated by Django 3.0.6 on 2020-05-23 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0017_auto_20200523_2133'),
    ]

    operations = [
        migrations.AddField(
            model_name='search',
            name='search_type',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='search',
            name='first_bearing',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='search',
            name='iterations',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='search',
            name='width',
            field=models.IntegerField(null=True),
        ),
    ]
