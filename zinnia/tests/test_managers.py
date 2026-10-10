"""Test cases for Zinnia's managers"""
from django.contrib.sites.models import Site
from django.test import TestCase

from tagging.models import Tag

from zinnia.managers import PUBLISHED
from zinnia.managers import entries_published
from zinnia.managers import tags_published
from zinnia.models.author import Author
from zinnia.models.category import Category
from zinnia.models.entry import Entry
from zinnia.tests.utils import datetime
from zinnia.tests.utils import skip_if_custom_user


@skip_if_custom_user
class ManagersTestCase(TestCase):

    def setUp(self):
        self.sites = [
            Site.objects.get_current(),
            Site.objects.create(domain='http://domain.com',
                                name='Domain.com')]
        self.authors = [
            Author.objects.create_user(username='webmaster',
                                       email='webmaster@example.com'),
            Author.objects.create_user(username='contributor',
                                       email='contributor@example.com')]
        self.categories = [
            Category.objects.create(title='Category 1',
                                    slug='category-1'),
            Category.objects.create(title='Category 2',
                                    slug='category-2')]

        params = {'title': 'My entry 1', 'content': 'My content 1',
                  'tags': 'zinnia, test', 'slug': 'my-entry-1',
                  'status': PUBLISHED}
        self.entry_1 = Entry.objects.create(**params)
        self.entry_1.authors.add(self.authors[0])
        self.entry_1.categories.add(*self.categories)
        self.entry_1.sites.add(*self.sites)

        params = {'title': 'My entry 2', 'content': 'My content 2',
                  'tags': 'zinnia, test', 'slug': 'my-entry-2'}
        self.entry_2 = Entry.objects.create(**params)
        self.entry_2.authors.add(*self.authors)
        self.entry_2.categories.add(self.categories[0])
        self.entry_2.sites.add(self.sites[0])

    def test_tags_published(self):
        self.assertEqual(tags_published().count(), Tag.objects.count())
        Tag.objects.create(name='out')
        self.assertNotEqual(tags_published().count(), Tag.objects.count())

    def test_author_published_manager_get_query_set(self):
        self.assertEqual(Author.published.count(), 1)
        self.entry_2.status = PUBLISHED
        self.entry_2.save()
        self.assertEqual(Author.published.count(), 2)
        self.entry_2.sites.remove(self.sites[0])
        self.entry_2.sites.add(self.sites[1])
        self.assertEqual(Author.published.count(), 1)

    def test_category_published_manager_get_query_set(self):
        category = Category.objects.create(
            title='Third Category', slug='third-category')
        self.assertEqual(Category.published.count(), 2)
        self.entry_2.categories.add(category)
        self.entry_2.status = PUBLISHED
        self.entry_2.save()
        self.assertEqual(Category.published.count(), 3)

    def test_entries_published(self):
        self.assertEqual(entries_published(Entry.objects.all()).count(), 1)
        self.entry_2.status = PUBLISHED
        self.entry_2.save()
        self.assertEqual(entries_published(Entry.objects.all()).count(), 2)
        self.entry_1.sites.clear()
        self.assertEqual(entries_published(Entry.objects.all()).count(), 1)
        self.entry_1.sites.add(*self.sites)
        self.entry_1.start_publication = datetime(2030, 1, 1)
        self.entry_1.save()
        self.assertEqual(entries_published(Entry.objects.all()).count(), 1)
        self.entry_1.start_publication = datetime(2000, 1, 1)
        self.entry_1.save()
        self.assertEqual(entries_published(Entry.objects.all()).count(), 2)
        self.entry_1.end_publication = datetime(2000, 1, 1)
        self.entry_1.save()
        self.assertEqual(entries_published(Entry.objects.all()).count(), 1)
        self.entry_1.end_publication = datetime(2030, 1, 1)
        self.entry_1.save()
        self.assertEqual(entries_published(Entry.objects.all()).count(), 2)

    def test_entry_published_manager_get_query_set(self):
        self.assertEqual(Entry.published.count(), 1)
        self.entry_2.status = PUBLISHED
        self.entry_2.save()
        self.assertEqual(Entry.published.count(), 2)
        self.entry_1.sites.clear()
        self.assertEqual(Entry.published.count(), 1)
        self.entry_1.sites.add(*self.sites)
        self.entry_1.start_publication = datetime(2030, 1, 1)
        self.entry_1.save()
        self.assertEqual(Entry.published.count(), 1)
        self.entry_1.start_publication = datetime(2000, 1, 1)
        self.entry_1.save()
        self.assertEqual(Entry.published.count(), 2)
        self.entry_1.end_publication = datetime(2000, 1, 1)
        self.entry_1.save()
        self.assertEqual(Entry.published.count(), 1)
        self.entry_1.end_publication = datetime(2030, 1, 1)
        self.entry_1.save()
        self.assertEqual(Entry.published.count(), 2)

    def test_entry_published_manager_on_site(self):
        self.assertEqual(Entry.published.on_site().count(), 2)
        self.entry_2.sites.clear()
        self.entry_2.sites.add(self.sites[1])
        self.assertEqual(Entry.published.on_site().count(), 1)
        self.entry_1.sites.clear()
        self.assertEqual(Entry.published.on_site().count(), 0)
