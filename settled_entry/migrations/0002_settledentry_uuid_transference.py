# Generated by Django 5.0.6 on 2024-05-19 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settled_entry', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='settledentry',
            name='uuid_transference',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]
