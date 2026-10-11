"""Optional Etherpad webhook URL."""
from django.urls import re_path

from zinnia.views.etherpad import etherpad_event

urlpatterns = [
    re_path(r'^etherpad/event$', etherpad_event, name='etherpad_event'),
]
