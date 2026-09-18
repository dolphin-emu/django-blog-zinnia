======================
Advanced Configuration
======================

.. _zinnia-sitemaps:

Sitemaps
========

.. module:: zinnia.sitemaps

One of the cool features of Django is the sitemap application, so if you
want to fill your Web site's sitemap with the entries of your blog, follow
these steps.

* Register :mod:`django.contrib.sitemaps` in the :setting:`INSTALLED_APPS` section.
* Edit your project's URLs and add this code: ::

    from django.contrib.sitemaps.views import index
    from django.contrib.sitemaps.views import sitemap

    from zinnia.sitemaps import AuthorSitemap
    from zinnia.sitemaps import CategorySitemap
    from zinnia.sitemaps import EntrySitemap
    from zinnia.sitemaps import TagSitemap

    sitemaps = {
        'tags': TagSitemap,
        'blog': EntrySitemap,
        'authors': AuthorSitemap,
        'categories': CategorySitemap
    }

    urlpatterns += [
        url(r'^sitemap.xml$',
            index,
            {'sitemaps': sitemaps}),
        url(r'^sitemap-(?P<section>.+)\.xml$',
            sitemap,
            {'sitemaps': sitemaps},
            name='django.contrib.sitemaps.views.sitemap'),
    ]

.. _zinnia-templates:

Templates for entries
=====================

In your Weblog you will always publish entries, but sometimes you want to
have a different look and feel for special entries.

You may want to publish an entry with a short content like a quote, in
which case it would be better not to provide a *continue reading* link when
rendering this entry.

To solve this problem, Zinnia allows the user to select a template to
render the entry's content and the entry's detail page.

In order to use a template without the *continue reading* link, we need to
register it under this setting in the project's configuration: ::

  ZINNIA_ENTRY_CONTENT_TEMPLATES = [
    ('zinnia/_short_entry_detail.html', 'Short entry template'),
  ]

Now we will create the ``zinnia/_short_entry_detail.html`` template with
this sample of code:

.. code-block:: html+django

  {% extends "zinnia/_entry_detail.html" %}

  {% block continue-reading %}{% endblock %}

A new template is now available in the admin interface to display the entry
without the *continue reading* link when displayed in a list.

Then if you want to have custom rendering of the detail page of the entry,
by displaying the entry fullwidth without the sidebar for example, the same
process applies. We will add this setting in the project's configuration:
::

  ZINNIA_ENTRY_DETAIL_TEMPLATES = [
      ('zinnia/fullwidth_entry_detail.html', 'Fullwidth template'),
  ]

And now we finally create the ``zinnia/fullwidth_entry_detail.html``
template with this sample of code:

.. code-block:: html+django

  {% extends "zinnia/entry_detail.html" %}

  {% block sidebar-class %}no-sidebar{% endblock %}

  {% block sidebar %}{% endblock %}

.. _zinnia-markup-languages:

Markup languages
================

If you doesn't want to write your entries in HTML, because you are
an über coder knowing more than 42 programming languages, you have the
possibility to use a custom markup language for editing the entries.

Currently **MarkDown** is supported, so if you want to use it, first set this
setting as appropriate in your project's settings. ::

  ZINNIA_MARKUP_LANGUAGE = 'markdown'

Note that the name of the language must be in lowercase.

Then install the corresponding library to your needs:

* ``markdown`` -- requires `Markdown`_ >= 2.3.1

.. _zinnia-cache:

Cache
=====

For performance considerations the Django's cache API is used when
comparing the entries between them. To isolate these operations, the
:setting:`CACHES` setting must contain a value named ``'comparison'``,
otherwise the ``'default'`` value will be used.

::

  CACHES = {
      'default': {
          'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
      },
      'comparison': {
          'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
          'LOCATION': 'comparison',
          'TIMEOUT': None,
     }
  }

.. _`Markdown`: http://pypi.python.org/pypi/Markdown
