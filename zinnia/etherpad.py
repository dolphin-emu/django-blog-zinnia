"""Optional Etherpad configuration and pad creation."""
import logging
import uuid

import requests

from zinnia.settings import ETHERPAD_URL
from zinnia.settings import ETHERPAD_API_KEY

logger = logging.getLogger(__name__)


def create_entry_pad(sender, instance, raw=False, using=None, **kwargs):
    if raw or instance.etherpad_id:
        return
    url = ETHERPAD_URL
    api_key = ETHERPAD_API_KEY
    if not url or not api_key:
        return

    pad_id = str(uuid.uuid4())
    try:
        response = requests.post(url.rstrip('/') + '/api/1/createPad', timeout=5,
                                 data={'apikey': api_key, 'padID': pad_id,
                                       'text': instance.content})
        response.raise_for_status()
        if response.json().get('code') != 0:
            logger.warning('Etherpad rejected pad creation for entry %s', instance.pk)
            return
    except (requests.RequestException, ValueError, AttributeError):
        logger.warning('Unable to create Etherpad pad for entry %s', instance.pk)
        return

    # Avoid recursively saving the entry and firing its signals again.
    sender.objects.using(using).filter(pk=instance.pk).update(etherpad_id=pad_id)
    instance.etherpad_id = pad_id
