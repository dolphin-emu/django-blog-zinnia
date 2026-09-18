"""Urls for the zinnia capabilities"""
from django.conf.urls import url

from zinnia.views.capabilities import HumansTxt
from zinnia.views.capabilities import OpenSearchXml


urlpatterns = [
    url(r'^humans.txt$', HumansTxt.as_view(),
        name='humans'),
    url(r'^opensearch.xml$', OpenSearchXml.as_view(),
        name='opensearch'),
]
