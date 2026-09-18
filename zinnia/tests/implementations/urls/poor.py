"""Poor test urls for the zinnia project"""
from django.contrib import admin
from django.urls import include
from django.urls import re_path

from zinnia.views.entries import EntryDetail

admin.autodiscover()

blog_urls = ([
    re_path(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        EntryDetail.as_view(),
        name='entry_detail')],
    'zinnia'
)

urlpatterns = [
    re_path(r'^', include(blog_urls)),
    re_path(r'^admin/', admin.site.urls),
]
