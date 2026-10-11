"""Own dolweb's series and entry fields without replacing existing data."""
import django.db.models.deletion
from django.db import migrations, models


def ensure_tables_and_fields(apps, schema_editor):
    connection = schema_editor.connection
    series = apps.get_model('zinnia', 'BlogSeries')
    if series._meta.db_table not in connection.introspection.table_names():
        schema_editor.create_model(series)

    entry = apps.get_model('zinnia', 'Entry')
    with connection.cursor() as cursor:
        columns = {
            column.name for column in
            connection.introspection.get_table_description(
                cursor, entry._meta.db_table)
        }
    # An older dolweb database can already have these custom fields without a
    # corresponding Zinnia migration. Only add columns that are missing.
    for name in ('etherpad_id', 'within_series'):
        field = entry._meta.get_field(name)
        if field.column not in columns:
            schema_editor.add_field(entry, field)


class Migration(migrations.Migration):
    dependencies = [
        ('zinnia', '0009_alter_entry_related'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='BlogSeries',
                    fields=[
                        ('id', models.AutoField(
                            auto_created=True, primary_key=True,
                            serialize=False, verbose_name='ID')),
                        ('name', models.CharField(
                            db_index=True, max_length=255)),
                        ('visible', models.BooleanField(default=True)),
                        ('image', models.ImageField(
                            blank=True, help_text='Used for illustration.',
                            upload_to='uploads/zinnia', verbose_name='image')),
                    ],
                    options={'db_table': 'blog_blogseries'},
                ),
                migrations.AddField(
                    model_name='entry',
                    name='etherpad_id',
                    field=models.CharField(
                        blank=True, max_length=256, null=True),
                ),
                migrations.AddField(
                    model_name='entry',
                    name='within_series',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='entries', to='zinnia.blogseries'),
                ),
            ],
        ),
        migrations.RunPython(ensure_tables_and_fields),
    ]
