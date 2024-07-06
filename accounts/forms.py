from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import ShopUser

ACCOUNT_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
    )

class CustomUserCreationForm(UserCreationForm):
    
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE_CHOICES, required=True)

    class Meta:
        model = ShopUser
        fields = ('first_name', 'last_name', 'email',  'account_type')

class CustomUserChangeForm(UserChangeForm):
    
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE_CHOICES, required=True)

    class Meta:
        model = ShopUser
        fields = ('first_name', 'last_name', 'email',  'account_type')