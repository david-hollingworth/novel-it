"""
Backend/state tests for Character CRUD, roles, image upload, and
relationships, converted from content/requirements/04-character-management.md
per data/requirements/phase-1-run-2-scope.yaml. 27 tests.

Excluded (per scope file): T-FUNC-0401.01.02 (archive), T-DATA-0410.01.01
(relationship cleanup on delete) -- archive/delete not yet implemented for
any planning entity.

Note on T-UI-0402.01.01 ("appears in scenes" read-only field): the plain
character_edit_view / character_form.html never renders this at all -- only
the modal edit flow (modal_character_edit / modal_character_form.html) does,
via the scene_occurrences context variable. Tested against the modal view
since that's where the feature actually exists.

Note on "no parent summary section" (T-UI-0401.01.01): character_list_view's
context is exactly {'novel', 'characters'} -- there's no part/chapter
breadcrumb concept for planning entities the way there is for the
Novel/Part/Chapter/Scene hierarchy, so this is tested as an absence of
those context keys rather than a template-markup check.
"""
import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from accounts.factories import UserFactory
from novels.factories import NovelFactory
from .factories import CharacterFactory, CharacterRoleFactory, LocationFactory, ItemFactory
from .models import Character, CharacterRole, Item, Relationship


CHARACTER_FORM_FIELDS = {
    'fullname', 'first_name', 'middle_name', 'last_name', 'nickname',
    'aliases', 'gender', 'age', 'role', 'physical_description', 'interview',
    'the_lie_they_believe', 'goals_and_motivations', 'fears_and_weaknesses',
    'arc_in_story', 'image', 'description', 'notes',
}


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


# T-FUNC-0401.01.01
@pytest.mark.trace("T-FUNC-0401.01.01")
@pytest.mark.django_db
def test_characters_displayed_as_cards_on_board(auth_client, user):
    novel = NovelFactory(user=user)
    c1, c2, c3 = CharacterFactory(novel=novel), CharacterFactory(novel=novel), CharacterFactory(novel=novel)
    response = auth_client.get(reverse('character_list', kwargs={'novel_pk': novel.pk}))
    assert set(response.context['characters']) == {c1, c2, c3}


# T-UI-0401.02.01
@pytest.mark.trace("T-UI-0401.02.01")
@pytest.mark.django_db
def test_character_image_displayed_on_card_when_uploaded(auth_client, user):
    novel = NovelFactory(user=user)
    character = CharacterFactory(novel=novel, image=make_image_file())
    response = auth_client.get(reverse('character_list', kwargs={'novel_pk': novel.pk}))
    assert character.image.name.encode() in response.content or character.image.url.encode() in response.content


# T-UI-0401.02.02
@pytest.mark.trace("T-UI-0401.02.02")
@pytest.mark.django_db
def test_character_card_displays_no_image_when_none_uploaded(auth_client, user):
    novel = NovelFactory(user=user)
    character = CharacterFactory(novel=novel)
    response = auth_client.get(reverse('character_list', kwargs={'novel_pk': novel.pk}))
    assert not response.context['characters'][0].image


# T-UI-0401.01.01
@pytest.mark.trace("T-UI-0401.01.01")
@pytest.mark.django_db
def test_no_parent_summary_section_on_character_list(auth_client, user):
    novel = NovelFactory(user=user)
    CharacterFactory(novel=novel)
    response = auth_client.get(reverse('character_list', kwargs={'novel_pk': novel.pk}))
    assert set(response.context.keys()) & {'part', 'parts', 'chapter', 'chapters'} == set()


# T-FUNC-0402.01.01
@pytest.mark.trace("T-FUNC-0402.01.01")
@pytest.mark.django_db
def test_edit_character_success(auth_client, user):
    novel = NovelFactory(user=user)
    character = CharacterFactory(novel=novel, fullname='Original Name')
    response = auth_client.post(
        reverse('character_edit', kwargs={'novel_pk': novel.pk, 'pk': character.pk}),
        {'fullname': 'Updated Name'},
    )
    character.refresh_from_db()
    assert response.status_code == 302
    assert character.fullname == 'Updated Name'


# T-FUNC-0402.01.02
@pytest.mark.trace("T-FUNC-0402.01.02")
@pytest.mark.django_db
def test_cancel_editing_character_leaves_it_unchanged(auth_client, user):
    novel = NovelFactory(user=user)
    character = CharacterFactory(novel=novel, fullname='Original Name')
    response = auth_client.get(
        reverse('character_edit', kwargs={'novel_pk': novel.pk, 'pk': character.pk}))
    character.refresh_from_db()
    assert response.status_code == 200
    assert character.fullname == 'Original Name'


# T-UI-0402.01.01
@pytest.mark.trace("T-UI-0402.01.01")
@pytest.mark.django_db
def test_appears_in_scenes_readonly_on_edit_page(auth_client, user):
    novel = NovelFactory(user=user)
    character = CharacterFactory(novel=novel)
    response = auth_client.get(
        reverse('modal_character_edit', kwargs={'novel_pk': novel.pk, 'pk': character.pk}))
    assert 'scene_occurrences' in response.context
    # Not a form field -- there's nothing to submit, which is what makes it read-only
    assert 'scene_occurrences' not in response.context['form'].fields


# T-FUNC-0403.01.01
@pytest.mark.trace("T-FUNC-0403.01.01")
@pytest.mark.django_db
def test_create_character_success(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('character_create', kwargs={'novel_pk': novel.pk}),
        {'fullname': 'Elara'},
    )
    character = Character.objects.get(novel=novel, fullname='Elara')
    assert response.status_code == 302
    list_response = auth_client.get(reverse('character_list', kwargs={'novel_pk': novel.pk}))
    assert character in list_response.context['characters']


# T-FUNC-0403.01.02
@pytest.mark.trace("T-FUNC-0403.01.02")
@pytest.mark.django_db
def test_create_character_without_fullname_fails(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('character_create', kwargs={'novel_pk': novel.pk}), {'fullname': ''})
    assert response.status_code == 200
    assert not Character.objects.filter(novel=novel).exists()
    assert 'Full name is required' in response.context['form'].errors['fullname']


# T-UI-0403.01.01
@pytest.mark.trace("T-UI-0403.01.01")
@pytest.mark.django_db
def test_add_character_form_presents_all_required_fields(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.get(reverse('character_create', kwargs={'novel_pk': novel.pk}))
    assert set(response.context['form'].fields.keys()) == CHARACTER_FORM_FIELDS


# T-FUNC-0403.03.01
@pytest.mark.trace("T-FUNC-0403.03.01")
@pytest.mark.django_db
def test_add_new_character_role_value(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('character_role_list', kwargs={'novel_pk': novel.pk}),
        {'action': 'add', 'name': 'Protagonist'},
    )
    assert response.status_code == 302
    assert CharacterRole.objects.filter(novel=novel, name='Protagonist').exists()


# T-FUNC-0403.03.02
@pytest.mark.trace("T-FUNC-0403.03.02")
@pytest.mark.django_db
def test_role_values_scoped_to_novel(auth_client, user):
    novel_a = NovelFactory(user=user)
    novel_b = NovelFactory(user=user)
    CharacterRoleFactory(novel=novel_a, name='Protagonist')

    response = auth_client.get(reverse('character_create', kwargs={'novel_pk': novel_b.pk}))
    role_queryset = response.context['form'].fields['role'].queryset
    assert not role_queryset.filter(name='Protagonist').exists()


# T-FUNC-0403.04.01
@pytest.mark.trace("T-FUNC-0403.04.01")
@pytest.mark.django_db
def test_rename_character_role_value(auth_client, user):
    novel = NovelFactory(user=user)
    role = CharacterRoleFactory(novel=novel, name='Old Name')
    character = CharacterFactory(novel=novel, role=role)

    auth_client.post(
        reverse('character_role_list', kwargs={'novel_pk': novel.pk}),
        {'action': 'rename', 'category_id': role.pk, 'name': 'New Name'},
    )
    role.refresh_from_db()
    character.refresh_from_db()
    assert role.name == 'New Name'
    assert character.role.name == 'New Name'


# T-FUNC-0403.05.01
@pytest.mark.trace("T-FUNC-0403.05.01")
@pytest.mark.django_db
def test_delete_character_role_value(auth_client, user):
    novel = NovelFactory(user=user)
    role = CharacterRoleFactory(novel=novel)
    role_pk = role.pk

    auth_client.post(
        reverse('character_role_list', kwargs={'novel_pk': novel.pk}),
        {'action': 'delete', 'category_id': role_pk},
    )
    assert not CharacterRole.objects.filter(pk=role_pk).exists()


# T-FUNC-0403.05.02
@pytest.mark.trace("T-FUNC-0403.05.02")
@pytest.mark.django_db
def test_deleting_role_does_not_delete_assigned_characters(auth_client, user):
    novel = NovelFactory(user=user)
    role = CharacterRoleFactory(novel=novel)
    character = CharacterFactory(novel=novel, role=role)

    auth_client.post(
        reverse('character_role_list', kwargs={'novel_pk': novel.pk}),
        {'action': 'delete', 'category_id': role.pk},
    )
    character.refresh_from_db()
    assert Character.objects.filter(pk=character.pk).exists()
    assert character.role is None


# T-FUNC-0403.02.01
@pytest.mark.trace("T-FUNC-0403.02.01")
@pytest.mark.django_db
def test_upload_character_image_on_add_page(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('character_create', kwargs={'novel_pk': novel.pk}),
        {'fullname': 'Elara', 'image': make_image_file()},
    )
    character = Character.objects.get(novel=novel, fullname='Elara')
    assert response.status_code == 302
    assert character.image


# T-FUNC-0403.02.02
@pytest.mark.trace("T-FUNC-0403.02.02")
@pytest.mark.django_db
def test_upload_character_image_on_edit_page(auth_client, user):
    novel = NovelFactory(user=user)
    character = CharacterFactory(novel=novel)
    assert not character.image

    response = auth_client.post(
        reverse('character_edit', kwargs={'novel_pk': novel.pk, 'pk': character.pk}),
        {'fullname': character.fullname, 'image': make_image_file()},
    )
    character.refresh_from_db()
    assert response.status_code == 302
    assert character.image


# T-FUNC-0403.02.03
@pytest.mark.trace("T-FUNC-0403.02.03")
@pytest.mark.django_db
def test_replace_existing_character_image(auth_client, user):
    novel = NovelFactory(user=user)
    character = CharacterFactory(novel=novel, image=make_image_file('original.png'))
    original_name = character.image.name

    response = auth_client.post(
        reverse('character_edit', kwargs={'novel_pk': novel.pk, 'pk': character.pk}),
        {'fullname': character.fullname, 'image': make_image_file('replacement.png')},
    )
    character.refresh_from_db()
    assert response.status_code == 302
    assert character.image.name != original_name


# T-SEC-0403.01.01
@pytest.mark.trace("T-SEC-0403.01.01")
@pytest.mark.django_db
def test_png_image_accepted(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('character_create', kwargs={'novel_pk': novel.pk}),
        {'fullname': 'Elara', 'image': make_image_file('test.png', 'image/png', 'PNG')},
    )
    assert response.status_code == 302


# T-SEC-0403.01.02
@pytest.mark.trace("T-SEC-0403.01.02")
@pytest.mark.django_db
def test_jpg_image_accepted(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('character_create', kwargs={'novel_pk': novel.pk}),
        {'fullname': 'Elara', 'image': make_image_file('test.jpg', 'image/jpeg', 'JPEG')},
    )
    assert response.status_code == 302


# T-SEC-0403.01.03
@pytest.mark.trace("T-SEC-0403.01.03")
@pytest.mark.django_db
def test_jpeg_image_accepted(auth_client, user):
    novel = NovelFactory(user=user)
    response = auth_client.post(
        reverse('character_create', kwargs={'novel_pk': novel.pk}),
        {'fullname': 'Elara', 'image': make_image_file('test.jpeg', 'image/jpeg', 'JPEG')},
    )
    assert response.status_code == 302


# T-SEC-0403.01.04
@pytest.mark.trace("T-SEC-0403.01.04")
@pytest.mark.django_db
def test_unsupported_image_extension_rejected(auth_client, user):
    novel = NovelFactory(user=user)
    # Genuinely valid image bytes, but with a disallowed extension/content-type
    # -- exercises the app's own extension check, not Django's PIL validation.
    response = auth_client.post(
        reverse('character_create', kwargs={'novel_pk': novel.pk}),
        {'fullname': 'Elara', 'image': make_image_file('test.gif', 'image/gif', 'PNG')},
    )
    assert response.status_code == 200
    assert not Character.objects.filter(novel=novel).exists()
    assert 'Only .jpg, .jpeg, and .png images are allowed.' in response.context['form'].errors['image']


# T-FUNC-0410.01.01
@pytest.mark.trace("T-FUNC-0410.01.01")
@pytest.mark.django_db
def test_define_relationship_between_two_characters(auth_client, user):
    novel = NovelFactory(user=user)
    char_a = CharacterFactory(novel=novel)
    char_b = CharacterFactory(novel=novel)

    response = auth_client.post(
        reverse('relationship_add', kwargs={'novel_pk': novel.pk}),
        {
            'from_type': 'character', 'from_id': char_a.pk,
            'to_type': 'character', 'to_id': char_b.pk,
            'label': 'mentor of', 'reverse_label': 'mentored by',
        },
    )
    assert response.status_code == 200
    rel = Relationship.objects.get(novel=novel)
    assert rel.label == 'mentor of'
    assert rel.reverse_label == 'mentored by'


# T-FUNC-0410.01.02
@pytest.mark.trace("T-FUNC-0410.01.02")
@pytest.mark.django_db
def test_define_relationship_between_character_and_item(auth_client, user):
    novel = NovelFactory(user=user)
    character = CharacterFactory(novel=novel)
    item = ItemFactory(novel=novel)

    response = auth_client.post(
        reverse('relationship_add', kwargs={'novel_pk': novel.pk}),
        {
            'from_type': 'character', 'from_id': character.pk,
            'to_type': 'item', 'to_id': item.pk,
            'label': 'owns', 'reverse_label': 'owned by',
        },
    )
    assert response.status_code == 200
    assert Relationship.objects.filter(novel=novel, label='owns', reverse_label='owned by').exists()


# T-FUNC-0410.02.01
@pytest.mark.trace("T-FUNC-0410.02.01")
@pytest.mark.django_db
def test_relationship_appears_on_both_entities_with_correct_labels(auth_client, user):
    novel = NovelFactory(user=user)
    character = CharacterFactory(novel=novel)
    item = ItemFactory(novel=novel)
    auth_client.post(
        reverse('relationship_add', kwargs={'novel_pk': novel.pk}),
        {
            'from_type': 'character', 'from_id': character.pk,
            'to_type': 'item', 'to_id': item.pk,
            'label': 'owns', 'reverse_label': 'owned by',
        },
    )

    char_response = auth_client.get(
        reverse('modal_character_detail', kwargs={'novel_pk': novel.pk, 'pk': character.pk}))
    char_labels = [r['display_label'] for r in char_response.context['relationships']]
    assert 'owns' in char_labels

    item_response = auth_client.get(
        reverse('modal_item_detail', kwargs={'novel_pk': novel.pk, 'pk': item.pk}))
    item_labels = [r['display_label'] for r in item_response.context['relationships']]
    assert 'owned by' in item_labels


# T-FUNC-0410.03.01
@pytest.mark.trace("T-FUNC-0410.03.01")
@pytest.mark.django_db
def test_edit_relationship_from_character_page(auth_client, user):
    novel = NovelFactory(user=user)
    character = CharacterFactory(novel=novel)
    location = LocationFactory(novel=novel)
    add_response = auth_client.post(
        reverse('relationship_add', kwargs={'novel_pk': novel.pk}),
        {
            'from_type': 'character', 'from_id': character.pk,
            'to_type': 'location', 'to_id': location.pk,
            'label': 'lives in', 'reverse_label': 'home of',
        },
    )
    rel = Relationship.objects.get(novel=novel)

    response = auth_client.post(
        reverse('relationship_edit', kwargs={'novel_pk': novel.pk, 'pk': rel.pk}),
        {
            'entity_type': 'character', 'entity_id': character.pk,
            'label': 'resides in', 'reverse_label': 'residence of',
        },
    )
    rel.refresh_from_db()
    assert response.status_code == 200
    assert rel.label == 'resides in'
    assert rel.reverse_label == 'residence of'


# T-FUNC-0410.04.01
@pytest.mark.trace("T-FUNC-0410.04.01")
@pytest.mark.django_db
def test_delete_relationship(auth_client, user):
    novel = NovelFactory(user=user)
    character = CharacterFactory(novel=novel)
    item = ItemFactory(novel=novel)
    auth_client.post(
        reverse('relationship_add', kwargs={'novel_pk': novel.pk}),
        {
            'from_type': 'character', 'from_id': character.pk,
            'to_type': 'item', 'to_id': item.pk,
            'label': 'owns', 'reverse_label': 'owned by',
        },
    )
    rel = Relationship.objects.get(novel=novel)

    response = auth_client.post(
        reverse('relationship_delete', kwargs={'novel_pk': novel.pk, 'pk': rel.pk}),
        {'entity_type': 'character', 'entity_id': character.pk},
    )
    assert response.status_code == 200
    assert not Relationship.objects.filter(pk=rel.pk).exists()
    assert Character.objects.filter(pk=character.pk).exists()
    assert Item.objects.filter(pk=item.pk).exists()
