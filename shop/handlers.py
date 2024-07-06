
from django.dispatch import receiver
from .signals import product_restocked, sale_confirmation
from .models import NotificationRequest, OrderItem, Sale


'''update of the notification status'''
@receiver(product_restocked)
def notify_product_back_in_stock(product, **kwargs):
    NotificationRequest.objects.filter(product=product).update(back_in_stock=True)

'''create a sale *ONLY* when reciving a confirmation signal from Vendors'''
@receiver(sale_confirmation)
def create_sale(sender, instance, vendor, **kwargs):
        Sale.objects.create(
            sold_item=instance,
            vendor=vendor 

        )