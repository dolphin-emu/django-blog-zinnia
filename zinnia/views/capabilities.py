"""Views for Zinnia capabilities"""
from django.contrib.sites.models import Site
from django.views.generic.base import TemplateView

from zinnia.settings import COPYRIGHT
from zinnia.settings import FEEDS_FORMAT
from zinnia.settings import PROTOCOL


class CapabilityView(TemplateView):
    """
    Base view for the weblog capabilities.
    """

    def get_context_data(self, **kwargs):
        """
        Populate the context of the template
        with technical informations for building urls.
        """
        context = super().get_context_data(**kwargs)
        context.update({'protocol': PROTOCOL,
                        'copyright': COPYRIGHT,
                        'feeds_format': FEEDS_FORMAT,
                        'site': Site.objects.get_current()})
        return context


class HumansTxt(CapabilityView):
    """
    http://humanstxt.org/
    """
    content_type = 'text/plain'
    template_name = 'zinnia/humans.txt'


class OpenSearchXml(CapabilityView):
    """
    http://www.opensearch.org/
    """
    content_type = 'application/opensearchdescription+xml'
    template_name = 'zinnia/opensearch.xml'
