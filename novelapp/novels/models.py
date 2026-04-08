from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import re


# Manuscript entity status choices — applies to Novels, Parts, Chapters, and Scenes (FEAT-0229)
MANUSCRIPT_STATUS_CHOICES = [
    ('not_started', 'Not Started'),
    ('plotting', 'Plotting'),
    ('first_draft', 'First Draft'),
    ('first_review', 'First Review'),
    ('second_draft', 'Second Draft'),
    ('second_review', 'Second Review'),
    ('structural_edit', 'Structural Edit'),
    ('final_edit', 'Final Edit'),
    ('beta_reading', 'Beta Reading'),
    ('publishing', 'Publishing'),
    ('published', 'Published'),
]

MANUSCRIPT_STATUS_DEFAULT = 'not_started'


class Novel(models.Model):
    """
    A novel belongs to a user and contains chapters.
    Implements FEAT-0201 (Add novel) and FEAT-0203 (Edit novel).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='novels')

    # Base entity: Name (FEAT-0004) — labelled Title for novels
    title = models.CharField(max_length=255)

    # Novel-specific: Subtitle (FEAT-0201)
    subtitle = models.CharField(max_length=255, blank=True, help_text="Subtitle of the novel")

    # Novel-specific: Author name (FEAT-0201)
    author_name = models.CharField(max_length=255, blank=True, help_text="Author name")

    # Novel-specific: Genre (FEAT-0201)
    genre = models.CharField(max_length=100, blank=True, help_text="Genre of the novel")

    # Novel-specific: Target word count — see FEAT-1204 Novel word count goal
    target_word_count = models.IntegerField(default=0, help_text="Target word count goal")

    # Novel-specific: Status (FEAT-0201, FEAT-0229)
    status = models.CharField(
        max_length=20,
        choices=MANUSCRIPT_STATUS_CHOICES,
        default=MANUSCRIPT_STATUS_DEFAULT,
        help_text="Current status of the novel",
    )

    # Base entity: Description (FEAT-0004) — labelled Synopsis for novels
    description = models.TextField(blank=True, help_text="Synopsis of the novel")

    # Base entity: Notes (FEAT-0004) — labelled Premise for novels
    premise = models.TextField(blank=True, help_text="Premise or theme of the novel")

    # Novel-specific: Pitch (FEAT-0201)
    pitch = models.TextField(blank=True, help_text="One-paragraph pitch for the novel")

    # Novel-specific: calculated from scenes; read-only (FEAT-0203)
    word_count = models.IntegerField(default=0, help_text="Total word count (calculated from scenes)")

    # Base entity: Date and time created — system-set, not user-editable (FEAT-0004)
    created_at = models.DateTimeField(auto_now_add=True)

    # Base entity: Date and time last modified — system-set, not user-editable (FEAT-0004)
    updated_at = models.DateTimeField(auto_now=True)

    # Base entity: Archived flag — supports FEAT-0004 / FEAT-0005
    archived = models.BooleanField(default=False, help_text="Soft delete flag")

    # Novel-specific: controls whether the Parts level is visible in the UI (FEAT-0201, FEAT-0203)
    parts_enabled = models.BooleanField(default=False, help_text="Whether parts are enabled for this novel")

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Novel'
        verbose_name_plural = 'Novels'

    def __str__(self):
        return self.title

    def update_word_count(self):
        """
        Calculate and update word count from all parts in this novel.
        Parts sum from their chapters; this method sums across all parts.
        """
        total = sum(part.word_count for part in self.parts.filter(archived=False))
        self.word_count = total
        self.save(update_fields=['word_count'])

    def get_chapter_count(self):
        """Return the number of non-archived chapters across all parts in this novel."""
        return sum(part.chapters.filter(archived=False).count()
                   for part in self.parts.filter(archived=False))

    def get_scene_count(self):
        """Return the total number of scenes across all chapters in this novel."""
        return sum(
            chapter.scenes.filter(archived=False).count()
            for part in self.parts.filter(archived=False)
            for chapter in part.chapters.filter(archived=False)
        )


class Part(models.Model):
    """
    A part is an optional structural level between a novel and its chapters.
    Implements FEAT-0211 (Add part) and FEAT-0212 (Edit part), extending the
    base entity specification (FEAT-0004 / FEAT-0002).
    When parts_enabled is False on the novel, each novel has a single
    transparent Part that is not exposed in the UI.
    """

    # Parent relationship — not a base entity field
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='parts')

    # Base entity: Name (FEAT-0004)
    title = models.CharField(max_length=255)

    # Not a base entity field — controls display order within the novel
    order = models.IntegerField(default=0)

    # Base entity: Description (FEAT-0004)
    summary = models.TextField(blank=True)

    # Base entity: Notes (FEAT-0004)
    notes = models.TextField(blank=True)

    # Part-specific extension: Status (FEAT-0211, FEAT-0229)
    status = models.CharField(
        max_length=20,
        choices=MANUSCRIPT_STATUS_CHOICES,
        default=MANUSCRIPT_STATUS_DEFAULT,
    )

    # Part-specific: calculated from child chapters; read-only in edit mode (FEAT-0212)
    word_count = models.IntegerField(default=0)

    # Base entity: Date and time created — system-set, not user-editable (FEAT-0004)
    created_at = models.DateTimeField(auto_now_add=True)

    # Base entity: Date and time last modified — system-set, not user-editable (FEAT-0004)
    updated_at = models.DateTimeField(auto_now=True)

    # Base entity: Archived flag — supports FEAT-0005 / FEAT-0003
    archived = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']
        verbose_name = 'Part'
        verbose_name_plural = 'Parts'
        unique_together = ['novel', 'order']

    def __str__(self):
        return f"{self.novel.title} - {self.title}"

    def update_word_count(self):
        """
        Calculate and update word count from all chapters in this part.
        Also triggers novel word count update.
        """
        total = sum(c.word_count for c in self.chapters.filter(archived=False))
        self.word_count = total
        self.save(update_fields=['word_count'])
        self.novel.update_word_count()

    def get_chapter_count(self):
        """Return the number of non-archived chapters in this part."""
        return self.chapters.filter(archived=False).count()

    def get_scene_count(self):
        """Return the total number of scenes across all chapters in this part."""
        return sum(chapter.scenes.filter(archived=False).count()
                   for chapter in self.chapters.filter(archived=False))


class Chapter(models.Model):
    """
    A chapter belongs to a part and contains scenes.
    When parts are not enabled on the novel, a transparent Part is used as parent.
    """
    # Parent relationship — not a base entity field
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='chapters')

    # Base entity: Name (FEAT-0004)
    title = models.CharField(max_length=255)

    # Not a base entity field — controls display order within the part
    order = models.IntegerField(default=0, help_text="Display order within the part")

    # Base entity: Description (FEAT-0004)
    summary = models.TextField(blank=True, help_text="Chapter summary")

    # Base entity: Notes (FEAT-0004)
    notes = models.TextField(blank=True)

    # Chapter-specific extension: Status (FEAT-0217, FEAT-0229)
    status = models.CharField(
        max_length=20,
        choices=MANUSCRIPT_STATUS_CHOICES,
        default=MANUSCRIPT_STATUS_DEFAULT,
    )

    # Chapter-specific: calculated from child scenes; read-only in edit mode (FEAT-0218)
    word_count = models.IntegerField(default=0, help_text="Total word count (calculated from scenes)")

    # Base entity: Date and time created — system-set, not user-editable (FEAT-0004)
    created_at = models.DateTimeField(auto_now_add=True)

    # Base entity: Date and time last modified — system-set, not user-editable (FEAT-0004)
    updated_at = models.DateTimeField(auto_now=True)

    # Base entity: Archived flag — supports FEAT-0005 / FEAT-0003
    archived = models.BooleanField(default=False, help_text="Soft delete flag")

    class Meta:
        ordering = ['order']
        verbose_name = 'Chapter'
        verbose_name_plural = 'Chapters'
        unique_together = ['part', 'order']

    def __str__(self):
        return f"{self.part.novel.title} - {self.part.title} - {self.title}"

    @property
    def novel(self):
        """Convenience accessor — traverses via part to the parent novel."""
        return self.part.novel

    def update_word_count(self):
        """
        Calculate and update word count from all scenes in this chapter.
        Also triggers part word count update (which in turn updates the novel).
        """
        total = sum(scene.word_count for scene in self.scenes.filter(archived=False))
        self.word_count = total
        self.save(update_fields=['word_count'])
        # Update parent part's word count (which will update novel)
        self.part.update_word_count()

    def get_scene_count(self):
        """Return the number of scenes in this chapter."""
        return self.scenes.filter(archived=False).count()


class Scene(models.Model):
    """
    A scene belongs to a chapter and contains the actual writing content.
    """
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='scenes')

    # Base entity: Name (FEAT-0004)
    title = models.CharField(max_length=255)

    # Not a base entity field — controls display order within the chapter
    order = models.IntegerField(default=0, help_text="Display order within the chapter")

    # Scene-specific extension: Status (FEAT-0223, FEAT-0229)
    status = models.CharField(
        max_length=20,
        choices=MANUSCRIPT_STATUS_CHOICES,
        default=MANUSCRIPT_STATUS_DEFAULT,
    )

    # Scene-specific: the actual writing content
    content = models.TextField(blank=True, help_text="Markdown content of the scene")

    # Base entity: Notes (FEAT-0004)
    notes = models.TextField(blank=True, help_text="Scene notes or summary")

    # Scene-specific: calculated from content; read-only in edit mode (FEAT-0224)
    word_count = models.IntegerField(default=0, help_text="Word count of content")

    # Base entity: Date and time created — system-set, not user-editable (FEAT-0004)
    created_at = models.DateTimeField(auto_now_add=True)

    # Base entity: Date and time last modified — system-set, not user-editable (FEAT-0004)
    updated_at = models.DateTimeField(auto_now=True)

    # Base entity: Archived flag — supports FEAT-0005 / FEAT-0003
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
