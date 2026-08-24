"""
Backend/state tests for word-count save/cascade behaviour, converted from
content/requirements/03-writing-interface.md per
data/requirements/phase-1-run-2-scope.yaml.

Covers 12 of writing-interface's 16 backend_state tests: T-FUNC-0304.02.01
through T-FUNC-0304.05.06 (the .01-.03 scene-level cascade tests in each of
0304.03/.04/.05 are excluded -- scene archive/restore/delete isn't
implemented yet).

Cascade chain (see novels/models.py): Scene.save() always recalculates its
own word_count and calls chapter.update_word_count(), which recalculates
and calls part.update_word_count(), which recalculates and calls
novel.update_word_count(). Archiving/restoring/deleting a chapter or part
doesn't go through Scene.save(), so each view explicitly re-triggers the
relevant update_word_count() call -- these tests check that it actually
does, and does so correctly.

NOTE on T-FUNC-0304.05.06 ("Deleting a part reduces the novel word count"):
part_delete_view calls part.delete() but does not call
novel.update_word_count() afterward, and there's no signal filling that gap
(checked novels/apps.py and novels/signals.py -- no signals module exists).
This is a regression from an incomplete fix in #79 (which correctly fixed
chapter deletion but missed the equivalent call for part deletion). Tracked
as issue #138; the test below is marked xfail(strict=True) referencing it
so it doesn't break CI, but will flip to a loud failure if someone fixes
the bug without updating this marker -- a silent pass would be worse than
the current visible xfail.
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
@pytest.mark.xfail(reason="part_delete_view doesn't update novel word count -- issue #138", strict=True)
def test_deleting_part_reduces_novel_word_count(auth_client, user):
    """
    See module docstring -- part_delete_view doesn't call
    novel.update_word_count() after part.delete(). Tracked as issue #138.
    """
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
