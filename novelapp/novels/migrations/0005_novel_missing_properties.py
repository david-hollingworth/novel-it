from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Add missing Novel properties to align with FEAT-0201:
      - subtitle
      - author_name
      - target_word_count
      - status
      - pitch

    The existing 'description' field maps to Synopsis, and 'premise' maps to
    Notes/Premise — both already present, no schema change needed for those.
    """

    dependencies = [
        ('novels', '0004_fix_scene_status_values'),
    ]

    operations = [
        migrations.AddField(
            model_name='novel',
            name='subtitle',
            field=models.CharField(blank=True, default='', help_text='Subtitle of the novel', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='novel',
            name='author_name',
            field=models.CharField(blank=True, default='', help_text='Author name', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='novel',
            name='target_word_count',
            field=models.IntegerField(default=0, help_text='Target word count goal'),
        ),
        migrations.AddField(
            model_name='novel',
            name='status',
            field=models.CharField(
                choices=[
                    ('not_started', 'Not Started'),
                    ('plotting', 'Plotting'),
                    ('first_draft', 'First Draft'),
                    ('first_review', 'First Review'),
                    ('second_draft', 'Second Draft'),
                    ('second_review', 'Second Review'),
                    ('structural_edit', 'Structural Edit'),
                    ('final_edit', 'Final Edit'),
                    ('beta_reading', 'Beta Reading'),
                    ('publishing', 'Publishing'),
                    ('published', 'Published'),
                ],
                default='not_started',
                help_text='Current status of the novel',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='novel',
            name='pitch',
            field=models.TextField(blank=True, default='', help_text='One-paragraph pitch for the novel'),
            preserve_default=False,
        ),
    ]
