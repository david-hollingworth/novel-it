from django.core.management.base import BaseCommand
from novels.models import Scene
from planning.scan import _name_variants, _count_mentions, scan_scene_entities
from planning.models import SceneEntity


class Command(BaseCommand):
    help = 'Debug entity scanning for a scene'

    def add_arguments(self, parser):
        parser.add_argument('scene_pk', type=int)

    def handle(self, *args, **options):
        scene = Scene.objects.get(pk=options['scene_pk'])
        novel = scene.chapter.novel
        content = scene.content or ''

        self.stdout.write(f'\nScene: {scene}')
        self.stdout.write(f'Content: {repr(content[:200])}')

        self.stdout.write(f'\n--- Characters ---')
        for c in novel.characters.filter(archived=False):
            variants = _name_variants(c)
            count = _count_mentions(content, variants)
            self.stdout.write(f'  {c.fullname!r}: variants={variants}, count={count}')

        self.stdout.write(f'\n--- Locations ---')
        for l in novel.locations.filter(archived=False):
            variants = _name_variants(l)
            count = _count_mentions(content, variants)
            self.stdout.write(f'  {l.name!r}: variants={variants}, count={count}')

        self.stdout.write(f'\n--- Items ---')
        for i in novel.items.filter(archived=False):
            variants = _name_variants(i)
            count = _count_mentions(content, variants)
            self.stdout.write(f'  {i.name!r}: variants={variants}, count={count}')

        self.stdout.write(f'\n--- Running scan ---')
        scan_scene_entities(scene)

        self.stdout.write(f'\n--- SceneEntity records after scan ---')
        for se in SceneEntity.objects.filter(scene=scene):
            self.stdout.write(f'  {se}')
        if not SceneEntity.objects.filter(scene=scene).exists():
            self.stdout.write('  (none)')
