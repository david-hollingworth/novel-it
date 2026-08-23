import factory
from novels.factories import NovelFactory
from .models import (
    CharacterRole, LocationType, ItemType, WorldBuildingType,
    Character, Location, Item, WorldBuilding,
)


# --- User-definable choice models ---
#
# These are scoped to a novel (unique_together = ['novel', 'name']). If a
# Character/Location/Item/WorldBuilding needs a role/type from the SAME
# novel it belongs to, pass novel explicitly to both, e.g.:
#
#   novel = NovelFactory()
#   role = CharacterRoleFactory(novel=novel)
#   character = CharacterFactory(novel=novel, role=role)
#
# Left unspecified, each SubFactory below creates its own independent
# novel, which is fine when the test doesn't care about role/type scoping.

class CharacterRoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CharacterRole

    novel = factory.SubFactory(NovelFactory)
    name = factory.Sequence(lambda n: f'Role {n}')


class LocationTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LocationType

    novel = factory.SubFactory(NovelFactory)
    name = factory.Sequence(lambda n: f'Location Type {n}')


class ItemTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ItemType

    novel = factory.SubFactory(NovelFactory)
    name = factory.Sequence(lambda n: f'Item Type {n}')


class WorldBuildingTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WorldBuildingType

    novel = factory.SubFactory(NovelFactory)
    name = factory.Sequence(lambda n: f'World Building Type {n}')


# --- Main planning models ---

class CharacterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Character

    novel = factory.SubFactory(NovelFactory)
    fullname = factory.Faker('name')


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    novel = factory.SubFactory(NovelFactory)
    name = factory.Faker('city')


class ItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Item

    novel = factory.SubFactory(NovelFactory)
    name = factory.Sequence(lambda n: f'Item {n}')


class WorldBuildingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WorldBuilding

    novel = factory.SubFactory(NovelFactory)
    name = factory.Sequence(lambda n: f'World Building Item {n}')
