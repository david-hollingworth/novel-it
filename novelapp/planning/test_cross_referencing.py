"""
Backend/state tests for automatic scene cross-referencing (FEAT-0307),
converted from content/requirements/03-writing-interface.md per
data/requirements/phase-1-run-2-scope.yaml.

Covers writing-interface's remaining 4 backend_state tests: T-FUNC-0307.01.01
through T-FUNC-0307.01.04.

Lives in planning/ rather than novels/ because the scanning logic
(planning/scan.py) and the SceneEntity model it populates both live here,
even though the requirement itself is documented under 03-writing-interface.

Mechanics: scan_scene_entities() is only called from novels' scene_save_view
(the JSON save-content API), not from the regular form-based scene_edit_view
-- so these tests POST to scene_save, not scene_edit. There's no convenience
method on Character/Location/Item for "appears in scenes"; a mention is a
SceneEntity row keyed by (scene, content_type, object_id).
"""
import pytest
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

import json

from accounts.factories import UserFactory
from novels.factories import NovelFactory, ChapterFactory, SceneFactory
from novels.models import Part
from planning.factories import CharacterFactory, LocationFactory, ItemFactory
from .models import SceneEntity


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


def save_scene_content(auth_client, novel, chapter, scene, content):
    return auth_client.post(
        reverse('scene_save', kwargs={
            'novel_pk': novel.pk, 'chapter_pk': chapter.pk, 'scene_pk': scene.pk}),
        data=json.dumps({'content': content}),
        content_type='application/json',
    )


# T-FUNC-0307.01.01
@pytest.mark.trace("T-FUNC-0307.01.01")
@pytest.mark.django_db
def test_character_mention_recorded_on_scene_save(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, content='')
    character = CharacterFactory(novel=novel, fullname='Elara')

    save_scene_content(auth_client, novel, chapter, scene, 'Elara walked into the room.')

    ct = ContentType.objects.get_for_model(character)
    assert SceneEntity.objects.filter(scene=scene, content_type=ct, object_id=character.pk).exists()


# T-FUNC-0307.01.02
@pytest.mark.trace("T-FUNC-0307.01.02")
@pytest.mark.django_db
def test_location_mention_recorded_on_scene_save(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, content='')
    location = LocationFactory(novel=novel, name='The Crossroads Inn')

    save_scene_content(
        auth_client, novel, chapter, scene, 'They met at The Crossroads Inn.')

    ct = ContentType.objects.get_for_model(location)
    assert SceneEntity.objects.filter(scene=scene, content_type=ct, object_id=location.pk).exists()


# T-FUNC-0307.01.03
@pytest.mark.trace("T-FUNC-0307.01.03")
@pytest.mark.django_db
def test_item_mention_recorded_on_scene_save(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, content='')
    item = ItemFactory(novel=novel, name='the silver compass')

    save_scene_content(
        auth_client, novel, chapter, scene, 'She reached for the silver compass.')

    ct = ContentType.objects.get_for_model(item)
    assert SceneEntity.objects.filter(scene=scene, content_type=ct, object_id=item.pk).exists()


# T-FUNC-0307.01.04
@pytest.mark.trace("T-FUNC-0307.01.04")
@pytest.mark.django_db
def test_no_mention_recorded_when_name_absent(auth_client, user):
    novel = NovelFactory(user=user, parts_enabled=False)
    part = Part.objects.create(novel=novel, title='_default', order=0)
    chapter = ChapterFactory(part=part)
    scene = SceneFactory(chapter=chapter, content='')
    character = CharacterFactory(novel=novel, fullname='Marcus')

    save_scene_content(
        auth_client, novel, chapter, scene, 'Nobody relevant showed up today.')

    ct = ContentType.objects.get_for_model(character)
    assert not SceneEntity.objects.filter(scene=scene, content_type=ct, object_id=character.pk).exists()
