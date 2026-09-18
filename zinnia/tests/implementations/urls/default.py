"""Test urls for the zinnia project"""
from django.contrib import admin
from django.urls import include
from django.urls import re_path

from zinnia.views.channels import EntryChannel

admin.autodiscover()

urlpatterns = [
    re_path(r'^', include('zinnia.urls')),
    re_path(r'^channel-test/$', EntryChannel.as_view(query='test')),
    re_path(r'^admin/', admin.site.urls),
]
