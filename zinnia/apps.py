"""Apps for Zinnia"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ZinniaConfig(AppConfig):
    """
    Config for Zinnia application.
    """
    name = 'zinnia'
    label = 'zinnia'
    verbose_name = _('Weblog')

    def ready(self):
        from zinnia.signals import connect_entry_signals
        # Connect the signals
        connect_entry_signals()
