"""
Data migration: remap legacy Scene status values to FEAT-0229 choices.

Migration 0002 introduced Scene.status with six values that pre-date the
specification (FEAT-0229). Migration 0003 updated the field's choices list
on both Scene and Chapter to the correct eleven values, but any rows already
written with the old values remain in the database.  This migration remaps
those rows to the nearest FEAT-0229 equivalent.

Mapping applied:
  not_started  → not_started   (no change — value exists in both sets)
  in_progress  → plotting
  first_draft  → first_draft   (no change — value exists in both sets)
  needs_review → first_review
  final_draft  → final_edit
  complete     → published
"""

from django.db import migrations

REMAPPING = {
    'in_progress':  'plotting',
    'needs_review': 'first_review',
    'final_draft':  'final_edit',
    'complete':     'published',
}


def remap_scene_status_forward(apps, schema_editor):
    Scene = apps.get_model('novels', 'Scene')
    for old_value, new_value in REMAPPING.items():
        Scene.objects.filter(status=old_value).update(status=new_value)


def remap_scene_status_reverse(apps, schema_editor):
    """
    Reverse mapping — used when unapplying this migration.
    Note: 'complete' and 'published' are both non-recoverable without
    additional state, so we map back to the closest old equivalent.
    """
    Scene = apps.get_model('novels', 'Scene')
    reverse = {new: old for old, new in REMAPPING.items()}
    for new_value, old_value in reverse.items():
        Scene.objects.filter(status=new_value).update(status=old_value)


class Migration(migrations.Migration):

    dependencies = [
        ('novels', '0003_chapter_notes_chapter_status_novel_parts_enabled_and_more'),
    ]

    operations = [
        migrations.RunPython(
            remap_scene_status_forward,
            remap_scene_status_reverse,
        ),
    ]
