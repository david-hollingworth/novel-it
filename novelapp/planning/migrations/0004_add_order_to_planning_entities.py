from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Add display order field to Character, Location, and Item models.
    Supports drag-and-drop reordering on planning entity list pages (issue #98).
    All existing records default to order=0, preserving the previous
    alphabetical ordering as the tiebreaker in Meta.ordering.
    """

    dependencies = [
        ('planning', '0003_sceneentity'),
    ]

    operations = [
        migrations.AddField(
            model_name='character',
            name='order',
            field=models.IntegerField(default=0, help_text='Display order within the novel'),
        ),
        migrations.AddField(
            model_name='location',
            name='order',
            field=models.IntegerField(default=0, help_text='Display order within the novel'),
        ),
        migrations.AddField(
            model_name='item',
            name='order',
            field=models.IntegerField(default=0, help_text='Display order within the novel'),
        ),
    ]
