from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.messages import get_messages
from django.conf import settings
from .models import Product, Order, OrderItem, StatusEnum
from cart.cart import SessionCart

User = get_user_model()

class CreateOrderViewTests(TestCase):

    def setUp(self):
        # Create test user and add to "Customers" group
        self.user = User.objects.create_user(
            
            email='testuser@example.com',
            password='testpassword'
        )
        self.customers_group = Group.objects.create(name='Customers')
        self.user.groups.add(self.customers_group)

        # Create another user and add to "Vendors" group
        self.vendor = User.objects.create_user(
            
            email='vendoruser@example.com',
            password='testpassword'
        )
        self.vendors_group = Group.objects.create(name='Vendors')
        self.vendor.groups.add(self.vendors_group)

        # Create a test product
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=10.00,
            stock=5,
            vendor=self.vendor,
            category='Electronics',
            image='prod_images/default.jpg'
        )
        
        self.create_order_url = reverse('create_order')
        
        # Mock the session cart
        self.cart_data = {'quantity': 3, 'price': str(self.product.price)}
        self.session = self.client.session
        self.session[settings.CART_SESSION_ID] = {str(self.product.id): self.cart_data}
        self.session.save()

    def test_access_view_as_authenticated_customer(self):
        self.client.login(email='vendoruser@example.com', password='testpassword')
        response = self.client.post(self.create_order_url, data={})
        self.assertEqual(response.status_code, 302)  # Should redirect after post

    def test_access_view_as_authenticated_vendor(self):
        self.client.login(email='vendoruser@example.com', password='testpassword')
        response = self.client.post(self.create_order_url, data={})
        self.assertEqual(response.status_code, 302)  # Should redirect after post

    def test_access_view_as_unauthenticated_user(self):
        response = self.client.post(self.create_order_url, data={})
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertRedirects(response, f'/accounts/login/?next={self.create_order_url}')

    def test_create_order_with_sufficient_stock(self):
        self.client.login(email='testuser@example.com', password='testpassword')
        
        response = self.client.post(self.create_order_url, data={})
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertRedirects(response, reverse('order_detail', kwargs={'order_id': Order.objects.first().pk}))
        order = Order.objects.get(user=self.user)
        self.assertTrue(OrderItem.objects.filter(order=order, product=self.product).exists())
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2) 

    def test_create_order_with_insufficient_stock(self):
        self.client.login(email='testuser@example.com', password='testpassword')
        # Update cart to exceed stock
        session = self.client.session
        session[settings.CART_SESSION_ID] = {str(self.product.id): {'quantity': 10, 'price': str(self.product.price)}}
        session.save()
        response = self.client.post(self.create_order_url, data={})
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, reverse('product_detail', kwargs={'pk': self.product.pk}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "You have tried to order 10 but there's only 5 in stock")
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5) 
