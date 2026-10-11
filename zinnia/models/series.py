"""Date-ordered series of blog entries."""
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from zinnia.managers import entries_published
from zinnia.settings import UPLOAD_TO


class BlogSeries(models.Model):
    """Represents a date-ordered sequence of blog entries."""

    name = models.CharField(max_length=255, db_index=True)
    visible = models.BooleanField(default=True)
    image = models.ImageField(
        _('image'), blank=True, upload_to=UPLOAD_TO,
        help_text=_('Used for illustration.'))

    def get_absolute_url(self):
        return '%s#series-%s' % (reverse('zinnia:series_list'), self.pk)

    @property
    def published_entries(self):
        """Public entries in reading order, restricted to the current site."""
        return entries_published(self.entries).order_by('publication_date')

    @property
    def entries_reversed(self):
        return self.entries.order_by('publication_date')

    def nth_entry(self, nth, allow_hidden=False):
        """Returns the 1-indexed nth article in series."""
        if nth < 1:
            return None

        qs = self.entries.all() if allow_hidden else self.published_entries

        try:
            return qs.order_by('publication_date')[nth - 1]
        except IndexError:
            return None

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<BlogSeries "%s" (%d entries)>' % (
            self.name, self.entries.count())

    class Meta:
        # Keep existing dolweb installations on the same table.
        db_table = "blog_blogseries"
        verbose_name = _("Blog series")
        verbose_name_plural = _("Blog series")
