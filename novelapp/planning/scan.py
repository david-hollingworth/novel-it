"""
Entity scanning for scene content.

On each scene save, scan the text for known character/location/item names
(including nicknames, first names, and aliases) and upsert SceneEntity records.
"""
import re
from django.contrib.contenttypes.models import ContentType
from .models import Character, Location, Item, SceneEntity


def _name_variants(entity):
    """
    Return a list of non-empty name strings to search for, for a given entity.
    Longer variants are returned first so that e.g. 'Harry The Badger' matches
    before 'Harry' when both exist.
    """
    variants = set()

    if isinstance(entity, Character):
        for field in (entity.fullname, entity.nickname, entity.first_name, entity.last_name):
            if field and field.strip():
                variants.add(field.strip())
        # aliases is a comma-separated string
        if entity.aliases:
            for alias in entity.aliases.split(','):
                alias = alias.strip()
                if alias:
                    variants.add(alias)
    else:
        # Location and Item only have .name
        if entity.name and entity.name.strip():
            variants.add(entity.name.strip())

    # Sort longest first to prefer more specific matches
    return sorted(variants, key=len, reverse=True)


def _count_mentions(content, variants):
    """
    Return the total number of case-insensitive whole-word occurrences of any
    variant in content.  Counts each variant independently (not de-duplicated),
    but stops after the first variant that matches — we don't want to double-count
    'Harry The Badger' and 'Harry' in the same passage.
    """
    content_lower = content.lower()
    for variant in variants:
        pattern = r'\b' + re.escape(variant.lower()) + r'\b'
        matches = re.findall(pattern, content_lower)
        if matches:
            return len(matches)
    return 0


def scan_scene_entities(scene):
    """
    Scan scene.content for all known entities in the novel.
    Upserts SceneEntity records; removes stale ones.
    Called from novels.views.scene_save_view after saving content.
    """
    novel = scene.chapter.novel
    content = scene.content or ''

    # Collect all entities to check
    characters = list(novel.characters.filter(archived=False))
    locations = list(novel.locations.filter(archived=False))
    items = list(novel.items.filter(archived=False))

    ct_char = ContentType.objects.get_for_model(Character)
    ct_loc = ContentType.objects.get_for_model(Location)
    ct_item = ContentType.objects.get_for_model(Item)

    # Build (content_type, object_id, mention_count) for everything found
    found = []
    for entity, ct in (
        [(c, ct_char) for c in characters] +
        [(l, ct_loc) for l in locations] +
        [(i, ct_item) for i in items]
    ):
        variants = _name_variants(entity)
        count = _count_mentions(content, variants)
        if count > 0:
            found.append((ct, entity.pk, count))

    # Upsert found entities
    found_keys = set()
    for ct, obj_id, count in found:
        key = (ct.pk, obj_id)
        found_keys.add(key)
        SceneEntity.objects.update_or_create(
            scene=scene,
            content_type=ct,
            object_id=obj_id,
            defaults={'mention_count': count}
        )

    # Remove stale records (entity no longer mentioned)
    for se in SceneEntity.objects.filter(scene=scene):
        if (se.content_type_id, se.object_id) not in found_keys:
            se.delete()
