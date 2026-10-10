"""Entry model for Zinnia"""
from django.db import models
from django.utils.html import linebreaks

from zinnia.managers import DRAFT
from zinnia.markups import markdown
from zinnia.models_bases import load_model_class
from zinnia.settings import ENTRY_BASE_MODEL, MARKUP_LANGUAGE


def render_to_html(content):
    if MARKUP_LANGUAGE == 'markdown':
        return markdown(content)
    return linebreaks(content)


class Entry(load_model_class(ENTRY_BASE_MODEL)):
    """
    Represents a blog entry. Adds an optional `series` field to the default
    Zinnia model.
    """
    within_series = models.ForeignKey('zinnia.BlogSeries', on_delete=models.SET_NULL, null=True, blank=True, related_name='entries')
    etherpad_id = models.CharField(max_length=256, null=True, blank=True)

    @property
    def use_collaborative_editing(self):
        return self.etherpad_id and self.draft

    @property
    def draft(self):
        return self.status == DRAFT

    # The default Zinnia implementation of this does stupid content sniffing,
    # assuming that if something contains </p> it is raw HTML. That's not true,
    # since Markdown can contain HTML.
    @property
    def html_content(self):
        """
        Returns the "content" field formatted in HTML.
        """
        return render_to_html(self.content)

    # While Zinnia provides html_preview for HTML rendered excerpts,
    # that property doesn't allow custom article excerpts, so we need to roll
    # our own rendered excerpt property.
    @property
    def html_excerpt(self):
        """
        Returns the "excerpt" field formatted in HTML.
        """
        return render_to_html(self.excerpt)

    @property
    def real_image(self):
        """Priorities the entry image, then the series image, if any."""
        if self.image:
            return self.image

        if self.within_series is not None:
            # May be None!
            return self.within_series.image

    @property
    def series_index(self):
        if self.within_series is None:
            return 1

        return (self.within_series.entries
            .filter(publication_date__lt=self.publication_date)
            .exclude(pk=self.pk)
            .count()) + 1

    def relative_entry_in_series(self, offset):
        if self.within_series is None:
            return None

        return self.within_series.nth_entry(self.series_index + offset)

    @property
    def next_entry_in_series(self):
        return self.relative_entry_in_series(1)

    @property
    def previous_entry_in_series(self):
        return self.relative_entry_in_series(-1)
