# Generated by Django 5.0.2 on 2024-03-19 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("application", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="parent_pin",
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
