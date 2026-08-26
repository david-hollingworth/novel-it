"""
Backend/state tests for Location CRUD, types, image upload, and
relationships, converted from content/requirements/05-location-management.md
per data/requirements/phase-1-run-2-scope.yaml. 27 tests.

Excluded (per scope file): T-FUNC-0501.01.02 (archive), T-DATA-0510.01.01
(relationship cleanup on delete) -- archive/delete not yet implemented for
any planning entity.

See planning/test_character.py's module docstring for the rationale behind
the "appears in scenes" (modal-only) and "no parent summary section" tests
-- identical mechanics apply here.
"""
import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from accounts.factories import UserFactory
from novels.factories import NovelFactory
from .factories import LocationFactory, LocationTypeFactory, CharacterFactory, ItemFactory
from .models import Location, LocationType, Relationship


LOCATION_FORM_FIELDS = {'name', 'type', 'description', 'notes', 'image'}


def make_image_file(filename='test.png', content_type='image/png', pil_format='PNG'):
    buffer = io.BytesIO()
    Image.new('RGB', (1, 1), color='white').save(buffer, format=pil_format)
    buffer.seek(0)
    return SimpleUploadedFile(filename, buffer.read(), content_type=content_type)


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


# T-FUNC-0501.01.01
@pytest.mark.trace("T-FUNC-0501.01.01")
@pytest.mark.django_db
def test_locations_displayed_as_cards_on_board(auth_client, user):
    novel = NovelFactory(user=user)
    l1, l2, l3 = LocationFactory(novel=novel), LocationFactory(novel=novel), LocationFactory(novel=novel)
    response = auth_client.get(reverse('location_list', kwargs={'novel_pk': novel.pk}))
    assert set(response.context['locations']) == {l1, l2, l3}


# T-UI-0501.01.01
@pytest.mark.trace("T-UI-0501.01.01")
@pytest.mark.django_db
def test_no_parent_summary_section_on_location_list(auth_client, user):
    novel = NovelFactory(user=user)
    LocationFactory(novel=novel)
    response = auth_client.get(reverse('location_list', kwargs={'novel_pk': novel.pk}))
    assert set(response.context.keys()) & {'part', 'parts', 'chapter', 'chapters'} == set()


# T-UI-0501.02.01
@pytest.mark.trace("T-UI-0501.02.01")
@pytest.mark.django_db
def test_location_image_displayed_on_card_when_uploaded(auth_client, user):
    novel = NovelFactory(user=user)
    location = LocationFactory(novel=novel, image=make_image_file())
    response = auth_client.get(reverse('location_list', kwargs={'novel_pk': novel.pk}))
    assert location.image.name.encode() in response.content or location.image.url.encode() in response.content


# T-UI-0501.02.02
@pytest.mark.trace("T-UI-0501.02.02")
@pytest.mark.django_db
def test_location_card_displays_no_image_when_none_uploaded(auth_client, user):
    novel = NovelFactory(user=user)
    LocationFactory(novel=novel)
    response = auth_client.get(reverse('location_list', kwargs={'novel_pk': novel.pk}))
    assert not response.context['locations'][0].image


# T-FUNC-0502.01.01
@pytest.mark.trace("T-FUNC-0502.01.01")
@pytest.mark.django_db
def test_create_location_success(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('location_create', kwargs={'novel_pk': novel.pk}), {'name': 'The Crossroads Inn'})
    location = Location.objects.get(novel=novel, name='The Crossroads Inn')
    assert response.status_code == 302
    list_response = auth_client.get(reverse('location_list', kwargs={'novel_pk': novel.pk}))
    assert location in list_response.context['locations']


# T-FUNC-0502.01.02
@pytest.mark.trace("T-FUNC-0502.01.02")
@pytest.mark.django_db
def test_create_location_without_name_fails(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('location_create', kwargs={'novel_pk': novel.pk}), {'name': ''})
    assert response.status_code == 200
    assert not Location.objects.filter(novel=novel).exists()
    assert response.context['form'].errors.get('name')


# T-UI-0502.01.01
@pytest.mark.trace("T-UI-0502.01.01")
@pytest.mark.django_db
def test_add_location_form_presents_all_required_fields(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.get(reverse('location_create', kwargs={'novel_pk': novel.pk}))
    assert set(response.context['form'].fields.keys()) == LOCATION_FORM_FIELDS


# T-UI-0501.02.01 image test already covers upload display; next: edit/cancel

# T-FUNC-0503.01.01
@pytest.mark.trace("T-FUNC-0503.01.01")
@pytest.mark.django_db
def test_edit_location_success(auth_client, user):
    novel = NovelFactory(user=user)
    location = LocationFactory(novel=novel, name='Original Name')
    response = auth_client.post(
        reverse('location_edit', kwargs={'novel_pk': novel.pk, 'pk': location.pk}),
        {'name': 'Updated Name'},
    )
    location.refresh_from_db()
    assert response.status_code == 302
    assert location.name == 'Updated Name'


# T-FUNC-0503.01.02
@pytest.mark.trace("T-FUNC-0503.01.02")
@pytest.mark.django_db
def test_cancel_editing_location_leaves_it_unchanged(auth_client, user):
    novel = NovelFactory(user=user)
    location = LocationFactory(novel=novel, name='Original Name')
    response = auth_client.get(
        reverse('location_edit', kwargs={'novel_pk': novel.pk, 'pk': location.pk}))
    location.refresh_from_db()
    assert response.status_code == 200
    assert location.name == 'Original Name'


# T-UI-0503.01.01
@pytest.mark.trace("T-UI-0503.01.01")
@pytest.mark.django_db
def test_appears_in_scenes_readonly_on_edit_page(auth_client, user):
    novel = NovelFactory(user=user)
    location = LocationFactory(novel=novel)
    response = auth_client.get(
        reverse('modal_location_edit', kwargs={'novel_pk': novel.pk, 'pk': location.pk}))
    assert 'scene_occurrences' in response.context
    assert 'scene_occurrences' not in response.context['form'].fields


# T-FUNC-0502.03.01
@pytest.mark.trace("T-FUNC-0502.03.01")
@pytest.mark.django_db
def test_add_new_location_type_value(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('location_type_list', kwargs={'novel_pk': novel.pk}),
        {'action': 'add', 'name': 'Tavern'},
    )
    assert response.status_code == 302
    assert LocationType.objects.filter(novel=novel, name='Tavern').exists()


# T-FUNC-0502.03.02
@pytest.mark.trace("T-FUNC-0502.03.02")
@pytest.mark.django_db
def test_location_type_values_scoped_to_novel(auth_client, user):
    novel_a = NovelFactory(user=user)
    novel_b = NovelFactory(user=user)
    LocationTypeFactory(novel=novel_a, name='Tavern')

    response = auth_client.get(reverse('location_create', kwargs={'novel_pk': novel_b.pk}))
    type_queryset = response.context['form'].fields['type'].queryset
    assert not type_queryset.filter(name='Tavern').exists()


# T-FUNC-0502.04.01
@pytest.mark.trace("T-FUNC-0502.04.01")
@pytest.mark.django_db
def test_rename_location_type_value(auth_client, user):
    novel = NovelFactory(user=user)
    loc_type = LocationTypeFactory(novel=novel, name='Old Name')
    location = LocationFactory(novel=novel, type=loc_type)

    auth_client.post(
        reverse('location_type_list', kwargs={'novel_pk': novel.pk}),
        {'action': 'rename', 'category_id': loc_type.pk, 'name': 'New Name'},
    )
    loc_type.refresh_from_db()
    location.refresh_from_db()
    assert loc_type.name == 'New Name'
    assert location.type.name == 'New Name'


# T-FUNC-0502.05.01
@pytest.mark.trace("T-FUNC-0502.05.01")
@pytest.mark.django_db
def test_delete_location_type_value(auth_client, user):
    novel = NovelFactory(user=user)
    loc_type = LocationTypeFactory(novel=novel)
    type_pk = loc_type.pk

    auth_client.post(
        reverse('location_type_list', kwargs={'novel_pk': novel.pk}),
        {'action': 'delete', 'category_id': type_pk},
    )
    assert not LocationType.objects.filter(pk=type_pk).exists()


# T-FUNC-0502.05.02
@pytest.mark.trace("T-FUNC-0502.05.02")
@pytest.mark.django_db
def test_deleting_type_does_not_delete_assigned_locations(auth_client, user):
    novel = NovelFactory(user=user)
    loc_type = LocationTypeFactory(novel=novel)
    location = LocationFactory(novel=novel, type=loc_type)

    auth_client.post(
        reverse('location_type_list', kwargs={'novel_pk': novel.pk}),
        {'action': 'delete', 'category_id': loc_type.pk},
    )
    location.refresh_from_db()
    assert Location.objects.filter(pk=location.pk).exists()
    assert location.type is None


# T-FUNC-0502.02.01
@pytest.mark.trace("T-FUNC-0502.02.01")
@pytest.mark.django_db
def test_upload_location_image_on_add_page(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('location_create', kwargs={'novel_pk': novel.pk}),
        {'name': 'The Crossroads Inn', 'image': make_image_file()},
    )
    location = Location.objects.get(novel=novel, name='The Crossroads Inn')
    assert response.status_code == 302
    assert location.image


# T-FUNC-0502.02.02
@pytest.mark.trace("T-FUNC-0502.02.02")
@pytest.mark.django_db
def test_upload_location_image_on_edit_page(auth_client, user):
    novel = NovelFactory(user=user)
    location = LocationFactory(novel=novel)
    assert not location.image

    response = auth_client.post(
        reverse('location_edit', kwargs={'novel_pk': novel.pk, 'pk': location.pk}),
        {'name': location.name, 'image': make_image_file()},
    )
    location.refresh_from_db()
    assert response.status_code == 302
    assert location.image


# T-FUNC-0502.02.03
@pytest.mark.trace("T-FUNC-0502.02.03")
@pytest.mark.django_db
def test_replace_existing_location_image(auth_client, user):
    novel = NovelFactory(user=user)
    location = LocationFactory(novel=novel, image=make_image_file('original.png'))
    original_name = location.image.name

    response = auth_client.post(
        reverse('location_edit', kwargs={'novel_pk': novel.pk, 'pk': location.pk}),
        {'name': location.name, 'image': make_image_file('replacement.png')},
    )
    location.refresh_from_db()
    assert response.status_code == 302
    assert location.image.name != original_name


# T-SEC-0502.01.01
@pytest.mark.trace("T-SEC-0502.01.01")
@pytest.mark.django_db
def test_png_image_accepted(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('location_create', kwargs={'novel_pk': novel.pk}),
        {'name': 'Loc', 'image': make_image_file('test.png', 'image/png', 'PNG')},
    )
    assert response.status_code == 302


# T-SEC-0502.01.02
@pytest.mark.trace("T-SEC-0502.01.02")
@pytest.mark.django_db
def test_jpg_image_accepted(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('location_create', kwargs={'novel_pk': novel.pk}),
        {'name': 'Loc', 'image': make_image_file('test.jpg', 'image/jpeg', 'JPEG')},
    )
    assert response.status_code == 302


# T-SEC-0502.01.03
@pytest.mark.trace("T-SEC-0502.01.03")
@pytest.mark.django_db
def test_jpeg_image_accepted(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('location_create', kwargs={'novel_pk': novel.pk}),
        {'name': 'Loc', 'image': make_image_file('test.jpeg', 'image/jpeg', 'JPEG')},
    )
    assert response.status_code == 302


# T-SEC-0502.01.04
@pytest.mark.trace("T-SEC-0502.01.04")
@pytest.mark.django_db
def test_unsupported_image_extension_rejected(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('location_create', kwargs={'novel_pk': novel.pk}),
        {'name': 'Loc', 'image': make_image_file('test.gif', 'image/gif', 'PNG')},
    )
    assert response.status_code == 200
    assert not Location.objects.filter(novel=novel).exists()
    assert 'Only .jpg, .jpeg, and .png images are allowed.' in response.context['form'].errors['image']


# T-FUNC-0510.01.01
@pytest.mark.trace("T-FUNC-0510.01.01")
@pytest.mark.django_db
def test_define_relationship_between_location_and_character(auth_client, user):
    novel = NovelFactory(user=user)
    location = LocationFactory(novel=novel)
    character = CharacterFactory(novel=novel)

    response = auth_client.post(
        reverse('relationship_add', kwargs={'novel_pk': novel.pk}),
        {
            'from_type': 'location', 'from_id': location.pk,
            'to_type': 'character', 'to_id': character.pk,
            'label': 'inhabited by', 'reverse_label': 'inhabits',
        },
    )
    assert response.status_code == 200
    assert Relationship.objects.filter(novel=novel, label='inhabited by', reverse_label='inhabits').exists()


# T-FUNC-0510.01.02
@pytest.mark.trace("T-FUNC-0510.01.02")
@pytest.mark.django_db
def test_define_relationship_between_two_locations(auth_client, user):
    novel = NovelFactory(user=user)
    loc_a = LocationFactory(novel=novel)
    loc_b = LocationFactory(novel=novel)

    response = auth_client.post(
        reverse('relationship_add', kwargs={'novel_pk': novel.pk}),
        {
            'from_type': 'location', 'from_id': loc_a.pk,
            'to_type': 'location', 'to_id': loc_b.pk,
            'label': 'borders', 'reverse_label': 'bordered by',
        },
    )
    assert response.status_code == 200
    assert Relationship.objects.filter(novel=novel, label='borders', reverse_label='bordered by').exists()


# T-FUNC-0510.02.01
@pytest.mark.trace("T-FUNC-0510.02.01")
@pytest.mark.django_db
def test_relationship_appears_on_both_entities_with_correct_labels(auth_client, user):
    novel = NovelFactory(user=user)
    location = LocationFactory(novel=novel)
    character = CharacterFactory(novel=novel)
    auth_client.post(
        reverse('relationship_add', kwargs={'novel_pk': novel.pk}),
        {
            'from_type': 'location', 'from_id': location.pk,
            'to_type': 'character', 'to_id': character.pk,
            'label': 'inhabited by', 'reverse_label': 'inhabits',
        },
    )

    loc_response = auth_client.get(
        reverse('modal_location_detail', kwargs={'novel_pk': novel.pk, 'pk': location.pk}))
    loc_labels = [r['display_label'] for r in loc_response.context['relationships']]
    assert 'inhabited by' in loc_labels

    char_response = auth_client.get(
        reverse('modal_character_detail', kwargs={'novel_pk': novel.pk, 'pk': character.pk}))
    char_labels = [r['display_label'] for r in char_response.context['relationships']]
    assert 'inhabits' in char_labels


# T-FUNC-0510.03.01
@pytest.mark.trace("T-FUNC-0510.03.01")
@pytest.mark.django_db
def test_edit_relationship_from_location_page(auth_client, user):
    novel = NovelFactory(user=user)
    location = LocationFactory(novel=novel)
    item = ItemFactory(novel=novel)
    auth_client.post(
        reverse('relationship_add', kwargs={'novel_pk': novel.pk}),
        {
            'from_type': 'location', 'from_id': location.pk,
            'to_type': 'item', 'to_id': item.pk,
            'label': 'contains', 'reverse_label': 'found in',
        },
    )
    rel = Relationship.objects.get(novel=novel)

    response = auth_client.post(
        reverse('relationship_edit', kwargs={'novel_pk': novel.pk, 'pk': rel.pk}),
        {
            'entity_type': 'location', 'entity_id': location.pk,
            'label': 'houses', 'reverse_label': 'housed in',
        },
    )
    rel.refresh_from_db()
    assert response.status_code == 200
    assert rel.label == 'houses'
    assert rel.reverse_label == 'housed in'


# T-FUNC-0510.04.01
@pytest.mark.trace("T-FUNC-0510.04.01")
@pytest.mark.django_db
def test_delete_relationship(auth_client, user):
    novel = NovelFactory(user=user)
    location = LocationFactory(novel=novel)
    character = CharacterFactory(novel=novel)
    auth_client.post(
        reverse('relationship_add', kwargs={'novel_pk': novel.pk}),
        {
            'from_type': 'location', 'from_id': location.pk,
            'to_type': 'character', 'to_id': character.pk,
            'label': 'inhabited by', 'reverse_label': 'inhabits',
        },
    )
    rel = Relationship.objects.get(novel=novel)

    response = auth_client.post(
        reverse('relationship_delete', kwargs={'novel_pk': novel.pk, 'pk': rel.pk}),
        {'entity_type': 'location', 'entity_id': location.pk},
    )
    assert response.status_code == 200
    assert not Relationship.objects.filter(pk=rel.pk).exists()
    assert Location.objects.filter(pk=location.pk).exists()
