# Generated by Django 5.0.6 on 2024-07-05 13:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0013_orderitem_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="image",
            field=models.ImageField(default="default.jpg", upload_to="prod_images/"),
        ),
        migrations.AlterField(
            model_name="product",
            name="price",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(0.01)],
            ),
        ),
        migrations.AlterField(
            model_name="review",
            name="rating",
            field=models.IntegerField(
                default=1,
                validators=[
                    django.core.validators.MinValueValidator(0.0),
                    django.core.validators.MaxValueValidator(5.0),
                ],
            ),
        ),
    ]