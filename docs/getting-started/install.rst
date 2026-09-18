============
Installation
============

.. module:: zinnia

.. _dependencies:

Dependencies
============

Make sure to install these packages prior to installation :

* `Python`_ >= 3.8
* `Django`_ >= 3.2.25, < 3.3
* `Pillow`_ >= 10.4.0
* `django-mptt`_ >= 0.14.0
* `django-tagging`_ >= 0.5.0
* `beautifulsoup4`_ >= 4.15.0
* `mots-vides`_ >= 2015.5.11
* `pyparsing`_ >= 3.1.4
* `pytz`_ >= 2026.3.post1
* `regex`_ >= 2024.11.6

Note that all the needed dependencies will be resolved if you install
Zinnia with :program:`pip` or :program:`easy_install`, excepting Django.

.. _getting-the-code:

Getting the code
================

.. highlight:: console

For the latest stable version of Zinnia use :program:`easy_install`: ::

  $ easy_install django-blog-zinnia

or use :program:`pip`: ::

  $ pip install django-blog-zinnia

You could also retrieve the last sources from
https://github.com/Fantomas42/django-blog-zinnia. Clone the repository
using :program:`git` and run the installation script: ::

  $ git clone git://github.com/Fantomas42/django-blog-zinnia.git
  $ cd django-blog-zinnia
  $ python setup.py install

or more easily via :program:`pip`: ::

  $ pip install -e git://github.com/Fantomas42/django-blog-zinnia.git#egg=django-blog-zinnia

.. _applications:

Applications
============

.. highlight:: python

Assuming that you have an already existing Django project, register
:mod:`zinnia`, and these following applications in the
:setting:`INSTALLED_APPS` section of your project's settings. ::

  INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'mptt',
    'tagging',
    'zinnia',
  )

.. _template-context-processors:

Template Context Processors
===========================

Add these following
:setting:`template context processors<TEMPLATE_CONTEXT_PROCESSORS>` if not
already present. ::

  TEMPLATES = [
    {
      'BACKEND': 'django.template.backends.django.DjangoTemplates',
      'APP_DIRS': True,
      'OPTIONS': {
        'context_processors': [
          'django.contrib.auth.context_processors.auth',
          'django.template.context_processors.i18n',
          'django.template.context_processors.request',
          'django.contrib.messages.context_processors.messages',
          'zinnia.context_processors.version',  # Optional
        ]
      }
    }
  ]

.. _urls:

URLs
====

Add at least these following lines to your project's urls.py in order to
display the Weblog. ::

  from django.urls import include
  from django.urls import re_path

  re_path(r'^weblog/', include('zinnia.urls')),

Remember to enable the :mod:`~django.contrib.admin` site in the urls.py of
your project if you haven't done it yet for having the edition capabilities.

Note that the default Zinnia URLset :mod:`zinnia.urls` is calibrated for
convenient usage, but you can customize your Weblog URLs as you
want. Here's a custom implementation of the URLs provided by Zinnia: ::

  blog_urls = ([
      re_path(r'^', include('zinnia.urls.capabilities')),
      re_path(r'^search/', include('zinnia.urls.search')),
      re_path(r'^sitemap/', include('zinnia.urls.sitemap')),
      re_path(r'^blog/tags/', include('zinnia.urls.tags')),
      re_path(r'^blog/feeds/', include('zinnia.urls.feeds')),
      re_path(r'^blog/random/', include('zinnia.urls.random')),
      re_path(r'^blog/authors/', include('zinnia.urls.authors')),
      re_path(r'^blog/categories/', include('zinnia.urls.categories')),
      re_path(r'^blog/', include('zinnia.urls.entries')),
      re_path(r'^blog/', include('zinnia.urls.archives')),
      re_path(r'^blog/', include('zinnia.urls.shortlink')),
      re_path(r'^blog/', include('zinnia.urls.quick_entry'))
  ], 'zinnia')

  re_path(r'^', include(blog_urls))

.. _sites:

Sites
=====

Define the value of :setting:`SITE_ID` if not already done. ::

  SITE_ID = 1

.. _emails:

Emails
======

Be sure that the sending of emails is correctly configured, otherwise the
moderation system will not work. Please refer to
https://docs.djangoproject.com/en/dev/topics/email/ for more information
about sending emails.

.. _static-files:

Static Files
============

Since the version 1.3 of Django, Zinnia uses the
:mod:`~django.contrib.staticfiles` application to serve the static files
needed. Please refer to
https://docs.djangoproject.com/en/dev/howto/static-files/ for more
information about serving static files.

.. _syncing-database:

Syncing the database
====================

.. highlight:: console

Now that you have everything set up, simply run the following in your
project directory to sync the models with the database. ::

  $ python manage.py migrate

.. _`Python`: http://www.python.org/
.. _`Django`: https://www.djangoproject.com/
.. _`Pillow`: http://python-imaging.github.io/Pillow/
.. _`django-mptt`: https://github.com/django-mptt/django-mptt/
.. _`django-tagging`: https://code.google.com/p/django-tagging/
.. _`mots-vides`: https://github.com/Fantomas42/mots-vides
.. _`regex`: https://pypi.python.org/pypi/regex
.. _`beautifulsoup4`: http://www.crummy.com/software/BeautifulSoup/
.. _`pytz`: http://pytz.sourceforge.net/
.. _`pyparsing`: http://pyparsing.wikispaces.com/
