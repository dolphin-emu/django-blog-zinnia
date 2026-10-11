"""Use the same singular and plural label for blog series."""
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('zinnia', '0010_blogseries_entry_fields'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='blogseries',
            options={
                'verbose_name': 'Blog series',
                'verbose_name_plural': 'Blog series',
            },
        ),
    ]
