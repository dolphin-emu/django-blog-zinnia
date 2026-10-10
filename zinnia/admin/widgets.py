"""Widgets for Zinnia admin"""
from itertools import chain

from django.contrib.admin import widgets
from django.contrib.staticfiles.storage import staticfiles_storage
from django.forms import Media, Widget
from django.utils.encoding import force_str

from zinnia.settings import ETHERPAD_URL


class MPTTFilteredSelectMultiple(widgets.FilteredSelectMultiple):
    """
    MPTT version of FilteredSelectMultiple.
    """
    option_inherits_attrs = True

    def __init__(self, verbose_name, is_stacked=False, attrs=None, choices=()):
        """
        Initializes the widget directly not stacked.
        """
        super().__init__(
            verbose_name, is_stacked, attrs, choices)

    def optgroups(self, name, value, attrs=None):
        """Return a list of optgroups for this widget."""
        groups = []
        has_selected = False
        if attrs is None:
            attrs = {}

        for index, (option_value, option_label, sort_fields) in enumerate(
                chain(self.choices)):

            # Set tree attributes
            attrs['data-tree-id'] = sort_fields[0]
            attrs['data-left-value'] = sort_fields[1]

            subgroup = []
            subindex = None
            choices = [(option_value, option_label)]
            groups.append((None, subgroup, index))

            for subvalue, sublabel in choices:
                selected = (
                    force_str(subvalue) in value and
                    (has_selected is False or self.allow_multiple_selected)
                )
                if selected is True and has_selected is False:
                    has_selected = True
                subgroup.append(self.create_option(
                    name, subvalue, sublabel, selected, index,
                    subindex=subindex, attrs=attrs,
                ))

        return groups

    @property
    def media(self):
        """
        MPTTFilteredSelectMultiple's Media.
        """
        js = ['admin/js/core.js',
              'zinnia/admin/mptt/js/mptt_m2m_selectbox.js',
              'admin/js/SelectFilter2.js']
        return Media(js=[staticfiles_storage.url(path) for path in js])


class MiniTextarea(widgets.AdminTextareaWidget):
    """
    Vertically shorter version of the admin textarea widget.
    """
    rows = 2

    def __init__(self, attrs=None):
        super().__init__(
            {'rows': self.rows})


class EtherpadWidget(Widget):
    """Embedded editor for an entry's collaborative draft."""
    template_name = 'zinnia/admin/etherpad_widget.html'

    def __init__(self, pad_id, attrs=None):
        super().__init__(attrs)
        self.pad_id = pad_id

    def get_context(self, name, value, attrs):
        from urllib.parse import quote
        context = super().get_context(name, value, attrs)
        context['pad_url'] = '%s/p/%s' % (
            ETHERPAD_URL.rstrip('/'), quote(str(self.pad_id), safe=''))
        return context
