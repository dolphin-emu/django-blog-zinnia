"""Apps for Zinnia"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ZinniaConfig(AppConfig):
    """
    Config for Zinnia application.
    """
    default_auto_field = 'django.db.models.AutoField'
    name = 'zinnia'
    label = 'zinnia'
    verbose_name = _('Weblog')

    def ready(self):
        from django.db.models.signals import post_save
        from zinnia.etherpad import create_entry_pad
        from zinnia.models import Entry

        post_save.connect(create_entry_pad, sender=Entry,
                          dispatch_uid='zinnia.entry.create_etherpad')
