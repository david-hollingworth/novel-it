from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from novels.models import Novel


def character_image_path(instance, filename):
    """Generate upload path for character images."""
    return f'characters/{instance.novel.id}/{filename}'


def location_image_path(instance, filename):
    """Generate upload path for location images."""
    return f'locations/{instance.novel.id}/{filename}'


def item_image_path(instance, filename):
    """Generate upload path for item images."""
    return f'items/{instance.novel.id}/{filename}'


# Choice Models - these allow users to define their own categories

class CharacterRole(models.Model):
    """
    User-definable character roles.
    Each novel can have its own set of character roles.
    """
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='character_roles')
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Character Role'
        verbose_name_plural = 'Character Roles'
        unique_together = ['novel', 'name']

    def __str__(self):
        return self.name


class LocationType(models.Model):
    """
    User-definable location types.
    Each novel can have its own set of location types.
    """
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='location_types')
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Location Type'
        verbose_name_plural = 'Location Types'
        unique_together = ['novel', 'name']

    def __str__(self):
        return self.name


class ItemType(models.Model):
    """
    User-definable item types.
    Each novel can have its own set of item types.
    """
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='item_types')
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Item Type'
        verbose_name_plural = 'Item Types'
        unique_together = ['novel', 'name']

    def __str__(self):
        return self.name


# Main Planning Models

class Character(models.Model):
    """
    A character in a novel.
    Characters are scoped to a specific novel.
    """
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='characters')

    # Base entity: Name — labelled Full Name for characters (FEAT-0403)
    fullname = models.CharField(max_length=255)

    # Name breakdown fields (FEAT-0403)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    nickname = models.CharField(max_length=255, blank=True, null=True)
    aliases = models.CharField(max_length=255, blank=True, null=True)

    # Biographical fields (FEAT-0403)
    gender = models.CharField(max_length=255, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)

    # Role in story — FK to user-definable CharacterRole (FEAT-0403)
    role = models.ForeignKey(
        CharacterRole,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='characters',
        help_text="Character's role in the story"
    )

    # Character-specific narrative fields (FEAT-0403)
    physical_description = models.TextField(blank=True, help_text="Physical description of the character (markdown supported)")
    interview = models.TextField(blank=True, help_text="Interview with the character (markdown supported)")
    the_lie_they_believe = models.TextField(blank=True, help_text="The lie the character believes about themselves or the world (markdown supported)")
    goals_and_motivations = models.TextField(blank=True, help_text="Goals and motivations of the character (markdown supported)")
    fears_and_weaknesses = models.TextField(blank=True, help_text="Fears and weaknesses of the character (markdown supported)")
    arc_in_story = models.TextField(blank=True, help_text="The character's arc in the story (markdown supported)")

    # Character image (FEAT-0403)
    image = models.ImageField(upload_to=character_image_path, blank=True, null=True, help_text="Character portrait or reference image")

    # Base entity: Description (FEAT-0004)
    description = models.TextField(blank=True, help_text="General description of the character (markdown supported)")

    # Base entity: Notes (FEAT-0004)
    notes = models.TextField(blank=True, help_text="Additional notes about the character (markdown supported)")

    # NO LONGER IN USE — retained to avoid data loss pending review
    personality = models.TextField(blank=True, help_text="[No longer in use] Personality traits")
    relationships = models.TextField(blank=True, help_text="[No longer in use] Free-text relationships field, superseded by the Relationship model")
    order = models.IntegerField(default=0, help_text="Display order within the novel")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    archived = models.BooleanField(default=False, help_text="Soft delete flag")

    class Meta:
        ordering = ['order', 'last_name', 'first_name']
        verbose_name = 'Character'
        verbose_name_plural = 'Characters'

    def __str__(self):
        if self.role:
            return f"{self.fullname} ({self.role.name})"
        return self.fullname

    def get_novel_title(self):
        """Return the title of the novel this character belongs to."""
        return self.novel.title


class Location(models.Model):
    """
    A location/setting in a novel.
    Locations are scoped to a specific novel.
    """
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=255)
    type = models.ForeignKey(
        LocationType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='locations',
        help_text="Type of location"
    )
    description = models.TextField(blank=True, help_text="Description of the location (markdown supported)")
    notes = models.TextField(blank=True, help_text="Additional notes about the location (markdown supported)")
    image = models.ImageField(upload_to=location_image_path, blank=True, null=True, help_text="Location image or map")
    order = models.IntegerField(default=0, help_text="Display order within the novel")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    archived = models.BooleanField(default=False, help_text="Soft delete flag")

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'

    def __str__(self):
        if self.type:
            return f"{self.name} ({self.type.name})"
        return self.name

    def get_novel_title(self):
        """Return the title of the novel this location belongs to."""
        return self.novel.title


class Item(models.Model):
    """
    An item/object/artifact in a novel.
    Items are scoped to a specific novel.
    """
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='items')

    # Base entity: Name (FEAT-0602)
    name = models.CharField(max_length=255)

    # Item type — FK to user-definable ItemType (FEAT-0602)
    type = models.ForeignKey(
        ItemType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items',
        help_text="Type of item"
    )

    # Item-specific narrative fields (FEAT-0602)
    history = models.TextField(blank=True, help_text="History of the item (markdown supported)")
    properties_and_abilities = models.TextField(blank=True, help_text="Properties and abilities of the item (markdown supported)")

    # Base entity: Description (FEAT-0004)
    description = models.TextField(blank=True, help_text="Description of the item (markdown supported)")

    # Base entity: Notes (FEAT-0004)
    notes = models.TextField(blank=True, help_text="Additional notes about the item (markdown supported)")

    # Item image (FEAT-0602)
    image = models.ImageField(upload_to=item_image_path, blank=True, null=True, help_text="Item image or reference")
    order = models.IntegerField(default=0, help_text="Display order within the novel")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    archived = models.BooleanField(default=False, help_text="Soft delete flag")

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Item'
        verbose_name_plural = 'Items'

    def __str__(self):
        if self.type:
            return f"{self.name} ({self.type.name})"
        return self.name

    def get_novel_title(self):
        """Return the title of the novel this item belongs to."""
        return self.novel.title


class RelationshipType(models.Model):
    """
    User-definable relationship types with forward and reverse labels.
    e.g. forward: 'owns', reverse: 'owned by'
    """
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='relationship_types')
    forward_label = models.CharField(max_length=100, help_text="e.g. 'owns', 'lives in', 'enemy of'")
    reverse_label = models.CharField(max_length=100, help_text="e.g. 'owned by', 'home of', 'enemy of'")
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'forward_label']
        unique_together = ['novel', 'forward_label']

    def __str__(self):
        return f"{self.forward_label} / {self.reverse_label}"


class Relationship(models.Model):
    """
    A generic relationship between any two planning entities
    (Character, Location, or Item) within a novel.
    """
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='relationships')

    # From entity (generic FK)
    from_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name='relationships_from'
    )
    from_object_id = models.PositiveIntegerField()
    from_entity = GenericForeignKey('from_content_type', 'from_object_id')

    # To entity (generic FK)
    to_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name='relationships_to'
    )
    to_object_id = models.PositiveIntegerField()
    to_entity = GenericForeignKey('to_content_type', 'to_object_id')

    # Labels
    label = models.CharField(max_length=100, help_text="Forward label e.g. 'owns'")
    reverse_label = models.CharField(max_length=100, help_text="Reverse label e.g. 'owned by'")

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['label']

    def __str__(self):
        return f"{self.from_entity} {self.label} {self.to_entity}"


class SceneEntity(models.Model):
    """
    Records that a planning entity (Character, Location, or Item) was
    detected in a scene's content. Populated automatically on scene save
    by scanning the text for known names and aliases.
    """
    scene = models.ForeignKey(
        'novels.Scene', on_delete=models.CASCADE, related_name='scene_entities'
    )
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name='scene_occurrences'
    )
    object_id = models.PositiveIntegerField()
    entity = GenericForeignKey('content_type', 'object_id')
    mention_count = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['scene', 'content_type', 'object_id']
        ordering = ['content_type', 'object_id']

    def __str__(self):
        return f"{self.entity} in {self.scene} ({self.mention_count}x)"