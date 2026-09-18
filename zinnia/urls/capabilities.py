"""Urls for the zinnia capabilities"""
from django.urls import re_path

from zinnia.views.capabilities import HumansTxt
from zinnia.views.capabilities import OpenSearchXml


urlpatterns = [
    re_path(r'^humans.txt$', HumansTxt.as_view(),
        name='humans'),
    re_path(r'^opensearch.xml$', OpenSearchXml.as_view(),
        name='opensearch'),
]
