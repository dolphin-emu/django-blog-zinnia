"""Urls for the zinnia capabilities"""
from django.urls import re_path

from zinnia.views.capabilities import HumansTxt


urlpatterns = [
    re_path(r'^humans.txt$', HumansTxt.as_view(),
        name='humans'),
]
