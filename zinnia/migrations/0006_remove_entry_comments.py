from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zinnia', '0005_category_mptt_update'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entry',
            name='comment_count',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='comment_enabled',
        ),
    ]
