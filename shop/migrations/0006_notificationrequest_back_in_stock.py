# Generated by Django 5.0.6 on 2024-06-29 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0005_alter_notificationrequest_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="notificationrequest",
            name="back_in_stock",
            field=models.BooleanField(default=True),
        ),
    ]
