"""
Management command to create default character roles, location types, and item types for a novel.

Usage:
    python manage.py create_default_planning_types <novel_id>
    python manage.py create_default_planning_types --all  # For all novels
"""

from django.core.management.base import BaseCommand, CommandError
from novels.models import Novel
from planning.models import CharacterRole, LocationType, ItemType


class Command(BaseCommand):
    help = 'Create default character roles, location types, and item types for a novel'

    def add_arguments(self, parser):
        parser.add_argument(
            'novel_id',
            nargs='?',
            type=int,
            help='ID of the novel to create defaults for'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Create defaults for all novels that don\'t have any types defined'
        )

    def handle(self, *args, **options):
        if options['all']:
            self.create_defaults_for_all_novels()
        elif options['novel_id']:
            self.create_defaults_for_novel(options['novel_id'])
        else:
            raise CommandError('Please provide a novel_id or use --all flag')

    def create_defaults_for_all_novels(self):
        """Create defaults for all novels that don't have types defined."""
        novels = Novel.objects.all()
        count = 0
        
        for novel in novels:
            # Check if novel already has types defined
            has_roles = novel.character_roles.exists()
            has_location_types = novel.location_types.exists()
            has_item_types = novel.item_types.exists()
            
            if not (has_roles or has_location_types or has_item_types):
                self.create_defaults(novel)
                count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created default types for {count} novel(s)'
            )
        )

    def create_defaults_for_novel(self, novel_id):
        """Create defaults for a specific novel."""
        try:
            novel = Novel.objects.get(pk=novel_id)
        except Novel.DoesNotExist:
            raise CommandError(f'Novel with ID {novel_id} does not exist')
        
        self.create_defaults(novel)
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created default types for novel "{novel.title}"'
            )
        )

    def create_defaults(self, novel):
        """Create default character roles, location types, and item types."""
        
        # Default Character Roles
        default_roles = [
            ('Protagonist', 0),
            ('Antagonist', 1),
            ('Supporting', 2),
            ('Minor', 3),
            ('Love Interest', 4),
            ('Mentor', 5),
            ('Sidekick', 6),
            ('Villain', 7),
            ('Hero', 8),
            ('Anti-Hero', 9),
        ]
        
        for name, order in default_roles:
            CharacterRole.objects.get_or_create(
                novel=novel,
                name=name,
                defaults={'order': order}
            )
        
        # Default Location Types
        default_location_types = [
            ('City', 0),
            ('Town', 1),
            ('Village', 2),
            ('Building', 3),
            ('Room', 4),
            ('House', 5),
            ('Country', 6),
            ('Region', 7),
            ('Forest', 8),
            ('Mountain', 9),
            ('Ocean', 10),
            ('Desert', 11),
            ('Cave', 12),
            ('Island', 13),
            ('Castle', 14),
            ('Temple', 15),
            ('Spaceship', 16),
            ('Planet', 17),
            ('Fictional World', 18),
        ]
        
        for name, order in default_location_types:
            LocationType.objects.get_or_create(
                novel=novel,
                name=name,
                defaults={'order': order}
            )
        
        # Default Item Types
        default_item_types = [
            ('Weapon', 0),
            ('Armor', 1),
            ('Tool', 2),
            ('Artifact', 3),
            ('Magic Item', 4),
            ('Technology', 5),
            ('Vehicle', 6),
            ('Document', 7),
            ('Book', 8),
            ('Jewelry', 9),
            ('Clothing', 10),
            ('Food', 11),
            ('Treasure', 12),
            ('Key Item', 13),
            ('Quest Item', 14),
        ]
        
        for name, order in default_item_types:
            ItemType.objects.get_or_create(
                novel=novel,
                name=name,
                defaults={'order': order}
            )
        
        self.stdout.write(f'  - Created {len(default_roles)} character roles')
        self.stdout.write(f'  - Created {len(default_location_types)} location types')
        self.stdout.write(f'  - Created {len(default_item_types)} item types')
