"""
Set of" markup" function to transform plain text into HTML for Zinnia.
Code originally provided by django.contrib.markups
"""
import warnings

from django.utils.encoding import force_str
from django.utils.html import linebreaks

from zinnia.settings import MARKDOWN_EXTENSIONS
from zinnia.settings import MARKUP_LANGUAGE


def markdown(value, extensions=MARKDOWN_EXTENSIONS):
    """
    Markdown processing with optionally using various extensions
    that python-markdown supports.
    `extensions` is an iterable of either markdown.Extension instances
    or extension paths.
    """
    try:
        import markdown
    except ImportError:
        warnings.warn("The Python markdown library isn't installed.",
                      RuntimeWarning)
        return value

    return markdown.markdown(force_str(value), extensions=extensions)


def html_format(value):
    """
    Returns the value formatted in HTML,
    depends on MARKUP_LANGUAGE setting.
    """
    if not value:
        return ''
    elif MARKUP_LANGUAGE == 'markdown':
        return markdown(value)
    elif '</p>' not in value:
        return linebreaks(value)
    return value
