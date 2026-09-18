from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zinnia', '0006_remove_entry_comments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entry',
            name='pingback_count',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='pingback_enabled',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='trackback_count',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='trackback_enabled',
        ),
    ]
