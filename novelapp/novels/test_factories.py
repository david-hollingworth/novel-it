import pytest
from .factories import NovelFactory, PartFactory, ChapterFactory, SceneFactory


@pytest.mark.django_db
def test_scene_factory_builds_full_chain():
    """NovelFactory/PartFactory/ChapterFactory/SceneFactory should chain
    together into a valid Novel -> Part -> Chapter -> Scene hierarchy."""
    scene = SceneFactory()
    assert scene.pk is not None
    assert scene.chapter.pk is not None
    assert scene.chapter.part.pk is not None
    assert scene.chapter.part.novel.pk is not None
    assert scene.chapter.novel == scene.chapter.part.novel


@pytest.mark.django_db
def test_part_and_chapter_order_sequence_avoids_collisions():
    """Multiple Parts/Chapters against the same parent shouldn't collide
    with the (novel, order) / (part, order) unique_together constraints."""
    novel = NovelFactory()
    part1 = PartFactory(novel=novel)
    part2 = PartFactory(novel=novel)
    assert part1.order != part2.order

    chapter1 = ChapterFactory(part=part1)
    chapter2 = ChapterFactory(part=part1)
    assert chapter1.order != chapter2.order
