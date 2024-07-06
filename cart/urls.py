from django.urls import path
from .views import *

urlpatterns = [
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('sync/', sync_cart, name='sync_cart'),
    path('count/', CartCountView.as_view(), name='cart_count'),
    path('', CartDetailView.as_view(), name='cart_detail'),
]
