"""
Backend/state tests for Novel CRUD, converted from content/requirements/
02-novel-management.md per data/requirements/phase-1-run-2-scope.yaml.

Covers the "Novel" sub-batch: T-FUNC-0201.01.01 through T-FUNC-0210.01.02
(22 tests). Part/Chapter/Scene/Status sub-batches are separate files.

Note on "Cancel" scenarios (e.g. T-FUNC-0203.01.02, T-FUNC-0204.01.02):
Cancel buttons are plain links in the templates, not a server-side action --
there is no cancel endpoint to POST to. These are tested as "a GET request
to the view renders the confirmation/edit page and does not change state",
which is the closest backend-testable equivalent of "the user did not
submit anything."
"""
import pytest
from django.urls import reverse

from accounts.factories import UserFactory
from planning.factories import CharacterFactory, LocationFactory, ItemFactory
from planning.models import Character, Location, Item
from .factories import NovelFactory, PartFactory, ChapterFactory, SceneFactory
from .models import Novel, Part, Chapter, Scene


NOVEL_FORM_FIELDS = {
    'title', 'subtitle', 'author_name', 'genre', 'target_word_count',
    'status', 'description', 'premise', 'pitch', 'parts_enabled',
}


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


# T-FUNC-0201.01.01
@pytest.mark.django_db
def test_create_novel_success(auth_client, user):
    response = auth_client.post(reverse('novel_create'), {
        'title': 'My First Novel',
        'target_word_count': 0,
        'status': 'not_started',
    })
    novel = Novel.objects.get(user=user, title='My First Novel')
    assert response.status_code == 302
    assert response.url == reverse('novel_detail', kwargs={'pk': novel.pk})

    list_response = auth_client.get(reverse('novel_list'))
    assert novel in list_response.context['novels']


# T-FUNC-0201.01.02
@pytest.mark.django_db
def test_create_novel_without_title_fails(auth_client, user):
    response = auth_client.post(reverse('novel_create'), {
        'title': '',
        'target_word_count': 0,
        'status': 'not_started',
    })
    assert response.status_code == 200
    assert not Novel.objects.filter(user=user).exists()
    assert 'Title is required' in response.context['form'].errors['title']


# T-UI-0201.01.01
@pytest.mark.django_db
def test_add_novel_form_presents_all_required_fields(auth_client):
    response = auth_client.get(reverse('novel_create'))
    assert set(response.context['form'].fields.keys()) == NOVEL_FORM_FIELDS


# T-FUNC-0201.02.01
@pytest.mark.django_db
def test_parts_enabled_defaults_to_no_on_add_novel(auth_client):
    response = auth_client.get(reverse('novel_create'))
    assert response.context['form']['parts_enabled'].value() is False


# T-UI-0203.01.01
@pytest.mark.django_db
def test_edit_novel_form_presents_all_editable_fields(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.get(reverse('novel_edit', kwargs={'pk': novel.pk}))
    assert set(response.context['form'].fields.keys()) == NOVEL_FORM_FIELDS


# T-FUNC-0202.01.01
@pytest.mark.django_db
def test_novel_structure_without_parts(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    default_part = Part.objects.create(novel=novel, title='_default', order=0)
    ChapterFactory(part=default_part)
    ChapterFactory(part=default_part)

    response = auth_client.get(reverse('novel_detail', kwargs={'pk': novel.pk}))
    assert len(response.context['chapters']) == 2
    assert len(response.context['parts']) == 0


# T-FUNC-0202.02.01
@pytest.mark.django_db
def test_novel_structure_with_parts(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    PartFactory(novel=novel)
    PartFactory(novel=novel)

    response = auth_client.get(reverse('novel_detail', kwargs={'pk': novel.pk}))
    assert len(response.context['parts']) == 2
    assert len(response.context['chapters']) == 0


# T-FUNC-0203.01.01
@pytest.mark.django_db
def test_edit_novel_success(auth_client, user):
    novel = NovelFactory(user=user, title='Original Title')
    response = auth_client.post(reverse('novel_edit', kwargs={'pk': novel.pk}), {
        'title': 'Updated Title',
        'target_word_count': novel.target_word_count,
        'status': novel.status,
    })
    novel.refresh_from_db()
    assert response.status_code == 302
    assert novel.title == 'Updated Title'

    detail_response = auth_client.get(reverse('novel_detail', kwargs={'pk': novel.pk}))
    assert detail_response.context['novel'].title == 'Updated Title'


# T-FUNC-0203.01.02
@pytest.mark.django_db
def test_cancel_editing_novel_leaves_it_unchanged(auth_client, user):
    novel = NovelFactory(user=user, title='Original Title')
    response = auth_client.get(reverse('novel_edit', kwargs={'pk': novel.pk}))
    novel.refresh_from_db()
    assert response.status_code == 200
    assert novel.title == 'Original Title'


# T-FUNC-0203.02.01
@pytest.mark.django_db
def test_enable_parts_on_existing_novel(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    response = auth_client.post(reverse('novel_edit', kwargs={'pk': novel.pk}), {
        'title': novel.title,
        'target_word_count': novel.target_word_count,
        'status': novel.status,
        'parts_enabled': True,
    })
    novel.refresh_from_db()
    assert response.status_code == 302
    assert novel.parts_enabled is True


# T-FUNC-0203.02.02
@pytest.mark.django_db
def test_disable_parts_moves_existing_chapters_to_novel_level(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel)
    chapter1 = ChapterFactory(part=part)
    chapter2 = ChapterFactory(part=part)

    response = auth_client.post(reverse('novel_edit', kwargs={'pk': novel.pk}), {
        'title': novel.title,
        'target_word_count': novel.target_word_count,
        'status': novel.status,
        'parts_enabled': False,
    })
    novel.refresh_from_db()
    chapter1.refresh_from_db()
    chapter2.refresh_from_db()

    assert response.status_code == 302
    assert novel.parts_enabled is False
    assert chapter1.part.title == '_default'
    assert chapter2.part.title == '_default'

    detail_response = auth_client.get(reverse('novel_detail', kwargs={'pk': novel.pk}))
    assert set(detail_response.context['chapters']) == {chapter1, chapter2}


# T-FUNC-0204.01.01
@pytest.mark.django_db
def test_archive_novel_success(auth_client, user):
    novel = NovelFactory(user=user, archived=False)
    response = auth_client.post(reverse('novel_archive', kwargs={'pk': novel.pk}))
    novel.refresh_from_db()
    assert response.status_code == 302
    assert response.url == reverse('novel_list')
    assert novel.archived is True

    list_response = auth_client.get(reverse('novel_list'))
    assert novel not in list_response.context['novels']


# T-FUNC-0204.01.02
@pytest.mark.django_db
def test_cancel_archiving_novel_leaves_it_unarchived(auth_client, user):
    novel = NovelFactory(user=user, archived=False)
    response = auth_client.get(reverse('novel_archive', kwargs={'pk': novel.pk}))
    novel.refresh_from_db()
    assert response.status_code == 200
    assert novel.archived is False


# T-FUNC-0205.01.01
@pytest.mark.django_db
def test_restore_novel_success(auth_client, user):
    novel = NovelFactory(user=user, archived=True)
    response = auth_client.post(reverse('novel_unarchive', kwargs={'pk': novel.pk}))
    novel.refresh_from_db()
    assert response.status_code == 302
    assert response.url == reverse('novel_list')
    assert novel.archived is False

    list_response = auth_client.get(reverse('novel_list'))
    assert novel in list_response.context['novels']
    archived_response = auth_client.get(reverse('archived_novel_list'))
    assert novel not in archived_response.context['novels']


# T-FUNC-0205.01.02
@pytest.mark.django_db
def test_cancel_unarchiving_novel_leaves_it_archived(auth_client, user):
    novel = NovelFactory(user=user, archived=True)
    response = auth_client.get(reverse('novel_unarchive', kwargs={'pk': novel.pk}))
    novel.refresh_from_db()
    assert response.status_code == 200
    assert novel.archived is True


# T-FUNC-0206.01.01
@pytest.mark.django_db
def test_delete_novel_success(auth_client, user):
    novel = NovelFactory(user=user)
    novel_pk = novel.pk
    response = auth_client.post(reverse('novel_delete', kwargs={'pk': novel.pk}))
    assert response.status_code == 302
    assert response.url == reverse('novel_list')
    assert not Novel.objects.filter(pk=novel_pk).exists()


# T-FUNC-0206.01.02
@pytest.mark.django_db
def test_cancel_deleting_novel_leaves_it_intact(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.get(reverse('novel_delete', kwargs={'pk': novel.pk}))
    assert response.status_code == 200
    assert Novel.objects.filter(pk=novel.pk).exists()


# T-DATA-0206.01.01
@pytest.mark.django_db
def test_delete_novel_cascades_to_children(auth_client, user):
    novel = NovelFactory(user=user)
    part = PartFactory(novel=novel)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter)
    character = CharacterFactory(novel=novel)
    location = LocationFactory(novel=novel)
    item = ItemFactory(novel=novel)

    auth_client.post(reverse('novel_delete', kwargs={'pk': novel.pk}))

    assert not Part.objects.filter(pk=part.pk).exists()
    assert not Chapter.objects.filter(pk=chapter.pk).exists()
    assert not Scene.objects.filter(pk=scene.pk).exists()
    assert not Character.objects.filter(pk=character.pk).exists()
    assert not Location.objects.filter(pk=location.pk).exists()
    assert not Item.objects.filter(pk=item.pk).exists()


# T-FUNC-0209.01.01
@pytest.mark.django_db
def test_novels_board_displayed_after_login(auth_client, user):
    novel1 = NovelFactory(user=user)
    novel2 = NovelFactory(user=user)
    response = auth_client.get(reverse('novel_list'))
    assert set(response.context['novels']) == {novel1, novel2}


# T-FUNC-0209.01.02
@pytest.mark.django_db
def test_archived_novels_do_not_appear_on_novels_board(auth_client, user):
    active_novel = NovelFactory(user=user, archived=False)
    archived_novel = NovelFactory(user=user, archived=True)
    response = auth_client.get(reverse('novel_list'))
    assert active_novel in response.context['novels']
    assert archived_novel not in response.context['novels']


# T-FUNC-0210.01.01
@pytest.mark.django_db
def test_navigate_into_novel_without_parts(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    default_part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter1 = ChapterFactory(part=default_part)
    chapter2 = ChapterFactory(part=default_part)

    response = auth_client.get(reverse('novel_detail', kwargs={'pk': novel.pk}))
    assert response.status_code == 200
    assert set(response.context['chapters']) == {chapter1, chapter2}


# T-FUNC-0210.01.02
@pytest.mark.django_db
def test_navigate_into_novel_with_parts(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part1 = PartFactory(novel=novel)
    part2 = PartFactory(novel=novel)

    response = auth_client.get(reverse('novel_detail', kwargs={'pk': novel.pk}))
    assert response.status_code == 200
    assert set(response.context['parts']) == {part1, part2}
