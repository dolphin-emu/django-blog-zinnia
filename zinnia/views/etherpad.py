"""Signed content updates from Etherpad."""
import hashlib
import hmac
import json

from django.http import Http404, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from zinnia.managers import PUBLISHED
from zinnia.settings import ETHERPAD_URL
from zinnia.settings import ETHERPAD_HMAC_KEY
from zinnia.models import Entry


@csrf_exempt
def etherpad_event(request):
    key = ETHERPAD_HMAC_KEY
    if request.method != 'POST' or not ETHERPAD_URL or not key:
        raise Http404
    if b' ' not in request.body:
        return HttpResponse('Invalid format', status=400)

    signature, content = request.body.split(b' ', 1)
    expected = hmac.new(key.encode('utf-8'), content, hashlib.sha256).hexdigest().encode('ascii')
    if not hmac.compare_digest(expected, signature):
        return HttpResponse('Invalid signature', status=403)
    try:
        events = json.loads(content)
    except (ValueError, UnicodeDecodeError):
        return HttpResponse('Invalid format', status=400)
    if not isinstance(events, list):
        return HttpResponse('Invalid format', status=400)

    last_updates = {}
    for event in events:
        if not isinstance(event, dict):
            return HttpResponse('Invalid format', status=400)
        if event.get('type') != 'pad_update':
            continue
        pad_id, text = event.get('id'), event.get('text')
        if not isinstance(pad_id, str) or not pad_id or not isinstance(text, str):
            return HttpResponse('Invalid format', status=400)
        last_updates[pad_id] = text

    for pad_id, text in last_updates.items():
        # Check status in the UPDATE too, so publication racing a webhook wins.
        Entry.objects.filter(etherpad_id=pad_id).exclude(status=PUBLISHED).update(
            content=text, last_update=timezone.now())
    return HttpResponse('OK')
