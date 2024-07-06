from django.db import models

class CategoryEnum(models.TextChoices):
    SMARTPHONES = 'Smartphones'
    LAPTOPS = 'Laptops'
    TABLETS = 'Tablets'
    TELEVISIONS = 'Televisions'
    CAMERAS = 'Cameras'
    HEADPHONES = 'Headphones'
    SMARTWATCHES = 'Smartwatches'
    GAMING_CONSOLES = 'Gaming Consoles'
    DRONES = 'Drones'
    ACCESSORIES = 'Accessories'
    MORE = 'More'


class StatusEnum(models.TextChoices):
    PENDING = 'Pending', 'pending'
    CONFIRMED = 'Confirmed', 'confirmed'