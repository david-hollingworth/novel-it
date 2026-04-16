from django.contrib import admin

from .models import Novel, Part, Chapter, Scene


@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_name', 'status', 'parts_enabled', 'word_count', 'updated_at')
    list_filter = ('status', 'parts_enabled', 'archived')
    search_fields = ('title', 'author_name')


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('title', 'novel', 'order', 'status', 'word_count', 'archived')
    list_filter = ('status', 'archived', 'novel')
    search_fields = ('title', 'novel__title')


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'part', 'order', 'status', 'word_count', 'archived')
    list_filter = ('status', 'archived', 'part__novel')
    search_fields = ('title', 'part__title', 'part__novel__title')


@admin.register(Scene)
class SceneAdmin(admin.ModelAdmin):
    list_display = ('title', 'chapter', 'order', 'status', 'word_count', 'archived')
    list_filter = ('status', 'archived', 'chapter__part__novel')
    search_fields = ('title', 'chapter__title')

