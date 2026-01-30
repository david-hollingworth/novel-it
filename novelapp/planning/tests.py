from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from novels.models import Novel
from .models import Character, Location, Item

class PlanningScopingTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')
        self.novel1 = Novel.objects.create(user=self.user1, title='User 1 Novel')
        self.novel2 = Novel.objects.create(user=self.user2, title='User 2 Novel')
        self.char1 = Character.objects.create(novel=self.novel1, fullname='Char 1')
        self.char2 = Character.objects.create(novel=self.novel2, fullname='Char 2')

    def test_character_list_scoping(self):
        self.client.login(username='user1', password='pass1')
        response = self.client.get(reverse('character_list', kwargs={'novel_pk': self.novel1.pk}))
        self.assertContains(response, 'Char 1')
        self.assertNotContains(response, 'Char 2')

    def test_character_detail_access_scoping(self):
        self.client.login(username='user1', password='pass1')
        # Access own character
        response = self.client.get(reverse('character_detail', kwargs={'novel_pk': self.novel1.pk, 'pk': self.char1.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Access someone else's character
        response = self.client.get(reverse('character_detail', kwargs={'novel_pk': self.novel2.pk, 'pk': self.char2.pk}))
        self.assertEqual(response.status_code, 404)
