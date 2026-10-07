from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('zinnia', '0008_entry_indexes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='related',
            field=models.ManyToManyField(
                blank=True, to='zinnia.entry',
                verbose_name='related entries'),
        ),
    ]
