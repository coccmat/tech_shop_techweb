# Generated by Django 5.0.6 on 2024-06-22 16:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0003_order_orderitem"),
    ]

    operations = [
        migrations.RenameField(
            model_name="notificationrequest",
            old_name="customer",
            new_name="user",
        ),
    ]
