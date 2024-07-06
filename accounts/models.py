from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError
from .admin import *

''' kindly suggested in the django guiede to model better users (-:'''

class ShopUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = ShopUsersManager()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
