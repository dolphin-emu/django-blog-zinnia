"""Urls for the Zinnia feeds"""
from django.urls import re_path

from zinnia.feeds import AuthorEntries
from zinnia.feeds import CategoryEntries
from zinnia.feeds import LastEntries
from zinnia.feeds import SeriesFeed
from zinnia.feeds import TagEntries
from zinnia.urls import _


urlpatterns = [
    re_path(r'^series/(?P<pk>[0-9]+)$', SeriesFeed(), name='series_feed'),
    re_path(r'^$',
        LastEntries(),
        name='entry_feed'),
    re_path(_(r'^tags/(?P<tag>[^/]+)/$'),
        TagEntries(),
        name='tag_feed'),
    re_path(_(r'^authors/(?P<username>[.+-@\w]+)/$'),
        AuthorEntries(),
        name='author_feed'),
    re_path(_(r'^categories/(?P<path>[-\/\w]+)/$'),
        CategoryEntries(),
        name='category_feed'),
]
