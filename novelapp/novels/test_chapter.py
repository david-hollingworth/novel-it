"""
Backend/state tests for Chapter CRUD, converted from content/requirements/
02-novel-management.md per data/requirements/phase-1-run-2-scope.yaml.

Covers the "Chapter" sub-batch: T-FUNC-0217.01.01 through T-DATA-0221.01.01
(13 tests). See novels/test_novel.py's module docstring for the Cancel-
scenario testing rationale.
"""
import pytest
from django.urls import reverse

from accounts.factories import UserFactory
from .factories import NovelFactory, PartFactory, ChapterFactory, SceneFactory
from .models import Novel, Part, Chapter, Scene


CHAPTER_FORM_FIELDS = {'title', 'description', 'notes', 'status'}


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


# T-FUNC-0217.01.01
@pytest.mark.django_db
def test_create_chapter_in_novel_without_parts(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    response = auth_client.post(
        reverse('chapter_create', kwargs={'novel_pk': novel.pk}),
        {'title': 'Chapter One', 'status': 'not_started'},
    )
    chapter = Chapter.objects.get(part__novel=novel, title='Chapter One')
    assert response.status_code == 302
    assert response.url == reverse('novel_detail', kwargs={'pk': novel.pk})
    assert chapter.part.title == '_default'

    detail_response = auth_client.get(reverse('novel_detail', kwargs={'pk': novel.pk}))
    assert chapter in detail_response.context['chapters']


# T-FUNC-0217.01.02
@pytest.mark.django_db
def test_create_chapter_in_novel_with_parts(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel)
    response = auth_client.post(
        reverse('chapter_create_in_part', kwargs={'novel_pk': novel.pk, 'part_pk': part.pk}),
        {'title': 'Chapter One', 'status': 'not_started'},
    )
    chapter = Chapter.objects.get(part=part, title='Chapter One')
    assert response.status_code == 302
    assert response.url == reverse('part_detail', kwargs={'novel_pk': novel.pk, 'part_pk': part.pk})

    part_response = auth_client.get(
        reverse('part_detail', kwargs={'novel_pk': novel.pk, 'part_pk': part.pk}))
    assert chapter in part_response.context['chapters']


# T-UI-0217.01.01
@pytest.mark.django_db
def test_add_chapter_form_presents_all_required_fields(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    response = auth_client.get(reverse('chapter_create', kwargs={'novel_pk': novel.pk}))
    assert set(response.context['form'].fields.keys()) == CHAPTER_FORM_FIELDS


# T-FUNC-0218.01.01
@pytest.mark.django_db
def test_edit_chapter_success(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part, title='Original Name')

    response = auth_client.post(
        reverse('chapter_edit', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}),
        {'title': 'Updated Name', 'status': chapter.status},
    )
    chapter.refresh_from_db()
    assert response.status_code == 302
    assert chapter.title == 'Updated Name'


# T-FUNC-0218.01.02
@pytest.mark.django_db
def test_cancel_editing_chapter_leaves_it_unchanged(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part, title='Original Name')

    response = auth_client.get(
        reverse('chapter_edit', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}))
    chapter.refresh_from_db()
    assert response.status_code == 200
    assert chapter.title == 'Original Name'


# T-UI-0218.01.01
@pytest.mark.django_db
def test_edit_chapter_form_presents_all_required_fields(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)

    response = auth_client.get(
        reverse('chapter_edit', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}))
    assert set(response.context['form'].fields.keys()) == CHAPTER_FORM_FIELDS


# T-FUNC-0219.01.01
@pytest.mark.django_db
def test_archive_chapter_success(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part, archived=False)

    response = auth_client.post(
        reverse('chapter_archive', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}))
    chapter.refresh_from_db()
    assert response.status_code == 302
    assert response.url == reverse('novel_detail', kwargs={'pk': novel.pk})
    assert chapter.archived is True

    detail_response = auth_client.get(reverse('novel_detail', kwargs={'pk': novel.pk}))
    assert chapter not in detail_response.context['chapters']


# T-FUNC-0219.01.02
@pytest.mark.django_db
def test_cancel_archiving_chapter_leaves_it_unarchived(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part, archived=False)

    response = auth_client.get(
        reverse('chapter_archive', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}))
    chapter.refresh_from_db()
    assert response.status_code == 200
    assert chapter.archived is False


# T-FUNC-0220.01.01
@pytest.mark.django_db
def test_restore_chapter_success(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part, archived=True)

    response = auth_client.post(
        reverse('chapter_restore', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}))
    chapter.refresh_from_db()
    assert response.status_code == 302
    assert response.url == reverse('novel_detail', kwargs={'pk': novel.pk})
    assert chapter.archived is False

    detail_response = auth_client.get(reverse('novel_detail', kwargs={'pk': novel.pk}))
    assert chapter in detail_response.context['chapters']
    archived_response = auth_client.get(
        reverse('archived_chapter_list', kwargs={'novel_pk': novel.pk}))
    assert chapter not in archived_response.context['chapters']


# T-FUNC-0220.01.02
@pytest.mark.django_db
def test_cancel_unarchiving_chapter_leaves_it_archived(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part, archived=True)

    response = auth_client.get(
        reverse('chapter_restore', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}))
    chapter.refresh_from_db()
    assert response.status_code == 200
    assert chapter.archived is True


# T-FUNC-0221.01.01
@pytest.mark.django_db
def test_delete_chapter_success(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    chapter_pk = chapter.pk

    response = auth_client.post(
        reverse('chapter_delete', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}))
    assert response.status_code == 302
    assert response.url == reverse('novel_detail', kwargs={'pk': novel.pk})
    assert not Chapter.objects.filter(pk=chapter_pk).exists()


# T-FUNC-0221.01.02
@pytest.mark.django_db
def test_cancel_deleting_chapter_leaves_it_intact(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)

    response = auth_client.get(
        reverse('chapter_delete', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}))
    assert response.status_code == 200
    assert Chapter.objects.filter(pk=chapter.pk).exists()


# T-DATA-0221.01.01
@pytest.mark.django_db
def test_delete_chapter_cascades_to_scenes(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene1 = SceneFactory(chapter=chapter)
    scene2 = SceneFactory(chapter=chapter)
    scene3 = SceneFactory(chapter=chapter)

    auth_client.post(
        reverse('chapter_delete', kwargs={'novel_pk': novel.pk, 'chapter_pk': chapter.pk}))

    assert not Scene.objects.filter(pk__in=[scene1.pk, scene2.pk, scene3.pk]).exists()
