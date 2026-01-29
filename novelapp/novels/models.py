from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import re


class Novel(models.Model):
    """
    A novel belongs to a user and contains chapters.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='novels')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, help_text="Synopsis or description of the novel")
    premise = models.TextField(blank=True, help_text="Premise or theme of the novel")
    genre = models.CharField(max_length=100, blank=True, help_text="Genre of the novel")
    word_count = models.IntegerField(default=0, help_text="Total word count (calculated from scenes)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    archived = models.BooleanField(default=False, help_text="Soft delete flag")

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Novel'
        verbose_name_plural = 'Novels'

    def __str__(self):
        return self.title

    def update_word_count(self):
        """
        Calculate and update word count from all scenes in this novel.
        """
        total = 0
        for chapter in self.chapters.all():
            total += chapter.word_count
        self.word_count = total
        self.save(update_fields=['word_count'])

    def get_chapter_count(self):
        """Return the number of chapters in this novel."""
        return self.chapters.filter(archived=False).count()

    def get_scene_count(self):
        """Return the total number of scenes across all chapters."""
        return sum(chapter.scenes.filter(archived=False).count() 
                   for chapter in self.chapters.filter(archived=False))


class Chapter(models.Model):
    """
    A chapter belongs to a novel and contains scenes.
    """
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=255)
    order = models.IntegerField(default=0, help_text="Display order within the novel")
    summary = models.TextField(blank=True, help_text="Chapter summary or notes")
    word_count = models.IntegerField(default=0, help_text="Total word count (calculated from scenes)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    archived = models.BooleanField(default=False, help_text="Soft delete flag")

    class Meta:
        ordering = ['order']
        verbose_name = 'Chapter'
        verbose_name_plural = 'Chapters'
        unique_together = ['novel', 'order']

    def __str__(self):
        return f"{self.novel.title} - {self.title}"

    def update_word_count(self):
        """
        Calculate and update word count from all scenes in this chapter.
        Also triggers novel word count update.
        """
        total = sum(scene.word_count for scene in self.scenes.filter(archived=False))
        self.word_count = total
        self.save(update_fields=['word_count'])
        # Update parent novel's word count
        self.novel.update_word_count()

    def get_scene_count(self):
        """Return the number of scenes in this chapter."""
        return self.scenes.filter(archived=False).count()


class Scene(models.Model):
    """
    A scene belongs to a chapter and contains the actual writing content.
    """
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='scenes')
    title = models.CharField(max_length=255)
    order = models.IntegerField(default=0, help_text="Display order within the chapter")
    content = models.TextField(blank=True, help_text="Markdown content of the scene")
    notes = models.TextField(blank=True, help_text="Scene notes or summary")
    word_count = models.IntegerField(default=0, help_text="Word count of content")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    archived = models.BooleanField(default=False, help_text="Soft delete flag")

    class Meta:
        ordering = ['order']
        verbose_name = 'Scene'
        verbose_name_plural = 'Scenes'
        unique_together = ['chapter', 'order']

    def __str__(self):
        return f"{self.chapter.novel.title} - {self.chapter.title} - {self.title}"

    def calculate_word_count(self):
        """
        Calculate word count from markdown content.
        Excludes markdown syntax from count.
        """
        if not self.content:
            return 0
        
        # Remove markdown syntax for more accurate word count
        text = self.content
        # Remove code blocks
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        # Remove inline code
        text = re.sub(r'`[^`]*`', '', text)
        # Remove links but keep link text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # Remove images
        text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', text)
        # Remove headers
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        # Remove bold/italic markers
        text = re.sub(r'[*_]{1,3}', '', text)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Count words
        words = text.split()
        return len(words)

    def save(self, *args, **kwargs):
        """
        Override save to automatically update word counts.
        """
        # Calculate this scene's word count
        self.word_count = self.calculate_word_count()
        
        # Save the scene
        super().save(*args, **kwargs)
        
        # Update parent chapter's word count (which will update novel's)
        self.chapter.update_word_count()