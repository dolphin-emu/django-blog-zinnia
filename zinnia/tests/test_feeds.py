"""Test cases for Zinnia's feeds"""
from urllib.parse import urljoin

from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.encoding import smart_str
from django.utils.feedgenerator import Atom1Feed
from django.utils.feedgenerator import DefaultFeed
from django.utils.translation import activate
from django.utils.translation import deactivate

from tagging.models import Tag

from zinnia.feeds import AuthorEntries
from zinnia.feeds import CategoryEntries
from zinnia.feeds import EntryFeed
from zinnia.feeds import LastEntries
from zinnia.feeds import SearchEntries
from zinnia.feeds import TagEntries
from zinnia.feeds import ZinniaFeed
from zinnia.managers import PUBLISHED
from zinnia.models.author import Author
from zinnia.models.category import Category
from zinnia.models.entry import Entry
from zinnia.signals import disconnect_entry_signals
from zinnia.tests.utils import datetime
from zinnia.tests.utils import skip_if_custom_user


@skip_if_custom_user
@override_settings(
    ROOT_URLCONF='zinnia.tests.implementations.urls.default'
)
class FeedsTestCase(TestCase):
    """Test cases for the Feed classes provided"""

    def setUp(self):
        disconnect_entry_signals()
        activate('en')
        self.site = Site.objects.get_current()
        self.author = Author.objects.create(username='admin',
                                            first_name='Root',
                                            last_name='Bloody',
                                            email='admin@example.com')
        self.category = Category.objects.create(title='Tests', slug='tests')

    def tearDown(self):
        deactivate()

    def create_published_entry(self):
        params = {'title': 'My test entry',
                  'content': 'My test content with image '
                  '<img src="/image.jpg" />',
                  'slug': 'my-test-entry',
                  'tags': 'tests',
                  'publication_date': datetime(2010, 1, 1, 12),
                  'status': PUBLISHED}
        entry = Entry.objects.create(**params)
        entry.sites.add(self.site)
        entry.categories.add(self.category)
        entry.authors.add(self.author)
        return entry

    def test_entry_feed(self):
        entry = self.create_published_entry()
        feed = EntryFeed()
        self.assertEqual(feed.item_pubdate(entry), entry.publication_date)
        self.assertEqual(feed.item_updateddate(entry), entry.last_update)
        self.assertEqual(feed.item_categories(entry), [self.category.title])
        self.assertEqual(feed.item_author_name(entry),
                         self.author.__str__())
        self.assertEqual(feed.item_author_email(entry), self.author.email)
        self.assertEqual(
            feed.item_author_link(entry),
            'http://example.com/authors/%s/' % self.author.username)
        # Test a NoReverseMatch for item_author_link
        self.author.username = '[]'
        self.author.save()
        feed.item_author_name(entry)
        self.assertEqual(feed.item_author_link(entry), 'http://example.com')

    def test_entry_feed_enclosure(self):
        entry = self.create_published_entry()
        feed = EntryFeed()
        self.assertEqual(
            feed.item_enclosure_url(entry), 'http://example.com/image.jpg')
        self.assertEqual(feed.item_enclosure_length(entry), '100000')
        self.assertEqual(feed.item_enclosure_mime_type(entry), 'image/jpeg')
        entry.content = 'My test content with image <img src="image.jpg" />'
        entry.save()
        self.assertEqual(
            feed.item_enclosure_url(entry), 'http://example.com/image.jpg')
        self.assertEqual(feed.item_enclosure_length(entry), '100000')
        self.assertEqual(feed.item_enclosure_mime_type(entry), 'image/jpeg')
        entry.content = 'My test content with image ' \
                        '<img src="http://test.com/image.jpg" />'
        entry.save()
        self.assertEqual(
            feed.item_enclosure_url(entry), 'http://test.com/image.jpg')
        self.assertEqual(feed.item_enclosure_length(entry), '100000')
        self.assertEqual(feed.item_enclosure_mime_type(entry), 'image/jpeg')
        path = default_storage.save('enclosure.png', ContentFile('Content'))
        entry.image = path
        entry.save()
        self.assertEqual(feed.item_enclosure_url(entry),
                         urljoin('http://example.com', entry.image.url))
        self.assertEqual(feed.item_enclosure_length(entry), '7')
        self.assertEqual(feed.item_enclosure_mime_type(entry), 'image/png')
        default_storage.delete(path)
        entry.image = 'invalid_image_without_extension'
        entry.save()
        self.assertEqual(feed.item_enclosure_url(entry),
                         urljoin('http://example.com', entry.image.url))
        self.assertEqual(feed.item_enclosure_length(entry), '100000')
        self.assertEqual(feed.item_enclosure_mime_type(entry), 'image/jpeg')

    def test_entry_feed_enclosure_replace_https_in_rss(self):
        entry = self.create_published_entry()
        feed = EntryFeed()
        entry.content = 'My test content with image in https ' \
                        '<img src="https://test.com/image.jpg" />'
        entry.save()
        self.assertEqual(
            feed.item_enclosure_url(entry), 'http://test.com/image.jpg')
        feed.protocol = 'https'
        entry.content = 'My test content with image <img src="image.jpg" />'
        entry.save()
        self.assertEqual(
            feed.item_enclosure_url(entry), 'http://example.com/image.jpg')
        path = default_storage.save('enclosure.png', ContentFile('Content'))
        entry.image = path
        entry.save()
        self.assertEqual(feed.item_enclosure_url(entry),
                         urljoin('http://example.com', entry.image.url))
        original_feed_format = LastEntries.feed_format
        LastEntries.feed_format = 'atom'
        feed = LastEntries()
        feed.protocol = 'https'
        self.assertEqual(feed.item_enclosure_url(entry),
                         urljoin('https://example.com', entry.image.url))
        LastEntries.feed_format = original_feed_format
        default_storage.delete(path)

    def test_entry_feed_enclosure_without_image(self):
        entry = self.create_published_entry()
        feed = EntryFeed()
        entry.content = 'My test content without image '
        entry.save()
        self.assertEqual(
            feed.item_enclosure_url(entry), None)

    def test_entry_feed_enclosure_issue_134(self):
        entry = self.create_published_entry()
        feed = EntryFeed()
        entry.content = 'My test content with image <img xsrc="image.jpg" />'
        entry.save()
        self.assertEqual(
            feed.item_enclosure_url(entry), None)

    def test_last_entries(self):
        self.create_published_entry()
        feed = LastEntries()
        self.assertEqual(feed.link(), '/')
        self.assertEqual(len(feed.items()), 1)
        self.assertEqual(feed.get_title(None), 'Last entries')
        self.assertEqual(
            feed.description(),
            'The last entries on the site example.com')

    def test_category_entries(self):
        self.create_published_entry()
        feed = CategoryEntries()
        self.assertEqual(feed.get_object('request', '/tests/'), self.category)
        self.assertEqual(len(feed.items(self.category)), 1)
        self.assertEqual(feed.link(self.category), '/categories/tests/')
        self.assertEqual(
            feed.get_title(self.category),
            'Entries for the category %s' % self.category.title)
        self.assertEqual(
            feed.description(self.category),
            'The last entries categorized under %s' % self.category.title)
        self.category.description = 'Category description'
        self.assertEqual(feed.description(self.category),
                         'Category description')

    def test_category_title_non_ascii(self):
        self.create_published_entry()
        self.category.title = smart_str('Catégorie')
        self.category.save()
        feed = CategoryEntries()
        self.assertEqual(feed.get_title(self.category),
                         'Entries for the category %s' % self.category.title)
        self.assertEqual(
            feed.description(self.category),
            'The last entries categorized under %s' % self.category.title)

    def test_author_entries(self):
        self.create_published_entry()
        feed = AuthorEntries()
        self.assertEqual(feed.get_object('request', 'admin'), self.author)
        self.assertEqual(len(feed.items(self.author)), 1)
        self.assertEqual(feed.link(self.author), '/authors/admin/')
        self.assertEqual(feed.get_title(self.author),
                         'Entries for the author %s' %
                         self.author.__str__())
        self.assertEqual(feed.description(self.author),
                         'The last entries by %s' %
                         self.author.__str__())

    def test_author_title_non_ascii(self):
        self.author.first_name = smart_str('Léon')
        self.author.last_name = 'Bloom'
        self.author.save()
        self.create_published_entry()
        feed = AuthorEntries()
        self.assertEqual(feed.get_title(self.author),
                         smart_str('Entries for the author %s' %
                                   self.author.__str__()))
        self.assertEqual(feed.description(self.author),
                         smart_str('The last entries by %s' %
                                   self.author.__str__()))

    def test_tag_entries(self):
        self.create_published_entry()
        feed = TagEntries()
        tag = Tag(name='tests')
        self.assertEqual(feed.get_object('request', 'tests').name, 'tests')
        self.assertEqual(len(feed.items('tests')), 1)
        self.assertEqual(feed.link(tag), '/tags/tests/')
        self.assertEqual(feed.get_title(tag),
                         'Entries for the tag %s' % tag.name)
        self.assertEqual(feed.description(tag),
                         'The last entries tagged with %s' % tag.name)

    def test_tag_title_non_ascii(self):
        entry = self.create_published_entry()
        tag_unicode = smart_str('accentué')
        entry.tags = tag_unicode
        entry.save()
        feed = TagEntries()
        tag = Tag(name=tag_unicode)
        self.assertEqual(feed.get_title(tag),
                         'Entries for the tag %s' % tag_unicode)
        self.assertEqual(feed.description(tag),
                         'The last entries tagged with %s' % tag_unicode)

    def test_search_entries(self):
        class FakeRequest:
            def __init__(self, val):
                self.GET = {'pattern': val}
        self.create_published_entry()
        feed = SearchEntries()
        self.assertRaises(ObjectDoesNotExist,
                          feed.get_object, FakeRequest('te'))
        self.assertEqual(feed.get_object(FakeRequest('test')), 'test')
        self.assertEqual(len(feed.items('test')), 1)
        self.assertEqual(feed.link('test'), '/search/?pattern=test')
        self.assertEqual(feed.get_title('test'),
                         "Search results for '%s'" % 'test')
        self.assertEqual(
            feed.description('test'),
            "The last entries containing the pattern '%s'" % 'test')

    def test_entry_feed_no_authors(self):
        entry = self.create_published_entry()
        entry.authors.clear()
        feed = EntryFeed()
        self.assertEqual(feed.item_author_name(entry), None)

    def test_entry_feed_rss_or_atom(self):
        original_feed_format = LastEntries.feed_format
        LastEntries.feed_format = ''
        feed = LastEntries()
        self.assertEqual(feed.feed_type, DefaultFeed)
        LastEntries.feed_format = 'atom'
        feed = LastEntries()
        self.assertEqual(feed.feed_type, Atom1Feed)
        self.assertEqual(feed.subtitle, feed.description)
        LastEntries.feed_format = original_feed_format

    def test_title_with_sitename_implementation(self):
        feed = ZinniaFeed()
        self.assertRaises(NotImplementedError, feed.title)
        feed = LastEntries()
        self.assertEqual(feed.title(), 'example.com - Last entries')
