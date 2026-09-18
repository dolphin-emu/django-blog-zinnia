"""Urls for the Zinnia feeds"""
from django.conf.urls import url

from zinnia.feeds import AuthorEntries
from zinnia.feeds import CategoryEntries
from zinnia.feeds import LastEntries
from zinnia.feeds import SearchEntries
from zinnia.feeds import TagEntries
from zinnia.urls import _


urlpatterns = [
    url(r'^$',
        LastEntries(),
        name='entry_feed'),
    url(_(r'^search/$'),
        SearchEntries(),
        name='entry_search_feed'),
    url(_(r'^tags/(?P<tag>[^/]+)/$'),
        TagEntries(),
        name='tag_feed'),
    url(_(r'^authors/(?P<username>[.+-@\w]+)/$'),
        AuthorEntries(),
        name='author_feed'),
    url(_(r'^categories/(?P<path>[-\/\w]+)/$'),
        CategoryEntries(),
        name='category_feed'),
]
