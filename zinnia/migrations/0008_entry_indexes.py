from django.db import migrations
from django.db import models


def ensure_entry_indexes(apps, schema_editor):
    entry = apps.get_model('zinnia', 'Entry')
    with schema_editor.connection.cursor() as cursor:
        constraints = schema_editor.connection.introspection.get_constraints(
            cursor, entry._meta.db_table)

    indexes = (
        (('slug', 'publication_date'), 'zinnia_entry_slug_pub_idx'),
        (('status', 'publication_date', 'start_publication',
          'end_publication'), 'zinnia_entry_status_pub_idx'),
    )
    for fields, name in indexes:
        if name in constraints:
            continue
        columns = [entry._meta.get_field(field).column for field in fields]
        existing = [
            index_name for index_name, details in constraints.items()
            if details['index'] and not details['unique']
            and list(details['columns']) == columns
        ]
        new_index = models.Index(fields=fields, name=name)
        if len(existing) == 1:
            old_index = models.Index(fields=fields, name=existing[0])
            schema_editor.rename_index(entry, old_index, new_index)
        elif not existing:
            schema_editor.add_index(entry, new_index)
        else:
            raise ValueError('Multiple indexes found for %s' % name)


class Migration(migrations.Migration):

    dependencies = [
        ('zinnia', '0007_remove_entry_linkbacks'),
    ]

    operations = [
        migrations.RunPython(ensure_entry_indexes, migrations.RunPython.noop),
    ]
