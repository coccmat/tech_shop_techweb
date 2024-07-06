from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.messages import get_messages
# Create your tests here.

User = get_user_model()

class SignUpViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('signup')
        Group.objects.create(name='Customers')
        Group.objects.create(name='Vendors')

    def test_signup_view_get(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')

    def test_signup_view_post_customer(self):
        response = self.client.post(self.signup_url, {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'account_type': 'customer'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

        user = User.objects.get(email='john.doe@example.com')
        self.assertTrue(user.groups.filter(name='Customers').exists())

    def test_signup_view_post_vendor(self):
        response = self.client.post(self.signup_url, {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane.doe@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'account_type': 'vendor'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

        user = User.objects.get(email='jane.doe@example.com')
        self.assertTrue(user.groups.filter(name='Vendors').exists())




class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            password='testpassword123'
        )

    def test_login_view_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_view_post(self):
        response = self.client.post(self.login_url, {
            'username': 'john.doe@example.com',
            'password': 'testpassword123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('product_list'))