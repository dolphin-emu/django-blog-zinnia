"""Series work with Zinnia's own URLs and templates, without Dolweb."""
from datetime import timedelta

from django.contrib.sites.models import Site
from django.template import Context, Template
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from zinnia.feeds import SeriesFeed
from zinnia.managers import DRAFT, PUBLISHED
from zinnia.models import BlogSeries, Entry


@override_settings(ROOT_URLCONF='zinnia.tests.implementations.urls.default')
class SeriesTestCase(TestCase):
    def setUp(self):
        self.site = Site.objects.get_current()
        self.series = BlogSeries.objects.create(name='Public series')
        self.hidden = BlogSeries.objects.create(name='Hidden series', visible=False)
        now = timezone.now()
        self.first = self.create_entry('First article', now - timedelta(days=2))
        self.draft = self.create_entry('Draft article', now - timedelta(days=1), status=DRAFT)
        self.last = self.create_entry('Latest article', now)
        self.scheduled = self.create_entry(
            'Scheduled article', now + timedelta(days=1),
            start_publication=now + timedelta(days=1))
        self.expired = self.create_entry(
            'Expired article', now - timedelta(days=3),
            end_publication=now - timedelta(days=1))
        self.off_site = self.create_entry('Other site article', now)
        self.off_site.sites.clear()

    def create_entry(self, title, publication_date, **kwargs):
        kwargs.setdefault('status', PUBLISHED)

        entry = Entry.objects.create(
            title=title, slug=title.lower().replace(' ', '-'),
            publication_date=publication_date, within_series=self.series,
            **kwargs)
        entry.sites.add(self.site)

        return entry

    def test_urls_and_fragment(self):
        self.assertEqual(reverse('zinnia:series_list'), '/series')
        self.assertEqual(self.series.get_absolute_url(), '/series#series-%s' % self.series.pk)
        self.assertEqual(reverse('zinnia:series_feed', args=[self.series.pk]),
                         '/feeds/series/%s' % self.series.pk)

    def test_legacy_series_link(self):
        response = self.client.get(f'/series%23series-{self.series.pk}')
        self.assertRedirects(response, self.series.get_absolute_url(), status_code=301)

    def test_admin_series_field(self):
        from django.contrib import admin
        from django.contrib.auth import get_user_model
        from django.test import RequestFactory
        from zinnia.admin.entry import EntryAdmin

        entry_admin = EntryAdmin(Entry, admin.site)
        request = RequestFactory().get('/')
        request.user = get_user_model()(is_superuser=True, is_staff=True)
        self.assertIn('within_series', entry_admin.get_form(request).base_fields)

    def test_public_index(self):
        response = self.client.get(reverse('zinnia:series_list'))
        self.assertContains(response, 'Public series')
        self.assertContains(response, 'First article')
        self.assertContains(response, 'Latest article')

        for text in ('Hidden series', 'Draft article', 'Scheduled article',
                     'Expired article', 'Other site article'):
            self.assertNotContains(response, text)

        content = response.content.decode()

        self.assertLess(content.index('First article'), content.index('Latest article'))
        self.assertContains(response, 'id="series-%s"' % self.series.pk)

    def test_feed(self):
        feed = SeriesFeed()

        self.assertEqual(list(feed.items(self.series)), [self.last, self.first])

        feed.limit = 1

        self.assertEqual(list(feed.items(self.series)), [self.last])
        self.assertEqual(feed.link(self.series), self.series.get_absolute_url())

        response = self.client.get(reverse('zinnia:series_feed', args=[self.series.pk]))

        self.assertContains(response, 'Latest article')
        self.assertNotContains(response, 'Draft article')
        self.assertEqual(self.client.get(reverse('zinnia:series_feed', args=[self.hidden.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse('zinnia:series_feed', args=[999999])).status_code, 404)

    def test_recent_series_tag(self):
        latest = BlogSeries.objects.create(name='Latest series')
        template = Template('{% load zinnia %}{% get_recent_blog_series 1 %}')
        content = template.render(Context())

        self.assertIn(latest.get_absolute_url(), content)
        self.assertNotIn('Public series', content)
        self.assertNotIn('Hidden series', content)

    def test_navigation(self):
        self.assertEqual(self.last.series_index, 2)
        self.assertEqual(self.first.next_entry_in_series, self.last)
        self.assertEqual(self.last.previous_entry_in_series, self.first)
        self.assertIsNone(self.last.next_entry_in_series)

        template = Template('{% include "zinnia/tags/entry_series.html" %}')
        content = template.render(Context({'object': self.first}))

        self.assertIn(self.series.get_absolute_url(), content)
        self.assertIn(self.last.get_absolute_url(), content)
        self.assertNotIn(self.scheduled.get_absolute_url(), content)
