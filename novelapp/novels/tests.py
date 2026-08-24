from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Novel, Part, Chapter, Scene

# Cross-user data isolation is enforced here but not yet documented as a
# formal requirement -- see issue #136.
class NovelScopingTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')
        self.novel1 = Novel.objects.create(user=self.user1, title='User 1 Novel')
        self.novel2 = Novel.objects.create(user=self.user2, title='User 2 Novel')

    def test_novel_list_scoping(self):
        self.client.login(username='user1', password='pass1')
        response = self.client.get(reverse('novel_list'))
        self.assertContains(response, 'User 1 Novel')
        self.assertNotContains(response, 'User 2 Novel')

    def test_novel_detail_access_scoping(self):
        self.client.login(username='user1', password='pass1')
        # Access own novel
        response = self.client.get(reverse('novel_detail', kwargs={'pk': self.novel1.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Access someone else's novel
        response = self.client.get(reverse('novel_detail', kwargs={'pk': self.novel2.pk}))
        self.assertEqual(response.status_code, 404)

# Word-count calculation mechanics (markdown exclusion) are tested here but
# not yet documented as a formal requirement -- see issue #137.
class WordCountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.novel = Novel.objects.create(user=self.user, title='Test Novel')
        # Chapter has no direct FK to Novel -- it hangs off Part. Chapter.novel
        # is a derived read-only property (part.novel), so a Part has to exist
        # first even though parts_enabled is off for this novel.
        self.part = Part.objects.create(novel=self.novel, title='Part 1', order=1)
        self.chapter = Chapter.objects.create(part=self.part, title='Chapter 1', order=1)
        self.scene = Scene.objects.create(chapter=self.chapter, title='Scene 1', order=1)

    def test_word_count_calculation(self):
        self.scene.content = "One two three four five."
        self.scene.save() # Triggers calculation
        self.assertEqual(self.scene.word_count, 5)
        
        # Refresh from DB
        self.chapter.refresh_from_db()
        self.novel.refresh_from_db()
        
        self.assertEqual(self.chapter.word_count, 5)
        self.assertEqual(self.novel.word_count, 5)

    def test_markdown_exclusion(self):
        self.scene.content = "# Header\n\n**Bold** text and [link](http://example.com)."
        # words: Header, Bold, text, and, link. (5 words)
        self.scene.save()
        self.assertEqual(self.scene.word_count, 5)
