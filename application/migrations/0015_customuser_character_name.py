# Generated by Django 5.0.2 on 2024-04-13 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("application", "0014_customuser_total_brushes_days"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="character_name",
            field=models.CharField(default="Brushy"),
        ),
    ]