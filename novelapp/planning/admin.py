from django.contrib import admin

from .models import (
    Character, CharacterRole,
    Location, LocationType,
    Item, ItemType,
    RelationshipType, Relationship,
    SceneEntity,
)


@admin.register(CharacterRole)
class CharacterRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'novel', 'order')
    list_filter = ('novel',)
    search_fields = ('name', 'novel__title')


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'novel', 'role', 'gender', 'age', 'archived')
    list_filter = ('novel', 'role', 'archived')
    search_fields = ('fullname', 'nickname', 'first_name', 'last_name', 'novel__title')


@admin.register(LocationType)
class LocationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'novel', 'order')
    list_filter = ('novel',)
    search_fields = ('name', 'novel__title')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'novel', 'type', 'archived')
    list_filter = ('novel', 'type', 'archived')
    search_fields = ('name', 'novel__title')


@admin.register(ItemType)
class ItemTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'novel', 'order')
    list_filter = ('novel',)
    search_fields = ('name', 'novel__title')


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'novel', 'type', 'archived')
    list_filter = ('novel', 'type', 'archived')
    search_fields = ('name', 'novel__title')


@admin.register(RelationshipType)
class RelationshipTypeAdmin(admin.ModelAdmin):
    list_display = ('forward_label', 'reverse_label', 'novel', 'order')
    list_filter = ('novel',)
    search_fields = ('forward_label', 'reverse_label')


@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    list_display = ('label', 'novel', 'from_content_type', 'to_content_type')
    list_filter = ('novel', 'label')
    search_fields = ('label', 'reverse_label')


@admin.register(SceneEntity)
class SceneEntityAdmin(admin.ModelAdmin):
    list_display = ('scene', 'content_type', 'object_id', 'mention_count')
    list_filter = ('content_type',)
    search_fields = ('scene__title',)
