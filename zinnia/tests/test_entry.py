"""Test cases for Zinnia's Entry"""
from datetime import timedelta

from django.contrib.sites.models import Site
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import activate
from django.utils.translation import deactivate

from zinnia import markups
from zinnia import url_shortener as shortener_settings
from zinnia.managers import PUBLISHED
from zinnia.models.entry import Entry
from zinnia.models_bases import entry
from zinnia.signals import disconnect_entry_signals
from zinnia.tests.utils import datetime
from zinnia.tests.utils import skip_if_lib_not_available
from zinnia.url_shortener.backends.default import base36


class EntryTestCase(TestCase):

    def setUp(self):
        disconnect_entry_signals()
        params = {'title': 'My entry',
                  'content': 'My content',
                  'slug': 'my-entry'}
        self.entry = Entry.objects.create(**params)

    def test_str(self):
        activate('en')
        self.assertEqual(str(self.entry), 'My entry: draft')
        deactivate()

    def test_word_count(self):
        self.assertEqual(self.entry.word_count, 2)

    def test_is_actual(self):
        self.assertTrue(self.entry.is_actual)
        self.entry.start_publication = timezone.now() + timedelta(days=1)
        self.assertFalse(self.entry.is_actual)
        self.entry.start_publication = timezone.now()
        self.assertTrue(self.entry.is_actual)
        self.entry.end_publication = datetime(2000, 3, 15)
        self.assertFalse(self.entry.is_actual)

    def test_is_visible(self):
        self.assertFalse(self.entry.is_visible)
        self.entry.status = PUBLISHED
        self.assertTrue(self.entry.is_visible)
        self.entry.start_publication = timezone.now() + timedelta(days=1)
        self.assertFalse(self.entry.is_visible)

    def test_short_url(self):
        original_shortener = shortener_settings.URL_SHORTENER_BACKEND
        shortener_settings.URL_SHORTENER_BACKEND = 'zinnia.url_shortener.'\
                                                   'backends.default'
        self.assertEqual(self.entry.short_url,
                         'http://example.com' +
                         reverse('zinnia:entry_shortlink',
                                 args=[base36(self.entry.pk)]))
        shortener_settings.URL_SHORTENER_BACKEND = original_shortener

    def test_previous_entry(self):
        site = Site.objects.get_current()
        with self.assertNumQueries(0):
            # entry.previous_entry does not works until entry
            # is published, so no query should be performed
            self.assertFalse(self.entry.previous_entry)
        self.entry.status = PUBLISHED
        self.entry.save()
        self.entry.sites.add(site)
        del self.entry.previous_next  # Invalidate the cached property
        with self.assertNumQueries(1):
            self.assertFalse(self.entry.previous_entry)
            # Reload to check the cache
            self.assertFalse(self.entry.previous_entry)
        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'slug': 'my-second-entry',
                  'publication_date': datetime(2000, 1, 1),
                  'status': PUBLISHED}
        self.second_entry = Entry.objects.create(**params)
        self.second_entry.sites.add(site)
        del self.entry.previous_next  # Invalidate the cached property
        with self.assertNumQueries(1):
            self.assertEqual(self.entry.previous_entry, self.second_entry)
            # Reload to check the cache
            self.assertEqual(self.entry.previous_entry, self.second_entry)
        params = {'title': 'My third entry',
                  'content': 'My third content',
                  'slug': 'my-third-entry',
                  'publication_date': datetime(2001, 1, 1),
                  'status': PUBLISHED}
        self.third_entry = Entry.objects.create(**params)
        self.third_entry.sites.add(site)
        del self.entry.previous_next  # Invalidate the cached property
        self.assertEqual(self.entry.previous_entry, self.third_entry)
        self.assertEqual(self.third_entry.previous_entry, self.second_entry)
        self.assertFalse(self.second_entry.previous_entry)

    def test_next_entry(self):
        site = Site.objects.get_current()
        with self.assertNumQueries(0):
            # entry.next_entry does not works until entry
            # is published, so no query should be performed
            self.assertFalse(self.entry.previous_entry)
        self.entry.status = PUBLISHED
        self.entry.save()
        self.entry.sites.add(site)
        del self.entry.previous_next  # Invalidate the cached property
        with self.assertNumQueries(1):
            self.assertFalse(self.entry.next_entry)
            # Reload to check the cache
            self.assertFalse(self.entry.next_entry)
        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'slug': 'my-second-entry',
                  'publication_date': datetime(2100, 1, 1),
                  'status': PUBLISHED}
        self.second_entry = Entry.objects.create(**params)
        self.second_entry.sites.add(site)
        del self.entry.previous_next  # Invalidate the cached property
        with self.assertNumQueries(1):
            self.assertEqual(self.entry.next_entry, self.second_entry)
            # Reload to check the cache
            self.assertEqual(self.entry.next_entry, self.second_entry)
        params = {'title': 'My third entry',
                  'content': 'My third content',
                  'slug': 'my-third-entry',
                  'publication_date': datetime(2050, 1, 1),
                  'status': PUBLISHED}
        self.third_entry = Entry.objects.create(**params)
        self.third_entry.sites.add(site)
        del self.entry.previous_next  # Invalidate the cached property
        self.assertEqual(self.entry.next_entry, self.third_entry)
        self.assertEqual(self.third_entry.next_entry, self.second_entry)
        self.assertFalse(self.second_entry.next_entry)

    def test_previous_next_entry_in_one_query(self):
        site = Site.objects.get_current()
        self.entry.status = PUBLISHED
        self.entry.save()
        self.entry.sites.add(site)
        with self.assertNumQueries(1):
            self.assertFalse(self.entry.previous_entry)
            self.assertFalse(self.entry.next_entry)
            # Reload to check the cache
            self.assertFalse(self.entry.previous_entry)
            self.assertFalse(self.entry.next_entry)
        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'slug': 'my-second-entry',
                  'publication_date': datetime(2001, 1, 1),
                  'status': PUBLISHED}
        self.second_entry = Entry.objects.create(**params)
        self.second_entry.sites.add(site)
        params = {'title': 'My third entry',
                  'content': 'My third content',
                  'slug': 'my-third-entry',
                  'publication_date': datetime(2050, 1, 1),
                  'status': PUBLISHED}
        self.third_entry = Entry.objects.create(**params)
        self.third_entry.sites.add(site)
        del self.entry.previous_next  # Invalidate the cached property
        with self.assertNumQueries(1):
            self.assertEqual(self.entry.previous_entry, self.second_entry)
            self.assertEqual(self.entry.next_entry, self.third_entry)
            # Reload to check the cache
            self.assertEqual(self.entry.previous_entry, self.second_entry)
            self.assertEqual(self.entry.next_entry, self.third_entry)

    def test_related_published(self):
        site = Site.objects.get_current()
        self.assertFalse(self.entry.related_published)
        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'slug': 'my-second-entry',
                  'status': PUBLISHED}
        self.second_entry = Entry.objects.create(**params)
        self.second_entry.related.add(self.entry)
        self.assertEqual(len(self.entry.related_published), 0)

        self.second_entry.sites.add(site)
        self.assertEqual(len(self.entry.related_published), 1)
        self.assertEqual(len(self.second_entry.related_published), 0)

        self.entry.status = PUBLISHED
        self.entry.save()
        self.entry.sites.add(site)
        self.assertEqual(len(self.entry.related_published), 1)
        self.assertEqual(len(self.second_entry.related_published), 1)

    def test_tags_list(self):
        self.assertEqual(self.entry.tags_list, [])
        self.entry.tags = 'tag-1, tag-2'
        self.assertEqual(self.entry.tags_list, ['tag-1', 'tag-2'])

    def test_image_upload_to_dispatcher(self):
        path = entry.image_upload_to_dispatcher(self.entry, 'image.gif')
        self.assertTrue(path.endswith('image.gif'))

        class EntryCustomImageUploadTo(Entry):
            def image_upload_to(self, filename):
                return 'custom.png'

            class Meta:
                proxy = True

        custom_entry = EntryCustomImageUploadTo()
        self.assertEqual(
            entry.image_upload_to_dispatcher(custom_entry, 'image.gif'),
            'custom.png')

    def test_image_upload_to(self):
        path = self.entry.image_upload_to('Desktop wallpaper.jpeg')
        path_split = path.split('/')
        self.assertEqual(path_split[-1], 'desktop-wallpaper.jpeg')
        for i in range(1, 4):
            self.assertTrue(path_split[-1 - i].isdigit())

    def test_save_last_update(self):
        last_update = self.entry.last_update
        self.entry.save()
        self.assertNotEqual(
            last_update,
            self.entry.last_update)

    def test_save_excerpt(self):
        self.assertEqual(self.entry.excerpt, '')
        self.entry.status = PUBLISHED
        self.entry.save()
        self.assertEqual(self.entry.excerpt, 'My content')
        self.entry.content = 'My changed content'
        self.entry.save()
        self.assertEqual(self.entry.excerpt, 'My content')
        self.entry.excerpt = ''
        content = '<p>%s</p>' % ' '.join(['word-%s' % i for i in range(75)])
        self.entry.content = content
        self.entry.save()
        self.assertTrue(' '.join(['word-%s' % i for i in range(50)])
                        in self.entry.excerpt)

    def test_html_lead(self):
        self.assertEqual(self.entry.html_lead, '')
        self.entry.lead = 'Lead paragraph'
        self.assertEqual(self.entry.html_lead,
                         '<p>Lead paragraph</p>')


class EntryHtmlContentTestCase(TestCase):

    def setUp(self):
        params = {'title': 'My entry',
                  'content': 'My content',
                  'slug': 'my-entry'}
        self.entry = Entry(**params)
        self.original_rendering = markups.MARKUP_LANGUAGE

    def tearDown(self):
        markups.MARKUP_LANGUAGE = self.original_rendering

    def test_html_content_default(self):
        markups.MARKUP_LANGUAGE = None
        self.assertEqual(self.entry.html_content, '<p>My content</p>')

        self.entry.content = 'Hello world !\n' \
                             ' this is my content'
        self.assertHTMLEqual(
            self.entry.html_content,
            '<p>Hello world !<br /> this is my content</p>'
        )
        self.entry.content = ''
        self.assertEqual(self.entry.html_content, '')

    @skip_if_lib_not_available('markdown')
    def test_html_content_markdown(self):
        markups.MARKUP_LANGUAGE = 'markdown'
        self.entry.content = 'Hello world !\n\n' \
                             'this is my content :\n\n' \
                             '* Item 1\n* Item 2'
        html_content = self.entry.html_content
        self.assertHTMLEqual(
            html_content,
            '<p>Hello world !</p>\n'
            '<p>this is my content :</p>'
            '\n<ul>\n<li>Item 1</li>\n'
            '<li>Item 2</li>\n</ul>'
        )

    @skip_if_lib_not_available('markdown')
    def test_markdown_with_inline_html(self):
        markups.MARKUP_LANGUAGE = 'markdown'
        self.entry.content = ('Hello *World* !\n\n'
                              '<p>This is an inline HTML paragraph</p>')
        html_content = self.entry.html_content
        self.assertHTMLEqual(
            html_content,
            '<p>Hello <em>World</em> !</p>\n'
            '<p>This is an inline HTML paragraph</p>'
        )

    def test_html_preview(self):
        markups.MARKUP_LANGUAGE = None
        preview = self.entry.html_preview
        self.assertEqual(str(preview), '<p>My content</p>')
        self.assertEqual(preview.has_more, False)
        self.entry.lead = 'Lead paragraph'
        preview = self.entry.html_preview
        self.assertEqual(str(preview), '<p>Lead paragraph</p>')
        self.assertEqual(preview.has_more, True)


class EntryHtmlLeadTestCase(TestCase):

    def setUp(self):
        params = {'title': 'My entry',
                  'lead': 'My lead',
                  'slug': 'my-entry'}
        self.entry = Entry(**params)
        self.original_rendering = markups.MARKUP_LANGUAGE

    def tearDown(self):
        markups.MARKUP_LANGUAGE = self.original_rendering

    def test_html_lead_default(self):
        markups.MARKUP_LANGUAGE = None
        self.assertEqual(self.entry.html_lead, '<p>My lead</p>')

        self.entry.lead = 'Hello world !\n' \
                          ' this is my lead'
        self.assertHTMLEqual(self.entry.html_lead,
                             '<p>Hello world !<br /> this is my lead</p>')
        self.entry.lead = ''
        self.assertEqual(self.entry.html_lead, '')

    @skip_if_lib_not_available('markdown')
    def test_html_lead_markdown(self):
        markups.MARKUP_LANGUAGE = 'markdown'
        self.entry.lead = 'Hello world !\n\n' \
                          'this is my lead :\n\n' \
                          '* Item 1\n* Item 2'
        html_lead = self.entry.html_lead
        self.assertHTMLEqual(
            html_lead,
            '<p>Hello world !</p>\n'
            '<p>this is my lead :</p>'
            '\n<ul>\n<li>Item 1</li>\n'
            '<li>Item 2</li>\n</ul>'
        )

    @skip_if_lib_not_available('markdown')
    def test_markdown_with_inline_html(self):
        markups.MARKUP_LANGUAGE = 'markdown'
        self.entry.lead = ('Hello *World* !\n\n'
                           '<p>This is an inline HTML paragraph</p>')
        html_lead = self.entry.html_lead
        self.assertHTMLEqual(
            html_lead,
            '<p>Hello <em>World</em> !</p>\n'
            '<p>This is an inline HTML paragraph</p>'
        )


class EntryAbsoluteUrlTestCase(TestCase):

    def check_get_absolute_url(self, publication_date, url_expected):
        params = {'title': 'My entry',
                  'content': 'My content',
                  'slug': 'my-entry',
                  'publication_date': publication_date}
        e = Entry.objects.create(**params)
        self.assertTrue(url_expected in e.get_absolute_url())

    @override_settings(USE_TZ=False)
    def test_get_absolute_url_no_timezone(self):
        self.check_get_absolute_url(datetime(2013, 1, 1, 12, 0),
                                    '/2013/01/01/my-entry/')
        self.check_get_absolute_url(datetime(2013, 1, 1, 23, 0),
                                    '/2013/01/01/my-entry/')

    @override_settings(USE_TZ=True, TIME_ZONE='Europe/Paris')
    def test_get_absolute_url_with_timezone(self):
        self.check_get_absolute_url(datetime(2013, 1, 1, 12, 0),
                                    '/2013/01/01/my-entry/')
        self.check_get_absolute_url(datetime(2013, 1, 1, 23, 0),
                                    '/2013/01/02/my-entry/')
