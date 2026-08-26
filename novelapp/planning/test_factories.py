import pytest
from novels.factories import NovelFactory
from .factories import CharacterRoleFactory, CharacterFactory, LocationFactory, ItemFactory, WorldBuildingFactory


@pytest.mark.django_db
def test_planning_factories_build_independently():
    assert CharacterFactory().pk is not None
    assert LocationFactory().pk is not None
    assert ItemFactory().pk is not None
    assert WorldBuildingFactory().pk is not None


@pytest.mark.django_db
def test_character_with_role_in_same_novel():
    """Role and Character need the same novel passed explicitly -- this
    confirms that pattern actually works end-to-end."""
    novel = NovelFactory()
    role = CharacterRoleFactory(novel=novel)
    character = CharacterFactory(novel=novel, role=role)
    assert character.role == role
    assert character.novel == role.novel
