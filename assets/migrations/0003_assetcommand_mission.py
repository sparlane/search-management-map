# Generated by Django 2.2.6 on 2019-10-15 10:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mission', '0001_initial'),
        ('assets', '0002_assetcommand'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetcommand',
            name='mission',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='mission.Mission'),
        ),
    ]
