import factory
from accounts.factories import UserFactory
from .models import Novel, Part, Chapter, Scene


class NovelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Novel

    user = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: f'Test Novel {n}')


class PartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Part

    novel = factory.SubFactory(NovelFactory)
    title = factory.Sequence(lambda n: f'Part {n}')
    # Sequence is global across all Part instances, not per-novel, so this
    # never collides with the novel+order unique_together constraint even
    # when several Parts are created against the same novel.
    order = factory.Sequence(lambda n: n)


class ChapterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Chapter

    # Chapter has no direct FK to Novel -- it hangs off Part. Use
    # ChapterFactory(part=PartFactory(novel=my_novel)) to place a chapter
    # under a specific novel.
    part = factory.SubFactory(PartFactory)
    title = factory.Sequence(lambda n: f'Chapter {n}')
    order = factory.Sequence(lambda n: n)


class SceneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Scene

    chapter = factory.SubFactory(ChapterFactory)
    title = factory.Sequence(lambda n: f'Scene {n}')
    order = factory.Sequence(lambda n: n)
    content = factory.Faker('paragraph', nb_sentences=5)
