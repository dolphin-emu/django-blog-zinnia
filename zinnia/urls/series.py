"""URLs for blog series."""
from django.urls import re_path

from zinnia.views.series import LegacySeriesRedirect, SeriesList


urlpatterns = [
    re_path(r'^series$', SeriesList.as_view(), name='series_list'),
    re_path(r'^series#series-(?P<pk>[0-9]+)$', LegacySeriesRedirect.as_view()),
]
