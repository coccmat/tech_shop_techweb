# Generated by Django 5.0.6 on 2024-07-02 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0010_alter_product_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="notificationrequest",
            name="read",
            field=models.BooleanField(default=False),
        ),
    ]
