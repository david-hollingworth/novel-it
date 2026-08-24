"""
Backend/state tests for Item CRUD, types, image upload, and relationships,
converted from content/requirements/06-item-management.md per
data/requirements/phase-1-run-2-scope.yaml. 27 tests.

Excluded (per scope file): T-FUNC-0601.01.02 (archive), T-DATA-0610.01.01
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
from .factories import ItemFactory, ItemTypeFactory, CharacterFactory, LocationFactory
from .models import Item, ItemType, Relationship


ITEM_FORM_FIELDS = {'name', 'type', 'history', 'properties_and_abilities', 'description', 'notes', 'image'}


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


# T-FUNC-0601.01.01
@pytest.mark.trace("T-FUNC-0601.01.01")
@pytest.mark.django_db
def test_items_displayed_as_cards_on_board(auth_client, user):
    novel = NovelFactory(user=user)
    i1, i2, i3 = ItemFactory(novel=novel), ItemFactory(novel=novel), ItemFactory(novel=novel)
    response = auth_client.get(reverse('item_list', kwargs={'novel_pk': novel.pk}))
    assert set(response.context['items']) == {i1, i2, i3}


# T-UI-0601.01.01
@pytest.mark.trace("T-UI-0601.01.01")
@pytest.mark.django_db
def test_no_parent_summary_section_on_item_list(auth_client, user):
    novel = NovelFactory(user=user)
    ItemFactory(novel=novel)
    response = auth_client.get(reverse('item_list', kwargs={'novel_pk': novel.pk}))
    assert set(response.context.keys()) & {'part', 'parts', 'chapter', 'chapters'} == set()


# T-UI-0601.02.01
@pytest.mark.trace("T-UI-0601.02.01")
@pytest.mark.django_db
def test_item_image_displayed_on_card_when_uploaded(auth_client, user):
    novel = NovelFactory(user=user)
    item = ItemFactory(novel=novel, image=make_image_file())
    response = auth_client.get(reverse('item_list', kwargs={'novel_pk': novel.pk}))
    assert item.image.name.encode() in response.content or item.image.url.encode() in response.content


# T-UI-0601.02.02
@pytest.mark.trace("T-UI-0601.02.02")
@pytest.mark.django_db
def test_item_card_displays_no_image_when_none_uploaded(auth_client, user):
    novel = NovelFactory(user=user)
    ItemFactory(novel=novel)
    response = auth_client.get(reverse('item_list', kwargs={'novel_pk': novel.pk}))
    assert not response.context['items'][0].image


# T-FUNC-0602.01.01
@pytest.mark.trace("T-FUNC-0602.01.01")
@pytest.mark.django_db
def test_create_item_success(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('item_create', kwargs={'novel_pk': novel.pk}), {'name': 'The Silver Compass'})
    item = Item.objects.get(novel=novel, name='The Silver Compass')
    assert response.status_code == 302
    list_response = auth_client.get(reverse('item_list', kwargs={'novel_pk': novel.pk}))
    assert item in list_response.context['items']


# T-FUNC-0602.01.02
@pytest.mark.trace("T-FUNC-0602.01.02")
@pytest.mark.django_db
def test_create_item_without_name_fails(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(reverse('item_create', kwargs={'novel_pk': novel.pk}), {'name': ''})
    assert response.status_code == 200
    assert not Item.objects.filter(novel=novel).exists()
    assert 'Item name is required' in response.context['form'].errors['name']


# T-UI-0602.01.01
@pytest.mark.trace("T-UI-0602.01.01")
@pytest.mark.django_db
def test_add_item_form_presents_all_required_fields(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.get(reverse('item_create', kwargs={'novel_pk': novel.pk}))
    assert set(response.context['form'].fields.keys()) == ITEM_FORM_FIELDS


# T-FUNC-0603.01.01
@pytest.mark.trace("T-FUNC-0603.01.01")
@pytest.mark.django_db
def test_edit_item_success(auth_client, user):
    novel = NovelFactory(user=user)
    item = ItemFactory(novel=novel, name='Original Name')
    response = auth_client.post(
        reverse('item_edit', kwargs={'novel_pk': novel.pk, 'pk': item.pk}),
        {'name': 'Updated Name'},
    )
    item.refresh_from_db()
    assert response.status_code == 302
    assert item.name == 'Updated Name'


# T-FUNC-0603.01.02
@pytest.mark.trace("T-FUNC-0603.01.02")
@pytest.mark.django_db
def test_cancel_editing_item_leaves_it_unchanged(auth_client, user):
    novel = NovelFactory(user=user)
    item = ItemFactory(novel=novel, name='Original Name')
    response = auth_client.get(reverse('item_edit', kwargs={'novel_pk': novel.pk, 'pk': item.pk}))
    item.refresh_from_db()
    assert response.status_code == 200
    assert item.name == 'Original Name'


# T-UI-0603.01.01
@pytest.mark.trace("T-UI-0603.01.01")
@pytest.mark.django_db
def test_appears_in_scenes_readonly_on_edit_page(auth_client, user):
    novel = NovelFactory(user=user)
    item = ItemFactory(novel=novel)
    response = auth_client.get(
        reverse('modal_item_edit', kwargs={'novel_pk': novel.pk, 'pk': item.pk}))
    assert 'scene_occurrences' in response.context
    assert 'scene_occurrences' not in response.context['form'].fields


# T-FUNC-0602.03.01
@pytest.mark.trace("T-FUNC-0602.03.01")
@pytest.mark.django_db
def test_add_new_item_type_value(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('item_type_list', kwargs={'novel_pk': novel.pk}),
        {'action': 'add', 'name': 'Artifact'},
    )
    assert response.status_code == 302
    assert ItemType.objects.filter(novel=novel, name='Artifact').exists()


# T-FUNC-0602.03.02
@pytest.mark.trace("T-FUNC-0602.03.02")
@pytest.mark.django_db
def test_item_type_values_scoped_to_novel(auth_client, user):
    novel_a = NovelFactory(user=user)
    novel_b = NovelFactory(user=user)
    ItemTypeFactory(novel=novel_a, name='Artifact')

    response = auth_client.get(reverse('item_create', kwargs={'novel_pk': novel_b.pk}))
    type_queryset = response.context['form'].fields['type'].queryset
    assert not type_queryset.filter(name='Artifact').exists()


# T-FUNC-0602.04.01
@pytest.mark.trace("T-FUNC-0602.04.01")
@pytest.mark.django_db
def test_rename_item_type_value(auth_client, user):
    novel = NovelFactory(user=user)
    item_type = ItemTypeFactory(novel=novel, name='Old Name')
    item = ItemFactory(novel=novel, type=item_type)

    auth_client.post(
        reverse('item_type_list', kwargs={'novel_pk': novel.pk}),
        {'action': 'rename', 'category_id': item_type.pk, 'name': 'New Name'},
    )
    item_type.refresh_from_db()
    item.refresh_from_db()
    assert item_type.name == 'New Name'
    assert item.type.name == 'New Name'


# T-FUNC-0602.05.01
@pytest.mark.trace("T-FUNC-0602.05.01")
@pytest.mark.django_db
def test_delete_item_type_value(auth_client, user):
    novel = NovelFactory(user=user)
    item_type = ItemTypeFactory(novel=novel)
    type_pk = item_type.pk

    auth_client.post(
        reverse('item_type_list', kwargs={'novel_pk': novel.pk}),
        {'action': 'delete', 'category_id': type_pk},
    )
    assert not ItemType.objects.filter(pk=type_pk).exists()


# T-FUNC-0602.05.02
@pytest.mark.trace("T-FUNC-0602.05.02")
@pytest.mark.django_db
def test_deleting_type_does_not_delete_assigned_items(auth_client, user):
    novel = NovelFactory(user=user)
    item_type = ItemTypeFactory(novel=novel)
    item = ItemFactory(novel=novel, type=item_type)

    auth_client.post(
        reverse('item_type_list', kwargs={'novel_pk': novel.pk}),
        {'action': 'delete', 'category_id': item_type.pk},
    )
    item.refresh_from_db()
    assert Item.objects.filter(pk=item.pk).exists()
    assert item.type is None


# T-FUNC-0602.02.01
@pytest.mark.trace("T-FUNC-0602.02.01")
@pytest.mark.django_db
def test_upload_item_image_on_add_page(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('item_create', kwargs={'novel_pk': novel.pk}),
        {'name': 'The Silver Compass', 'image': make_image_file()},
    )
    item = Item.objects.get(novel=novel, name='The Silver Compass')
    assert response.status_code == 302
    assert item.image


# T-FUNC-0602.02.02
@pytest.mark.trace("T-FUNC-0602.02.02")
@pytest.mark.django_db
def test_upload_item_image_on_edit_page(auth_client, user):
    novel = NovelFactory(user=user)
    item = ItemFactory(novel=novel)
    assert not item.image

    response = auth_client.post(
        reverse('item_edit', kwargs={'novel_pk': novel.pk, 'pk': item.pk}),
        {'name': item.name, 'image': make_image_file()},
    )
    item.refresh_from_db()
    assert response.status_code == 302
    assert item.image


# T-FUNC-0602.02.03
@pytest.mark.trace("T-FUNC-0602.02.03")
@pytest.mark.django_db
def test_replace_existing_item_image(auth_client, user):
    novel = NovelFactory(user=user)
    item = ItemFactory(novel=novel, image=make_image_file('original.png'))
    original_name = item.image.name

    response = auth_client.post(
        reverse('item_edit', kwargs={'novel_pk': novel.pk, 'pk': item.pk}),
        {'name': item.name, 'image': make_image_file('replacement.png')},
    )
    item.refresh_from_db()
    assert response.status_code == 302
    assert item.image.name != original_name


# T-SEC-0602.01.01
@pytest.mark.trace("T-SEC-0602.01.01")
@pytest.mark.django_db
def test_png_image_accepted(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('item_create', kwargs={'novel_pk': novel.pk}),
        {'name': 'Thing', 'image': make_image_file('test.png', 'image/png', 'PNG')},
    )
    assert response.status_code == 302


# T-SEC-0602.01.02
@pytest.mark.trace("T-SEC-0602.01.02")
@pytest.mark.django_db
def test_jpg_image_accepted(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('item_create', kwargs={'novel_pk': novel.pk}),
        {'name': 'Thing', 'image': make_image_file('test.jpg', 'image/jpeg', 'JPEG')},
    )
    assert response.status_code == 302


# T-SEC-0602.01.03
@pytest.mark.trace("T-SEC-0602.01.03")
@pytest.mark.django_db
def test_jpeg_image_accepted(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('item_create', kwargs={'novel_pk': novel.pk}),
        {'name': 'Thing', 'image': make_image_file('test.jpeg', 'image/jpeg', 'JPEG')},
    )
    assert response.status_code == 302


# T-SEC-0602.01.04
@pytest.mark.trace("T-SEC-0602.01.04")
@pytest.mark.django_db
def test_unsupported_image_extension_rejected(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('item_create', kwargs={'novel_pk': novel.pk}),
        {'name': 'Thing', 'image': make_image_file('test.gif', 'image/gif', 'PNG')},
    )
    assert response.status_code == 200
    assert not Item.objects.filter(novel=novel).exists()
    assert 'Only .jpg, .jpeg, and .png images are allowed.' in response.context['form'].errors['image']


# T-FUNC-0610.01.01
@pytest.mark.trace("T-FUNC-0610.01.01")
@pytest.mark.django_db
def test_define_relationship_between_item_and_character(auth_client, user):
    novel = NovelFactory(user=user)
    item = ItemFactory(novel=novel)
    character = CharacterFactory(novel=novel)

    response = auth_client.post(
        reverse('relationship_add', kwargs={'novel_pk': novel.pk}),
        {
            'from_type': 'item', 'from_id': item.pk,
            'to_type': 'character', 'to_id': character.pk,
            'label': 'owned by', 'reverse_label': 'owns',
        },
    )
    assert response.status_code == 200
    assert Relationship.objects.filter(novel=novel, label='owned by', reverse_label='owns').exists()


# T-FUNC-0610.01.02
@pytest.mark.trace("T-FUNC-0610.01.02")
@pytest.mark.django_db
def test_define_relationship_between_two_items(auth_client, user):
    novel = NovelFactory(user=user)
    item_a = ItemFactory(novel=novel)
    item_b = ItemFactory(novel=novel)

    response = auth_client.post(
        reverse('relationship_add', kwargs={'novel_pk': novel.pk}),
        {
            'from_type': 'item', 'from_id': item_a.pk,
            'to_type': 'item', 'to_id': item_b.pk,
            'label': 'part of', 'reverse_label': 'contains',
        },
    )
    assert response.status_code == 200
    assert Relationship.objects.filter(novel=novel, label='part of', reverse_label='contains').exists()


# T-FUNC-0610.02.01
@pytest.mark.trace("T-FUNC-0610.02.01")
@pytest.mark.django_db
def test_relationship_appears_on_both_entities_with_correct_labels(auth_client, user):
    novel = NovelFactory(user=user)
    item = ItemFactory(novel=novel)
    location = LocationFactory(novel=novel)
    auth_client.post(
        reverse('relationship_add', kwargs={'novel_pk': novel.pk}),
        {
            'from_type': 'item', 'from_id': item.pk,
            'to_type': 'location', 'to_id': location.pk,
            'label': 'found in', 'reverse_label': 'contains',
        },
    )

    item_response = auth_client.get(
        reverse('modal_item_detail', kwargs={'novel_pk': novel.pk, 'pk': item.pk}))
    item_labels = [r['display_label'] for r in item_response.context['relationships']]
    assert 'found in' in item_labels

    loc_response = auth_client.get(
        reverse('modal_location_detail', kwargs={'novel_pk': novel.pk, 'pk': location.pk}))
    loc_labels = [r['display_label'] for r in loc_response.context['relationships']]
    assert 'contains' in loc_labels


# T-FUNC-0610.03.01
@pytest.mark.trace("T-FUNC-0610.03.01")
@pytest.mark.django_db
def test_edit_relationship_from_item_page(auth_client, user):
    novel = NovelFactory(user=user)
    item = ItemFactory(novel=novel)
    character = CharacterFactory(novel=novel)
    auth_client.post(
        reverse('relationship_add', kwargs={'novel_pk': novel.pk}),
        {
            'from_type': 'item', 'from_id': item.pk,
            'to_type': 'character', 'to_id': character.pk,
            'label': 'owned by', 'reverse_label': 'owns',
        },
    )
    rel = Relationship.objects.get(novel=novel)

    response = auth_client.post(
        reverse('relationship_edit', kwargs={'novel_pk': novel.pk, 'pk': rel.pk}),
        {
            'entity_type': 'item', 'entity_id': item.pk,
            'label': 'carried by', 'reverse_label': 'carries',
        },
    )
    rel.refresh_from_db()
    assert response.status_code == 200
    assert rel.label == 'carried by'
    assert rel.reverse_label == 'carries'


# T-FUNC-0610.04.01
@pytest.mark.trace("T-FUNC-0610.04.01")
@pytest.mark.django_db
def test_delete_relationship(auth_client, user):
    novel = NovelFactory(user=user)
    item = ItemFactory(novel=novel)
    character = CharacterFactory(novel=novel)
    auth_client.post(
        reverse('relationship_add', kwargs={'novel_pk': novel.pk}),
        {
            'from_type': 'item', 'from_id': item.pk,
            'to_type': 'character', 'to_id': character.pk,
            'label': 'owned by', 'reverse_label': 'owns',
        },
    )
    rel = Relationship.objects.get(novel=novel)

    response = auth_client.post(
        reverse('relationship_delete', kwargs={'novel_pk': novel.pk, 'pk': rel.pk}),
        {'entity_type': 'item', 'entity_id': item.pk},
    )
    assert response.status_code == 200
    assert not Relationship.objects.filter(pk=rel.pk).exists()
    assert Item.objects.filter(pk=item.pk).exists()
