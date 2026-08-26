"""
Backend/state tests for word-count save/cascade behaviour, converted from
content/requirements/03-writing-interface.md.

The chapter/part-level tests (T-FUNC-0304.02.01 through .03, and the .04-.06
variants of 0304.03/.04/.05) were converted per
data/requirements/phase-1-run-2-scope.yaml for Run 2. The scene-level
cascade tests (T-FUNC-0304.03.01-03, 0304.04.01-03, 0304.05.01-03) were
added for Run 3 -- these were originally excluded from Run 2 on the
assumption that scene archive/restore/delete weren't implemented, but that
assumption was wrong: the backend views existed all along, only the UI
buttons to reach them were missing from the old card design. See
data/requirements/phase-1-run-3-scope.yaml.

Cascade chain (see novels/models.py): Scene.save() always recalculates its
own word_count and calls chapter.update_word_count(), which recalculates
and calls part.update_word_count(), which recalculates and calls
novel.update_word_count(). Archiving/restoring a scene goes through
Scene.save() (so the cascade is automatic); deleting a scene doesn't, so
scene_delete_view explicitly calls chapter.update_word_count() afterward.
Archiving/restoring/deleting a chapter or part doesn't go through
Scene.save() either, so those views each explicitly re-trigger the relevant
update_word_count() call -- these tests check that all of this actually
happens, and happens correctly.
"""
import pytest
from django.urls import reverse

from accounts.factories import UserFactory
from .factories import NovelFactory, PartFactory, ChapterFactory, SceneFactory
from .models import Novel, Part, Chapter, Scene


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


# T-FUNC-0304.02.01
@pytest.mark.trace("T-FUNC-0304.02.01")
@pytest.mark.django_db
def test_chapter_word_count_updates_on_scene_save(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, content='')

    auth_client.post(
        reverse('scene_save', kwargs={
            'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk}),
        data='{"content": "one two three four five"}',
        content_type='application/json',
    )
    chapter.refresh_from_db()
    assert chapter.word_count == 5


# T-FUNC-0304.02.02
@pytest.mark.trace("T-FUNC-0304.02.02")
@pytest.mark.django_db
def test_novel_word_count_updates_on_scene_save(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, content='')

    auth_client.post(
        reverse('scene_save', kwargs={
            'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk}),
        data='{"content": "one two three four five"}',
        content_type='application/json',
    )
    novel.refresh_from_db()
    assert novel.word_count == 5


# T-FUNC-0304.02.03
@pytest.mark.trace("T-FUNC-0304.02.03")
@pytest.mark.django_db
def test_part_word_count_updates_on_scene_save_when_parts_enabled(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, content='')

    auth_client.post(
        reverse('scene_save', kwargs={
            'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk}),
        data='{"content": "one two three four five"}',
        content_type='application/json',
    )
    part.refresh_from_db()
    assert part.word_count == 5


# T-FUNC-0304.03.01
@pytest.mark.trace("T-FUNC-0304.03.01")
@pytest.mark.django_db
def test_archiving_scene_reduces_chapter_word_count(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, content='one two three four five')
    chapter.refresh_from_db()
    assert chapter.word_count == 5

    auth_client.post(
        reverse('scene_archive', kwargs={
            'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk}))
    chapter.refresh_from_db()
    assert chapter.word_count == 0


# T-FUNC-0304.03.02
@pytest.mark.trace("T-FUNC-0304.03.02")
@pytest.mark.django_db
def test_archiving_scene_reduces_novel_word_count(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, content='one two three four five')
    novel.refresh_from_db()
    assert novel.word_count == 5

    auth_client.post(
        reverse('scene_archive', kwargs={
            'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk}))
    novel.refresh_from_db()
    assert novel.word_count == 0


# T-FUNC-0304.03.03
@pytest.mark.trace("T-FUNC-0304.03.03")
@pytest.mark.django_db
def test_archiving_scene_reduces_part_word_count_when_parts_enabled(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, content='one two three four five')
    part.refresh_from_db()
    assert part.word_count == 5

    auth_client.post(
        reverse('scene_archive', kwargs={
            'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk}))
    part.refresh_from_db()
    assert part.word_count == 0


# T-FUNC-0304.03.04
@pytest.mark.trace("T-FUNC-0304.03.04")
@pytest.mark.django_db
def test_archiving_chapter_reduces_novel_word_count(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    SceneFactory(chapter=chapter, content='one two three four five')
    novel.refresh_from_db()
    assert novel.word_count == 5  # sanity check on setup

    auth_client.post(
        reverse('chapter_archive', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}))
    novel.refresh_from_db()
    assert novel.word_count == 0


# T-FUNC-0304.03.05
@pytest.mark.trace("T-FUNC-0304.03.05")
@pytest.mark.django_db
def test_archiving_chapter_reduces_part_word_count_when_parts_enabled(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel)
    chapter = ChapterFactory(part=part)
    SceneFactory(chapter=chapter, content='one two three four five')
    part.refresh_from_db()
    assert part.word_count == 5

    auth_client.post(
        reverse('chapter_archive', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}))
    part.refresh_from_db()
    assert part.word_count == 0


# T-FUNC-0304.03.06
@pytest.mark.trace("T-FUNC-0304.03.06")
@pytest.mark.django_db
def test_archiving_part_reduces_novel_word_count(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel)
    chapter = ChapterFactory(part=part)
    SceneFactory(chapter=chapter, content='one two three four five')
    novel.refresh_from_db()
    assert novel.word_count == 5

    auth_client.post(
        reverse('part_archive', kwargs={'novel_pk': novel.pk, 'part_pk': part.pk}),
        {'action': 'archive_with_chapters'},
    )
    novel.refresh_from_db()
    assert novel.word_count == 0


# T-FUNC-0304.04.01
@pytest.mark.trace("T-FUNC-0304.04.01")
@pytest.mark.django_db
def test_unarchiving_scene_increases_chapter_word_count(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, content='one two three four five', archived=True)
    chapter.refresh_from_db()
    # Scene is archived, so its word count doesn't count toward the chapter yet
    assert chapter.word_count == 0

    auth_client.post(
        reverse('scene_restore', kwargs={
            'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk}))
    chapter.refresh_from_db()
    assert chapter.word_count == 5


# T-FUNC-0304.04.02
@pytest.mark.trace("T-FUNC-0304.04.02")
@pytest.mark.django_db
def test_unarchiving_scene_increases_novel_word_count(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, content='one two three four five', archived=True)
    novel.refresh_from_db()
    assert novel.word_count == 0

    auth_client.post(
        reverse('scene_restore', kwargs={
            'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk}))
    novel.refresh_from_db()
    assert novel.word_count == 5


# T-FUNC-0304.04.03
@pytest.mark.trace("T-FUNC-0304.04.03")
@pytest.mark.django_db
def test_unarchiving_scene_increases_part_word_count_when_parts_enabled(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, content='one two three four five', archived=True)
    part.refresh_from_db()
    assert part.word_count == 0

    auth_client.post(
        reverse('scene_restore', kwargs={
            'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk}))
    part.refresh_from_db()
    assert part.word_count == 5


# T-FUNC-0304.04.04
@pytest.mark.trace("T-FUNC-0304.04.04")
@pytest.mark.django_db
def test_unarchiving_chapter_increases_novel_word_count(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part, archived=True)
    SceneFactory(chapter=chapter, content='one two three four five')
    novel.refresh_from_db()
    # Chapter is archived, so its word count doesn't count toward the novel yet
    assert novel.word_count == 0

    auth_client.post(
        reverse('chapter_restore', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}))
    novel.refresh_from_db()
    assert novel.word_count == 5


# T-FUNC-0304.04.05
@pytest.mark.trace("T-FUNC-0304.04.05")
@pytest.mark.django_db
def test_unarchiving_chapter_increases_part_word_count_when_parts_enabled(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel)
    chapter = ChapterFactory(part=part, archived=True)
    SceneFactory(chapter=chapter, content='one two three four five')
    part.refresh_from_db()
    assert part.word_count == 0

    auth_client.post(
        reverse('chapter_restore', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}))
    part.refresh_from_db()
    assert part.word_count == 5


# T-FUNC-0304.04.06
@pytest.mark.trace("T-FUNC-0304.04.06")
@pytest.mark.django_db
def test_unarchiving_part_increases_novel_word_count(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel, archived=True)
    chapter = ChapterFactory(part=part, archived=False)
    SceneFactory(chapter=chapter, content='one two three four five')
    novel.refresh_from_db()
    # Part is archived, so its word count doesn't count toward the novel yet
    assert novel.word_count == 0

    auth_client.post(
        reverse('part_unarchive', kwargs={'novel_pk': novel.pk, 'part_pk': part.pk}))
    novel.refresh_from_db()
    assert novel.word_count == 5


# T-FUNC-0304.05.01
@pytest.mark.trace("T-FUNC-0304.05.01")
@pytest.mark.django_db
def test_deleting_scene_reduces_chapter_word_count(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, content='one two three four five')
    chapter.refresh_from_db()
    assert chapter.word_count == 5

    auth_client.post(
        reverse('scene_delete', kwargs={
            'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk}))
    chapter.refresh_from_db()
    assert chapter.word_count == 0


# T-FUNC-0304.05.02
@pytest.mark.trace("T-FUNC-0304.05.02")
@pytest.mark.django_db
def test_deleting_scene_reduces_novel_word_count(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, content='one two three four five')
    novel.refresh_from_db()
    assert novel.word_count == 5

    auth_client.post(
        reverse('scene_delete', kwargs={
            'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk}))
    novel.refresh_from_db()
    assert novel.word_count == 0


# T-FUNC-0304.05.03
@pytest.mark.trace("T-FUNC-0304.05.03")
@pytest.mark.django_db
def test_deleting_scene_reduces_part_word_count_when_parts_enabled(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, content='one two three four five')
    part.refresh_from_db()
    assert part.word_count == 5

    auth_client.post(
        reverse('scene_delete', kwargs={
            'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk}))
    part.refresh_from_db()
    assert part.word_count == 0


# T-FUNC-0304.05.04
@pytest.mark.trace("T-FUNC-0304.05.04")
@pytest.mark.django_db
def test_deleting_chapter_reduces_novel_word_count(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    SceneFactory(chapter=chapter, content='one two three four five')
    novel.refresh_from_db()
    assert novel.word_count == 5

    auth_client.post(
        reverse('chapter_delete', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}))
    novel.refresh_from_db()
    assert novel.word_count == 0


# T-FUNC-0304.05.05
@pytest.mark.trace("T-FUNC-0304.05.05")
@pytest.mark.django_db
def test_deleting_chapter_reduces_part_word_count_when_parts_enabled(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel)
    chapter = ChapterFactory(part=part)
    SceneFactory(chapter=chapter, content='one two three four five')
    part.refresh_from_db()
    assert part.word_count == 5

    auth_client.post(
        reverse('chapter_delete', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}))
    part.refresh_from_db()
    assert part.word_count == 0


# T-FUNC-0304.05.06
@pytest.mark.trace("T-FUNC-0304.05.06")
@pytest.mark.django_db
def test_deleting_part_reduces_novel_word_count(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel)
    chapter = ChapterFactory(part=part)
    SceneFactory(chapter=chapter, content='one two three four five')
    novel.refresh_from_db()
    assert novel.word_count == 5

    auth_client.post(
        reverse('part_delete', kwargs={'novel_pk': novel.pk, 'part_pk': part.pk}))
    novel.refresh_from_db()
    assert novel.word_count == 0
