"""
Backend/state tests for Part CRUD and the branching archive logic, converted
from content/requirements/02-novel-management.md per
data/requirements/phase-1-run-2-scope.yaml.

Covers the "Part" sub-batch: T-FUNC-0211.01.01 through T-DATA-0215.01.01
(19 tests).

Note on "Cancel"/"options displayed" scenarios: see novels/test_novel.py's
module docstring for the Cancel-scenario testing rationale. The "options
displayed" scenarios (T-FUNC-0213.01.01/.05/.07) are tested by asserting on
the has_active_chapters/is_last_active_part context returned by a GET to the
archive URL -- those flags are what the template branches its prompt on.
"""
import pytest
from django.urls import reverse

from accounts.factories import UserFactory
from .factories import NovelFactory, PartFactory, ChapterFactory, SceneFactory
from .models import Novel, Part, Chapter, Scene


PART_FORM_FIELDS = {'title', 'description', 'notes', 'status'}


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


# T-FUNC-0211.01.01
@pytest.mark.django_db
def test_create_part_success(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    response = auth_client.post(
        reverse('part_create', kwargs={'novel_pk': novel.pk}),
        {'title': 'Act One', 'status': 'not_started'},
    )
    part = Part.objects.get(novel=novel, title='Act One')
    assert response.status_code == 302
    assert response.url == reverse('novel_detail', kwargs={'pk': novel.pk})

    detail_response = auth_client.get(reverse('novel_detail', kwargs={'pk': novel.pk}))
    assert part in detail_response.context['parts']


# T-FUNC-0211.01.02
@pytest.mark.django_db
def test_create_part_and_assign_existing_chapters(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    default_part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter1 = ChapterFactory(part=default_part)
    chapter2 = ChapterFactory(part=default_part)

    response = auth_client.post(
        reverse('part_create', kwargs={'novel_pk': novel.pk}),
        {
            'title': 'Act One', 'status': 'not_started',
            'selected_chapters': [chapter1.pk, chapter2.pk],
        },
    )
    part = Part.objects.get(novel=novel, title='Act One')
    chapter1.refresh_from_db()
    chapter2.refresh_from_db()

    assert response.status_code == 302
    assert chapter1.part == part
    assert chapter2.part == part


# T-FUNC-0211.01.03
@pytest.mark.django_db
def test_add_part_button_not_available_when_parts_disabled(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    response = auth_client.get(reverse('novel_detail', kwargs={'pk': novel.pk}))
    add_part_url = reverse('part_create', kwargs={'novel_pk': novel.pk})
    assert add_part_url.encode() not in response.content


# T-UI-0211.01.01
@pytest.mark.django_db
def test_add_part_form_presents_all_required_fields(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    response = auth_client.get(reverse('part_create', kwargs={'novel_pk': novel.pk}))
    assert set(response.context['form'].fields.keys()) == PART_FORM_FIELDS


# T-FUNC-0212.01.01
@pytest.mark.django_db
def test_edit_part_success(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel, title='Original Name')
    response = auth_client.post(
        reverse('part_edit', kwargs={'novel_pk': novel.pk, 'part_pk': part.pk}),
        {'title': 'Updated Name', 'status': part.status},
    )
    part.refresh_from_db()
    assert response.status_code == 302
    assert part.title == 'Updated Name'


# T-FUNC-0212.01.02
@pytest.mark.django_db
def test_cancel_editing_part_leaves_it_unchanged(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel, title='Original Name')
    response = auth_client.get(
        reverse('part_edit', kwargs={'novel_pk': novel.pk, 'part_pk': part.pk}))
    part.refresh_from_db()
    assert response.status_code == 200
    assert part.title == 'Original Name'


# T-UI-0212.01.01
@pytest.mark.django_db
def test_edit_part_form_presents_all_required_fields(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel)
    response = auth_client.get(
        reverse('part_edit', kwargs={'novel_pk': novel.pk, 'part_pk': part.pk}))
    assert set(response.context['form'].fields.keys()) == PART_FORM_FIELDS


# T-FUNC-0213.01.01
@pytest.mark.django_db
def test_archive_part_options_with_multiple_active_parts(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel)
    PartFactory(novel=novel)  # a second active part
    ChapterFactory(part=part)

    response = auth_client.get(
        reverse('part_archive', kwargs={'novel_pk': novel.pk, 'part_pk': part.pk}))
    assert response.status_code == 200
    assert response.context['has_active_chapters'] is True
    assert response.context['is_last_active_part'] is False


# T-FUNC-0213.01.02
@pytest.mark.django_db
def test_archive_part_moving_chapters_to_another_part(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel)
    destination = PartFactory(novel=novel)
    chapter = ChapterFactory(part=part)

    response = auth_client.post(
        reverse('part_archive', kwargs={'novel_pk': novel.pk, 'part_pk': part.pk}),
        {'action': 'move_to_part', 'destination_part_id': destination.pk},
    )
    part.refresh_from_db()
    chapter.refresh_from_db()

    assert response.status_code == 302
    assert part.archived is True
    assert chapter.part == destination


# T-FUNC-0213.01.03
@pytest.mark.django_db
def test_archive_part_and_its_chapters(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel)
    chapter = ChapterFactory(part=part)

    response = auth_client.post(
        reverse('part_archive', kwargs={'novel_pk': novel.pk, 'part_pk': part.pk}),
        {'action': 'archive_with_chapters'},
    )
    part.refresh_from_db()
    chapter.refresh_from_db()

    assert response.status_code == 302
    assert part.archived is True
    assert chapter.archived is True


# T-FUNC-0213.01.04
@pytest.mark.django_db
def test_cancel_archiving_part_leaves_it_unarchived(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel, archived=False)
    response = auth_client.get(
        reverse('part_archive', kwargs={'novel_pk': novel.pk, 'part_pk': part.pk}))
    part.refresh_from_db()
    assert response.status_code == 200
    assert part.archived is False


# T-FUNC-0213.01.05
@pytest.mark.django_db
def test_archive_part_options_with_only_one_active_part(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel)
    ChapterFactory(part=part)

    response = auth_client.get(
        reverse('part_archive', kwargs={'novel_pk': novel.pk, 'part_pk': part.pk}))
    assert response.status_code == 200
    assert response.context['has_active_chapters'] is True
    assert response.context['is_last_active_part'] is True


# T-FUNC-0213.01.06
@pytest.mark.django_db
def test_archive_final_part_moves_chapters_to_novel(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel)
    chapter = ChapterFactory(part=part)

    response = auth_client.post(
        reverse('part_archive', kwargs={'novel_pk': novel.pk, 'part_pk': part.pk}),
        {'action': 'move_to_novel'},
    )
    novel.refresh_from_db()
    part.refresh_from_db()
    chapter.refresh_from_db()

    assert response.status_code == 302
    assert part.archived is True
    assert chapter.part.title == '_default'
    assert novel.parts_enabled is False

    detail_response = auth_client.get(reverse('novel_detail', kwargs={'pk': novel.pk}))
    assert chapter in detail_response.context['chapters']


# T-FUNC-0213.01.07
@pytest.mark.django_db
def test_archive_part_with_no_chapters(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel)

    prompt_response = auth_client.get(
        reverse('part_archive', kwargs={'novel_pk': novel.pk, 'part_pk': part.pk}))
    assert prompt_response.context['has_active_chapters'] is False

    response = auth_client.post(
        reverse('part_archive', kwargs={'novel_pk': novel.pk, 'part_pk': part.pk}),
        {'action': 'archive_only'},
    )
    part.refresh_from_db()
    assert response.status_code == 302
    assert part.archived is True


# T-FUNC-0214.01.01
@pytest.mark.django_db
def test_restore_part_success(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel, archived=True)

    response = auth_client.post(
        reverse('part_unarchive', kwargs={'novel_pk': novel.pk, 'part_pk': part.pk}))
    part.refresh_from_db()
    assert response.status_code == 302
    assert response.url == reverse('novel_detail', kwargs={'pk': novel.pk})
    assert part.archived is False

    detail_response = auth_client.get(reverse('novel_detail', kwargs={'pk': novel.pk}))
    assert part in detail_response.context['parts']
    archived_response = auth_client.get(
        reverse('archived_part_list', kwargs={'novel_pk': novel.pk}))
    assert part not in archived_response.context['parts']


# T-FUNC-0214.01.02
@pytest.mark.django_db
def test_cancel_unarchiving_part_leaves_it_archived(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel, archived=True)
    response = auth_client.get(
        reverse('part_unarchive', kwargs={'novel_pk': novel.pk, 'part_pk': part.pk}))
    part.refresh_from_db()
    assert response.status_code == 200
    assert part.archived is True


# T-FUNC-0215.01.01
@pytest.mark.django_db
def test_delete_part_success(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel)
    part_pk = part.pk

    response = auth_client.post(
        reverse('part_delete', kwargs={'novel_pk': novel.pk, 'part_pk': part.pk}))
    assert response.status_code == 302
    assert response.url == reverse('novel_detail', kwargs={'pk': novel.pk})
    assert not Part.objects.filter(pk=part_pk).exists()


# T-FUNC-0215.01.02
@pytest.mark.django_db
def test_cancel_deleting_part_leaves_it_intact(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel)
    response = auth_client.get(
        reverse('part_delete', kwargs={'novel_pk': novel.pk, 'part_pk': part.pk}))
    assert response.status_code == 200
    assert Part.objects.filter(pk=part.pk).exists()


# T-DATA-0215.01.01
@pytest.mark.django_db
def test_delete_part_cascades_to_chapters_and_scenes(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=True)
    part = PartFactory(novel=novel)
    chapter1 = ChapterFactory(part=part)
    chapter2 = ChapterFactory(part=part)
    scene1 = SceneFactory(chapter=chapter1)
    scene2 = SceneFactory(chapter=chapter2)

    auth_client.post(
        reverse('part_delete', kwargs={'novel_pk': novel.pk, 'part_pk': part.pk}))

    assert not Chapter.objects.filter(pk__in=[chapter1.pk, chapter2.pk]).exists()
    assert not Scene.objects.filter(pk__in=[scene1.pk, scene2.pk]).exists()
