from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from .signals import product_restocked
from .enum import CategoryEnum, StatusEnum



class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(validators=[MinValueValidator(0.01)],max_digits=10, decimal_places=2,)
    stock = models.IntegerField(default=0,validators=[MinValueValidator(0)])
    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor_products')
    category =  models.CharField(choices=CategoryEnum, max_length=20, default=CategoryEnum.MORE)
    image = models.ImageField(upload_to='prod_images/',default='prod_images/default.jpg')
    def __str__(self):
        return self.name
    '''method override to send the restock signal when updated'''
    def save(self, *args, **kwargs):
        if self.pk is not None:
            original = Product.objects.get(pk=self.pk)
            if original.stock == 0 and self.stock > 0:
                print(f"original stock = {original.stock} self.stok ={self.stock}")
                product_restocked.send(sender=self.__class__, product=self)
        super().save(*args, **kwargs)


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f'Order {self.id}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=10, choices=StatusEnum.choices, default=StatusEnum.PENDING)


    def __str__(self):
        return f'OrderItem {self.id}'


class Sale(models.Model):
    sold_item=models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='items')
    date = models.DateTimeField(auto_now_add=True)
    vendor=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor_sales')

    def __str__(self):
        return f'Sale of {self.product.name} on {self.date}'

   
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(default=1, validators=[
                                MinValueValidator(0), MaxValueValidator(5)], )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.customer.name}"




class NotificationRequest(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    requested_at = models.DateTimeField(auto_now_add=True)
    back_in_stock=models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    def __str__(self):
        return f"The product {self.product.name}, you've been following is now back on stock"
    class Meta: 
        verbose_name_plural = "notifications"
        unique_together = (('product', 'user'),)

