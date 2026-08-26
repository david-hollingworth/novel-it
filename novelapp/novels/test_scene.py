"""
Backend/state tests for Scene create/edit/relocate/archive/restore/delete,
converted from content/requirements/02-novel-management.md.

The first 6 tests (create/edit/relocate) were converted per
data/requirements/phase-1-run-2-scope.yaml for Run 2. The archive/restore/
delete tests (T-FUNC-0225/0226/0227) were added for Run 3 -- these were
originally excluded from Run 2 on the assumption that scene archive/restore/
delete weren't implemented, but that assumption was wrong: the backend
views existed all along, only the UI buttons to reach them were missing
from the old card design. See data/requirements/phase-1-run-3-scope.yaml.

Each test carries a @pytest.mark.trace(...) tag mapping it back to its
requirements-doc test ID -- see conftest.py for how this surfaces in -v
output.
"""
import json

import pytest
from django.urls import reverse

from accounts.factories import UserFactory
from .factories import NovelFactory, ChapterFactory, SceneFactory
from .models import Novel, Part, Chapter, Scene


SCENE_FORM_FIELDS = {'title', 'description', 'notes', 'status'}


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


# T-FUNC-0223.01.01
@pytest.mark.trace("T-FUNC-0223.01.01")
@pytest.mark.django_db
def test_create_scene_success(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)

    response = auth_client.post(
        reverse('scene_create', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}),
        {'title': 'Scene One', 'status': 'not_started'},
    )
    scene = Scene.objects.get(chapter=chapter, title='Scene One')
    assert response.status_code == 302
    assert response.url == reverse(
        'chapter_detail', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk})

    detail_response = auth_client.get(
        reverse('chapter_detail', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}))
    assert scene in detail_response.context['scenes']


# T-UI-0223.01.01
@pytest.mark.trace("T-UI-0223.01.01")
@pytest.mark.django_db
def test_add_scene_form_presents_all_required_fields(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)

    response = auth_client.get(
        reverse('scene_create', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}))
    assert set(response.context['form'].fields.keys()) == SCENE_FORM_FIELDS


# T-FUNC-0224.01.01
@pytest.mark.trace("T-FUNC-0224.01.01")
@pytest.mark.django_db
def test_edit_scene_success(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, title='Original Name')

    response = auth_client.post(
        reverse('scene_edit', kwargs={
            'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk}),
        {'title': 'Updated Name', 'status': scene.status},
    )
    scene.refresh_from_db()
    assert response.status_code == 302
    assert scene.title == 'Updated Name'


# T-FUNC-0224.01.02
@pytest.mark.trace("T-FUNC-0224.01.02")
@pytest.mark.django_db
def test_cancel_editing_scene_leaves_it_unchanged(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, title='Original Name')

    response = auth_client.get(
        reverse('scene_edit', kwargs={
            'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk}))
    scene.refresh_from_db()
    assert response.status_code == 200
    assert scene.title == 'Original Name'


# T-UI-0224.01.01
@pytest.mark.trace("T-UI-0224.01.01")
@pytest.mark.django_db
def test_edit_scene_form_presents_all_required_fields(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter)

    response = auth_client.get(
        reverse('scene_edit', kwargs={
            'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk}))
    assert set(response.context['form'].fields.keys()) == SCENE_FORM_FIELDS


# T-FUNC-0228.01.01
@pytest.mark.trace("T-FUNC-0228.01.01")
@pytest.mark.django_db
def test_relocate_scene_to_another_chapter(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    source_chapter = ChapterFactory(part=part)
    target_chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=source_chapter)

    response = auth_client.post(
        reverse('scene_move', kwargs={'novel_pk': novel.pk, 'scene_pk': scene.pk}),
        data=json.dumps({'target_chapter_id': target_chapter.pk}),
        content_type='application/json',
    )
    scene.refresh_from_db()

    assert response.status_code == 200
    assert response.json()['status'] == 'success'
    assert scene.chapter == target_chapter
    assert scene not in source_chapter.scenes.all()


# T-FUNC-0225.01.01
@pytest.mark.trace("T-FUNC-0225.01.01")
@pytest.mark.django_db
def test_archive_scene_success(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, archived=False)

    response = auth_client.post(
        reverse('scene_archive', kwargs={
            'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk}))
    scene.refresh_from_db()
    assert response.status_code == 302
    assert response.url == reverse(
        'chapter_detail', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk})
    assert scene.archived is True

    detail_response = auth_client.get(
        reverse('chapter_detail', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}))
    assert scene not in detail_response.context['scenes']


# T-FUNC-0225.01.02
@pytest.mark.trace("T-FUNC-0225.01.02")
@pytest.mark.django_db
def test_cancel_archiving_scene_leaves_it_unarchived(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, archived=False)

    response = auth_client.get(
        reverse('scene_archive', kwargs={
            'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk}))
    scene.refresh_from_db()
    assert response.status_code == 200
    assert scene.archived is False


# T-FUNC-0226.01.01
@pytest.mark.trace("T-FUNC-0226.01.01")
@pytest.mark.django_db
def test_restore_scene_success(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, archived=True)

    response = auth_client.post(
        reverse('scene_restore', kwargs={
            'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk}))
    scene.refresh_from_db()
    assert response.status_code == 302
    assert response.url == reverse(
        'chapter_detail', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk})
    assert scene.archived is False

    detail_response = auth_client.get(
        reverse('chapter_detail', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}))
    assert scene in detail_response.context['scenes']
    archived_response = auth_client.get(
        reverse('archived_scene_list', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}))
    assert scene not in archived_response.context['scenes']


# T-FUNC-0226.01.02
@pytest.mark.trace("T-FUNC-0226.01.02")
@pytest.mark.django_db
def test_cancel_unarchiving_scene_leaves_it_archived(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, archived=True)

    response = auth_client.get(
        reverse('scene_restore', kwargs={
            'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk}))
    scene.refresh_from_db()
    assert response.status_code == 200
    assert scene.archived is True


# T-FUNC-0227.01.01
@pytest.mark.trace("T-FUNC-0227.01.01")
@pytest.mark.django_db
def test_delete_scene_success(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter)
    scene_pk = scene.pk

    response = auth_client.post(
        reverse('scene_delete', kwargs={
            'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk}))
    assert response.status_code == 302
    assert response.url == reverse(
        'chapter_detail', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk})
    assert not Scene.objects.filter(pk=scene_pk).exists()


# T-FUNC-0227.01.02
@pytest.mark.trace("T-FUNC-0227.01.02")
@pytest.mark.django_db
def test_cancel_deleting_scene_leaves_it_intact(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter)

    response = auth_client.get(
        reverse('scene_delete', kwargs={
            'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk}))
    assert response.status_code == 200
    assert Scene.objects.filter(pk=scene.pk).exists()
