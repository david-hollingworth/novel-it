from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class AuthenticationTests(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_login_functionality(self):
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_logout_functionality(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(reverse('logout')) # My logout is a POST form
        self.assertRedirects(response, reverse('login'))
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_registration_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_registration_functionality(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password': 'newpassword123',
            'password_confirm': 'newpassword123' # Standard UserCreationForm fields? No, it's password1 and password2
        }, follow=True) # UserCreationForm fields are usually username, password1, password2
        # Let's check the form or just use valid data
        response = self.client.post(reverse('register'), {
            'username': 'newuser2',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(User.objects.filter(username='newuser2').exists())
