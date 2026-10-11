"""Preview mixins for Zinnia views"""
from django.http import Http404
from django.utils.translation import gettext as _

from zinnia.settings import PUBLIC_PREVIEWS


class EntryPreviewMixin:
    """
    Mixin implementing the preview of Entries.
    """

    def get_object(self, queryset=None):
        """
        Allow public previews, or restrict them to authors and permitted users.
        """
        obj = super().get_object(queryset)
        if PUBLIC_PREVIEWS or obj.is_visible:
            return obj
        if (self.request.user.has_perm('zinnia.can_view_all') or
                self.request.user.pk in [
                author.pk for author in obj.authors.all()]):
            return obj
        raise Http404(_('No entry found matching the query'))
