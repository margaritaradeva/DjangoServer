# Generated by Django 5.0.2 on 2024-04-04 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("application", "0008_customuser_last_active_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="last_active_evening",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="customuser",
            name="last_active_morning",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="customuser",
            name="max_streak_evening",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="customuser",
            name="max_streak_morning",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="customuser",
            name="streak_evening",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="customuser",
            name="streak_morning",
            field=models.IntegerField(default=0),
        ),
    ]
