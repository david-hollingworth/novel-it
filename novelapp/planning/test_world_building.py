"""
Backend/state tests for World Building CRUD, types, image upload, and
relationships, converted from content/requirements/07-world-building.md per
data/requirements/phase-1-run-2-scope.yaml. 27 tests.

Excluded (per scope file): T-FUNC-0701.01.02 (archive), T-DATA-0710.01.01
(relationship cleanup on delete) -- archive/delete not yet implemented for
any planning entity. (World Building itself is fully implemented -- FEAT-0701
through FEAT-0710 -- only its archive/delete pair is excluded, same as every
other planning entity.)

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
from .factories import WorldBuildingFactory, WorldBuildingTypeFactory, CharacterFactory, LocationFactory
from .models import WorldBuilding, WorldBuildingType, Relationship


WORLD_BUILDING_FORM_FIELDS = {'name', 'type', 'description', 'notes', 'image'}


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


# T-FUNC-0701.01.01
@pytest.mark.trace("T-FUNC-0701.01.01")
@pytest.mark.django_db
def test_world_building_items_displayed_as_cards_on_board(auth_client, user):
    novel = NovelFactory(user=user)
    w1, w2, w3 = WorldBuildingFactory(novel=novel), WorldBuildingFactory(novel=novel), WorldBuildingFactory(novel=novel)
    response = auth_client.get(reverse('world_building_list', kwargs={'novel_pk': novel.pk}))
    assert set(response.context['world_building_items']) == {w1, w2, w3}


# T-UI-0701.01.01
@pytest.mark.trace("T-UI-0701.01.01")
@pytest.mark.django_db
def test_no_parent_summary_section_on_world_building_list(auth_client, user):
    novel = NovelFactory(user=user)
    WorldBuildingFactory(novel=novel)
    response = auth_client.get(reverse('world_building_list', kwargs={'novel_pk': novel.pk}))
    assert set(response.context.keys()) & {'part', 'parts', 'chapter', 'chapters'} == set()


# T-UI-0701.02.01
@pytest.mark.trace("T-UI-0701.02.01")
@pytest.mark.django_db
def test_world_building_image_displayed_on_card_when_uploaded(auth_client, user):
    novel = NovelFactory(user=user)
    item = WorldBuildingFactory(novel=novel, image=make_image_file())
    response = auth_client.get(reverse('world_building_list', kwargs={'novel_pk': novel.pk}))
    assert item.image.name.encode() in response.content or item.image.url.encode() in response.content


# T-UI-0701.02.02
@pytest.mark.trace("T-UI-0701.02.02")
@pytest.mark.django_db
def test_world_building_card_displays_no_image_when_none_uploaded(auth_client, user):
    novel = NovelFactory(user=user)
    WorldBuildingFactory(novel=novel)
    response = auth_client.get(reverse('world_building_list', kwargs={'novel_pk': novel.pk}))
    assert not response.context['world_building_items'][0].image


# T-FUNC-0702.01.01
@pytest.mark.trace("T-FUNC-0702.01.01")
@pytest.mark.django_db
def test_create_world_building_item_success(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('world_building_create', kwargs={'novel_pk': novel.pk}), {'name': 'The Old Religion'})
    item = WorldBuilding.objects.get(novel=novel, name='The Old Religion')
    assert response.status_code == 302
    list_response = auth_client.get(reverse('world_building_list', kwargs={'novel_pk': novel.pk}))
    assert item in list_response.context['world_building_items']


# T-FUNC-0702.01.02
@pytest.mark.trace("T-FUNC-0702.01.02")
@pytest.mark.django_db
def test_create_world_building_item_without_name_fails(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('world_building_create', kwargs={'novel_pk': novel.pk}), {'name': ''})
    assert response.status_code == 200
    assert not WorldBuilding.objects.filter(novel=novel).exists()
    assert 'Name is required' in response.context['form'].errors['name']


# T-UI-0702.01.01
@pytest.mark.trace("T-UI-0702.01.01")
@pytest.mark.django_db
def test_add_world_building_form_presents_all_required_fields(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.get(reverse('world_building_create', kwargs={'novel_pk': novel.pk}))
    assert set(response.context['form'].fields.keys()) == WORLD_BUILDING_FORM_FIELDS


# T-FUNC-0703.01.01
@pytest.mark.trace("T-FUNC-0703.01.01")
@pytest.mark.django_db
def test_edit_world_building_item_success(auth_client, user):
    novel = NovelFactory(user=user)
    item = WorldBuildingFactory(novel=novel, name='Original Name')
    response = auth_client.post(
        reverse('world_building_edit', kwargs={'novel_pk': novel.pk, 'pk': item.pk}),
        {'name': 'Updated Name'},
    )
    item.refresh_from_db()
    assert response.status_code == 302
    assert item.name == 'Updated Name'


# T-FUNC-0703.01.02
@pytest.mark.trace("T-FUNC-0703.01.02")
@pytest.mark.django_db
def test_cancel_editing_world_building_item_leaves_it_unchanged(auth_client, user):
    novel = NovelFactory(user=user)
    item = WorldBuildingFactory(novel=novel, name='Original Name')
    response = auth_client.get(
        reverse('world_building_edit', kwargs={'novel_pk': novel.pk, 'pk': item.pk}))
    item.refresh_from_db()
    assert response.status_code == 200
    assert item.name == 'Original Name'


# T-UI-0703.01.01
@pytest.mark.trace("T-UI-0703.01.01")
@pytest.mark.django_db
def test_appears_in_scenes_readonly_on_edit_page(auth_client, user):
    novel = NovelFactory(user=user)
    item = WorldBuildingFactory(novel=novel)
    response = auth_client.get(
        reverse('modal_world_building_edit', kwargs={'novel_pk': novel.pk, 'pk': item.pk}))
    assert 'scene_occurrences' in response.context
    assert 'scene_occurrences' not in response.context['form'].fields


# T-FUNC-0702.03.01
@pytest.mark.trace("T-FUNC-0702.03.01")
@pytest.mark.django_db
def test_add_new_world_building_type_value(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('world_building_type_list', kwargs={'novel_pk': novel.pk}),
        {'action': 'add', 'name': 'Religion'},
    )
    assert response.status_code == 302
    assert WorldBuildingType.objects.filter(novel=novel, name='Religion').exists()


# T-FUNC-0702.03.02
@pytest.mark.trace("T-FUNC-0702.03.02")
@pytest.mark.django_db
def test_world_building_type_values_scoped_to_novel(auth_client, user):
    novel_a = NovelFactory(user=user)
    novel_b = NovelFactory(user=user)
    WorldBuildingTypeFactory(novel=novel_a, name='Religion')

    response = auth_client.get(reverse('world_building_create', kwargs={'novel_pk': novel_b.pk}))
    type_queryset = response.context['form'].fields['type'].queryset
    assert not type_queryset.filter(name='Religion').exists()


# T-FUNC-0702.04.01
@pytest.mark.trace("T-FUNC-0702.04.01")
@pytest.mark.django_db
def test_rename_world_building_type_value(auth_client, user):
    novel = NovelFactory(user=user)
    wb_type = WorldBuildingTypeFactory(novel=novel, name='Old Name')
    item = WorldBuildingFactory(novel=novel, type=wb_type)

    auth_client.post(
        reverse('world_building_type_list', kwargs={'novel_pk': novel.pk}),
        {'action': 'rename', 'category_id': wb_type.pk, 'name': 'New Name'},
    )
    wb_type.refresh_from_db()
    item.refresh_from_db()
    assert wb_type.name == 'New Name'
    assert item.type.name == 'New Name'


# T-FUNC-0702.05.01
@pytest.mark.trace("T-FUNC-0702.05.01")
@pytest.mark.django_db
def test_delete_world_building_type_value(auth_client, user):
    novel = NovelFactory(user=user)
    wb_type = WorldBuildingTypeFactory(novel=novel)
    type_pk = wb_type.pk

    auth_client.post(
        reverse('world_building_type_list', kwargs={'novel_pk': novel.pk}),
        {'action': 'delete', 'category_id': type_pk},
    )
    assert not WorldBuildingType.objects.filter(pk=type_pk).exists()


# T-FUNC-0702.05.02
@pytest.mark.trace("T-FUNC-0702.05.02")
@pytest.mark.django_db
def test_deleting_type_does_not_delete_assigned_world_building_items(auth_client, user):
    novel = NovelFactory(user=user)
    wb_type = WorldBuildingTypeFactory(novel=novel)
    item = WorldBuildingFactory(novel=novel, type=wb_type)

    auth_client.post(
        reverse('world_building_type_list', kwargs={'novel_pk': novel.pk}),
        {'action': 'delete', 'category_id': wb_type.pk},
    )
    item.refresh_from_db()
    assert WorldBuilding.objects.filter(pk=item.pk).exists()
    assert item.type is None


# T-FUNC-0702.02.01
@pytest.mark.trace("T-FUNC-0702.02.01")
@pytest.mark.django_db
def test_upload_world_building_image_on_add_page(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('world_building_create', kwargs={'novel_pk': novel.pk}),
        {'name': 'The Old Religion', 'image': make_image_file()},
    )
    item = WorldBuilding.objects.get(novel=novel, name='The Old Religion')
    assert response.status_code == 302
    assert item.image


# T-FUNC-0702.02.02
@pytest.mark.trace("T-FUNC-0702.02.02")
@pytest.mark.django_db
def test_upload_world_building_image_on_edit_page(auth_client, user):
    novel = NovelFactory(user=user)
    item = WorldBuildingFactory(novel=novel)
    assert not item.image

    response = auth_client.post(
        reverse('world_building_edit', kwargs={'novel_pk': novel.pk, 'pk': item.pk}),
        {'name': item.name, 'image': make_image_file()},
    )
    item.refresh_from_db()
    assert response.status_code == 302
    assert item.image


# T-FUNC-0702.02.03
@pytest.mark.trace("T-FUNC-0702.02.03")
@pytest.mark.django_db
def test_replace_existing_world_building_image(auth_client, user):
    novel = NovelFactory(user=user)
    item = WorldBuildingFactory(novel=novel, image=make_image_file('original.png'))
    original_name = item.image.name

    response = auth_client.post(
        reverse('world_building_edit', kwargs={'novel_pk': novel.pk, 'pk': item.pk}),
        {'name': item.name, 'image': make_image_file('replacement.png')},
    )
    item.refresh_from_db()
    assert response.status_code == 302
    assert item.image.name != original_name


# T-SEC-0702.01.01
@pytest.mark.trace("T-SEC-0702.01.01")
@pytest.mark.django_db
def test_png_image_accepted(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('world_building_create', kwargs={'novel_pk': novel.pk}),
        {'name': 'Thing', 'image': make_image_file('test.png', 'image/png', 'PNG')},
    )
    assert response.status_code == 302


# T-SEC-0702.01.02
@pytest.mark.trace("T-SEC-0702.01.02")
@pytest.mark.django_db
def test_jpg_image_accepted(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('world_building_create', kwargs={'novel_pk': novel.pk}),
        {'name': 'Thing', 'image': make_image_file('test.jpg', 'image/jpeg', 'JPEG')},
    )
    assert response.status_code == 302


# T-SEC-0702.01.03
@pytest.mark.trace("T-SEC-0702.01.03")
@pytest.mark.django_db
def test_jpeg_image_accepted(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('world_building_create', kwargs={'novel_pk': novel.pk}),
        {'name': 'Thing', 'image': make_image_file('test.jpeg', 'image/jpeg', 'JPEG')},
    )
    assert response.status_code == 302


# T-SEC-0702.01.04
@pytest.mark.trace("T-SEC-0702.01.04")
@pytest.mark.django_db
def test_unsupported_image_extension_rejected(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('world_building_create', kwargs={'novel_pk': novel.pk}),
        {'name': 'Thing', 'image': make_image_file('test.gif', 'image/gif', 'PNG')},
    )
    assert response.status_code == 200
    assert not WorldBuilding.objects.filter(novel=novel).exists()
    assert 'Only .jpg, .jpeg, and .png images are allowed.' in response.context['form'].errors['image']


# T-FUNC-0710.01.01
@pytest.mark.trace("T-FUNC-0710.01.01")
@pytest.mark.django_db
def test_define_relationship_between_world_building_item_and_character(auth_client, user):
    novel = NovelFactory(user=user)
    item = WorldBuildingFactory(novel=novel)
    character = CharacterFactory(novel=novel)

    response = auth_client.post(
        reverse('relationship_add', kwargs={'novel_pk': novel.pk}),
        {
            'from_type': 'world_building', 'from_id': item.pk,
            'to_type': 'character', 'to_id': character.pk,
            'label': 'practised by', 'reverse_label': 'follows',
        },
    )
    assert response.status_code == 200
    assert Relationship.objects.filter(novel=novel, label='practised by', reverse_label='follows').exists()


# T-FUNC-0710.01.02
@pytest.mark.trace("T-FUNC-0710.01.02")
@pytest.mark.django_db
def test_define_relationship_between_two_world_building_items(auth_client, user):
    novel = NovelFactory(user=user)
    item_a = WorldBuildingFactory(novel=novel)
    item_b = WorldBuildingFactory(novel=novel)

    response = auth_client.post(
        reverse('relationship_add', kwargs={'novel_pk': novel.pk}),
        {
            'from_type': 'world_building', 'from_id': item_a.pk,
            'to_type': 'world_building', 'to_id': item_b.pk,
            'label': 'influences', 'reverse_label': 'influenced by',
        },
    )
    assert response.status_code == 200
    assert Relationship.objects.filter(novel=novel, label='influences', reverse_label='influenced by').exists()


# T-FUNC-0710.02.01
@pytest.mark.trace("T-FUNC-0710.02.01")
@pytest.mark.django_db
def test_relationship_appears_on_both_entities_with_correct_labels(auth_client, user):
    novel = NovelFactory(user=user)
    item = WorldBuildingFactory(novel=novel)
    location = LocationFactory(novel=novel)
    auth_client.post(
        reverse('relationship_add', kwargs={'novel_pk': novel.pk}),
        {
            'from_type': 'world_building', 'from_id': item.pk,
            'to_type': 'location', 'to_id': location.pk,
            'label': 'governs', 'reverse_label': 'governed by',
        },
    )

    item_response = auth_client.get(
        reverse('modal_world_building_detail', kwargs={'novel_pk': novel.pk, 'pk': item.pk}))
    item_labels = [r['display_label'] for r in item_response.context['relationships']]
    assert 'governs' in item_labels

    loc_response = auth_client.get(
        reverse('modal_location_detail', kwargs={'novel_pk': novel.pk, 'pk': location.pk}))
    loc_labels = [r['display_label'] for r in loc_response.context['relationships']]
    assert 'governed by' in loc_labels


# T-FUNC-0710.03.01
@pytest.mark.trace("T-FUNC-0710.03.01")
@pytest.mark.django_db
def test_edit_relationship_from_world_building_page(auth_client, user):
    novel = NovelFactory(user=user)
    item = WorldBuildingFactory(novel=novel)
    character = CharacterFactory(novel=novel)
    auth_client.post(
        reverse('relationship_add', kwargs={'novel_pk': novel.pk}),
        {
            'from_type': 'world_building', 'from_id': item.pk,
            'to_type': 'character', 'to_id': character.pk,
            'label': 'practised by', 'reverse_label': 'follows',
        },
    )
    rel = Relationship.objects.get(novel=novel)

    response = auth_client.post(
        reverse('relationship_edit', kwargs={'novel_pk': novel.pk, 'pk': rel.pk}),
        {
            'entity_type': 'world_building', 'entity_id': item.pk,
            'label': 'worshipped by', 'reverse_label': 'worships',
        },
    )
    rel.refresh_from_db()
    assert response.status_code == 200
    assert rel.label == 'worshipped by'
    assert rel.reverse_label == 'worships'


# T-FUNC-0710.04.01
@pytest.mark.trace("T-FUNC-0710.04.01")
@pytest.mark.django_db
def test_delete_relationship(auth_client, user):
    novel = NovelFactory(user=user)
    item = WorldBuildingFactory(novel=novel)
    character = CharacterFactory(novel=novel)
    auth_client.post(
        reverse('relationship_add', kwargs={'novel_pk': novel.pk}),
        {
            'from_type': 'world_building', 'from_id': item.pk,
            'to_type': 'character', 'to_id': character.pk,
            'label': 'practised by', 'reverse_label': 'follows',
        },
    )
    rel = Relationship.objects.get(novel=novel)

    response = auth_client.post(
        reverse('relationship_delete', kwargs={'novel_pk': novel.pk, 'pk': rel.pk}),
        {'entity_type': 'world_building', 'entity_id': item.pk},
    )
    assert response.status_code == 200
    assert not Relationship.objects.filter(pk=rel.pk).exists()
    assert WorldBuilding.objects.filter(pk=item.pk).exists()
