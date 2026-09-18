"""Signal handlers of Zinnia"""
import inspect
from functools import wraps

from django.db.models.signals import post_delete
from django.db.models.signals import post_save

from zinnia.comparison import EntryPublishedVectorBuilder
from zinnia.models.entry import Entry

ENTRY_PS_FLUSH_SIMILAR_CACHE = 'zinnia.entry.post_save.flush_similar_cache'
ENTRY_PD_FLUSH_SIMILAR_CACHE = 'zinnia.entry.post_delete.flush_similar_cache'


def disable_for_loaddata(signal_handler):
    """
    Decorator for disabling signals sent by 'post_save'
    on loaddata command.
    http://code.djangoproject.com/ticket/8399
    """
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        for fr in inspect.stack():
            if inspect.getmodulename(fr[1]) == 'loaddata':
                return  # pragma: no cover
        signal_handler(*args, **kwargs)

    return wrapper


@disable_for_loaddata
def flush_similar_cache_handler(sender, **kwargs):
    """
    Flush the cache of similar entries when an entry is saved.
    """
    entry = kwargs['instance']
    if entry.is_visible:
        EntryPublishedVectorBuilder().cache_flush()


def connect_entry_signals():
    """
    Connect all the signals on Entry model.
    """
    post_save.connect(
        flush_similar_cache_handler, sender=Entry,
        dispatch_uid=ENTRY_PS_FLUSH_SIMILAR_CACHE)
    post_delete.connect(
        flush_similar_cache_handler, sender=Entry,
        dispatch_uid=ENTRY_PD_FLUSH_SIMILAR_CACHE)


def disconnect_entry_signals():
    """
    Disconnect all the signals on Entry model.
    """
    post_save.disconnect(
        sender=Entry,
        dispatch_uid=ENTRY_PS_FLUSH_SIMILAR_CACHE)
    post_delete.disconnect(
        sender=Entry,
        dispatch_uid=ENTRY_PD_FLUSH_SIMILAR_CACHE)
