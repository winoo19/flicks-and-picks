# Generated by Django 4.2.11 on 2024-05-05 09:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_remove_review_unique_combination_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="film",
            name="image_url",
            field=models.CharField(max_length=200, null=True),
        ),
    ]
