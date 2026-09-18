"""Test cases for Zinnia's admin"""

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test import RequestFactory
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import activate
from django.utils.translation import deactivate

from zinnia.admin.category import CategoryAdmin
from zinnia.admin.entry import EntryAdmin
from zinnia.managers import PUBLISHED
from zinnia.models.author import Author
from zinnia.models.category import Category
from zinnia.models.entry import Entry
from zinnia.signals import disconnect_entry_signals
from zinnia.tests.utils import datetime
from zinnia.tests.utils import skip_if_custom_user
from zinnia.url_shortener.backends.default import base36


class BaseAdminTestCase(TestCase):
    rich_urls = 'zinnia.tests.implementations.urls.default'
    poor_urls = 'zinnia.tests.implementations.urls.poor'
    model_class = None
    admin_class = None

    def setUp(self):
        disconnect_entry_signals()
        activate('en')
        self.site = AdminSite()
        self.admin = self.admin_class(
            self.model_class, self.site)

    def tearDown(self):
        """
        Deactivate the translation system.
        """
        deactivate()

    def check_with_rich_and_poor_urls(self, func, args,
                                      result_rich, result_poor):
        with self.settings(ROOT_URLCONF=self.rich_urls):
            self.assertEqual(func(*args), result_rich)
        with self.settings(ROOT_URLCONF=self.poor_urls):
            self.assertEqual(func(*args), result_poor)


class TestMessageBackend:
    """Message backend for testing"""
    def __init__(self, *ka, **kw):
        self.messages = []

    def add(self, *ka, **kw):
        self.messages.append(ka)


@skip_if_custom_user
class EntryAdminTestCase(BaseAdminTestCase):
    """Test case for Entry Admin"""
    model_class = Entry
    admin_class = EntryAdmin

    def setUp(self):
        super().setUp()
        params = {'title': 'My title',
                  'content': 'My content',
                  'slug': 'my-title'}
        self.entry = Entry.objects.create(**params)
        self.request_factory = RequestFactory()
        self.request = self.request_factory.get('/')

    def test_get_title(self):
        self.assertEqual(self.admin.get_title(self.entry),
                         'My title (2 words)')

    def test_get_authors(self):
        self.check_with_rich_and_poor_urls(
            self.admin.get_authors, (self.entry,),
            '', '')
        author_1 = Author.objects.create_user(
            'author-1', 'author1@example.com')
        author_2 = Author.objects.create_user(
            'author<2>', 'author2@example.com')
        self.entry.authors.add(author_1)
        self.check_with_rich_and_poor_urls(
            self.admin.get_authors, (self.entry,),
            '<a href="/authors/author-1/" target="blank">author-1</a>',
            'author-1')
        self.entry.authors.add(author_2)
        self.check_with_rich_and_poor_urls(
            self.admin.get_authors, (self.entry,),
            '<a href="/authors/author-1/" target="blank">author-1</a>, '
            '<a href="/authors/author%3C2%3E/" target="blank">'
            'author&lt;2&gt;</a>',
            'author-1, author&lt;2&gt;')

    def test_get_authors_non_ascii(self):
        author = Author.objects.create_user(
            'тест', 'test@example.com')
        self.entry.authors.add(author)
        self.check_with_rich_and_poor_urls(
            self.admin.get_authors, (self.entry,),
            '<a href="/authors/%D1%82%D0%B5%D1%81%D1%82/" '
            'target="blank">тест</a>',
            'тест')

    def test_get_categories(self):
        self.check_with_rich_and_poor_urls(
            self.admin.get_categories, (self.entry,),
            '', '')
        category_1 = Category.objects.create(title='Category <b>1</b>',
                                             slug='category-1')
        category_2 = Category.objects.create(title='Category <b>2</b>',
                                             slug='category-2')
        self.entry.categories.add(category_1)
        self.check_with_rich_and_poor_urls(
            self.admin.get_categories, (self.entry,),
            '<a href="/categories/category-1/" target="blank">'
            'Category &lt;b&gt;1&lt;/b&gt;</a>',
            'Category &lt;b&gt;1&lt;/b&gt;')
        self.entry.categories.add(category_2)
        self.check_with_rich_and_poor_urls(
            self.admin.get_categories, (self.entry,),
            '<a href="/categories/category-1/" target="blank">'
            'Category &lt;b&gt;1&lt;/b&gt;</a>, '
            '<a href="/categories/category-2/" target="blank">Category '
            '&lt;b&gt;2&lt;/b&gt;</a>',
            'Category &lt;b&gt;1&lt;/b&gt;, Category &lt;b&gt;2&lt;/b&gt;')

    def test_get_categories_non_ascii(self):
        category = Category.objects.create(title='Category тест',
                                           slug='category')
        self.entry.categories.add(category)
        self.check_with_rich_and_poor_urls(
            self.admin.get_categories, (self.entry,),
            '<a href="/categories/category/" target="blank">'
            'Category тест</a>',
            'Category тест')

    def test_get_tags(self):
        self.check_with_rich_and_poor_urls(
            self.admin.get_tags, (self.entry,),
            '', '')
        self.entry.tags = 'zinnia'
        self.check_with_rich_and_poor_urls(
            self.admin.get_tags, (self.entry,),
            '<a href="/tags/zinnia/" target="blank">zinnia</a>',
            'zinnia')
        self.entry.tags = 'zinnia, t<e>st'
        self.check_with_rich_and_poor_urls(
            self.admin.get_tags, (self.entry,),
            '<a href="/tags/t%3Ce%3Est/" target="blank">t&lt;e&gt;st</a>, '
            '<a href="/tags/zinnia/" target="blank">zinnia</a>',
            'zinnia, t&lt;e&gt;st')  # Yes, this is not the same order...

    def test_get_tags_non_ascii(self):
        self.entry.tags = 'тест'
        self.check_with_rich_and_poor_urls(
            self.admin.get_tags, (self.entry,),
            '<a href="/tags/%D1%82%D0%B5%D1%81%D1%82/" '
            'target="blank">тест</a>',
            'тест')

    def test_get_sites(self):
        self.assertEqual(self.admin.get_sites(self.entry), '')
        self.entry.sites.add(Site.objects.get_current())
        self.check_with_rich_and_poor_urls(
            self.admin.get_sites, (self.entry,),
            '<a href="http://example.com/" target="blank">example.com</a>',
            '<a href="http://example.com" target="blank">example.com</a>')

    def test_get_short_url(self):
        with self.settings(ROOT_URLCONF=self.poor_urls):
            entry_url = self.entry.get_absolute_url()

        self.check_with_rich_and_poor_urls(
            self.admin.get_short_url, (self.entry,),
            '<a href="http://example.com/%(hash)s/" target="blank">'
            'http://example.com/%(hash)s/</a>' % {
                'hash': base36(self.entry.pk)},
            '<a href="%(url)s" target="blank">%(url)s</a>' % {
                'url': entry_url})

    def test_get_is_visible(self):
        self.assertEqual(self.admin.get_is_visible(self.entry),
                         self.entry.is_visible)

    def test_queryset(self):
        user = Author.objects.create_user(
            'user', 'user@exemple.com')
        self.entry.authors.add(user)
        root = Author.objects.create_superuser(
            'root', 'root@exemple.com', 'toor')
        params = {'title': 'My root title',
                  'content': 'My root content',
                  'slug': 'my-root-titile'}
        root_entry = Entry.objects.create(**params)
        root_entry.authors.add(root)
        self.request.user = User.objects.get(pk=user.pk)
        self.assertEqual(len(self.admin.get_queryset(self.request)), 1)
        self.request.user = User.objects.get(pk=root.pk)
        self.assertEqual(len(self.admin.get_queryset(self.request)), 2)

    def test_get_changeform_initial_data(self):
        user = User.objects.create_user(
            'user', 'user@exemple.com')
        site = Site.objects.get_current()
        self.request.user = user
        data = self.admin.get_changeform_initial_data(self.request)
        self.assertEqual(data, {'authors': [user.pk],
                                'sites': [site.pk]})
        request = self.request_factory.get('/?title=data')
        request.user = user
        data = self.admin.get_changeform_initial_data(request)
        self.assertEqual(data, {'title': 'data'})

    def test_formfield_for_manytomany(self):
        staff = User.objects.create_user(
            'staff', 'staff@exemple.com')
        author = User.objects.create_user(
            'author', 'author@exemple.com')
        root = User.objects.create_superuser(
            'root', 'root@exemple.com', 'toor')
        self.request.user = root
        field = self.admin.formfield_for_manytomany(
            Entry.authors.field, self.request)
        self.assertEqual(field.queryset.count(), 1)
        staff.is_staff = True
        staff.save()
        field = self.admin.formfield_for_manytomany(
            Entry.authors.field, self.request)
        self.assertEqual(field.queryset.count(), 2)
        self.entry.authors.add(Author.objects.get(pk=author.pk))
        field = self.admin.formfield_for_manytomany(
            Entry.authors.field, self.request)
        self.assertEqual(field.queryset.count(), 3)

    def test_get_readonly_fields(self):
        user = User.objects.create_user(
            'user', 'user@exemple.com')
        root = User.objects.create_superuser(
            'root', 'root@exemple.com', 'toor')
        self.request.user = user
        self.assertEqual(self.admin.get_readonly_fields(self.request),
                         ['status', 'authors'])
        self.request.user = root
        self.assertEqual(self.admin.get_readonly_fields(self.request),
                         [])

    def test_get_actions(self):
        user = User.objects.create_user(
            'user', 'user@exemple.com')
        root = User.objects.create_superuser(
            'root', 'root@exemple.com', 'toor')
        self.request.user = user
        self.assertEqual(
            list(self.admin.get_actions(self.request).keys()),
            ['put_on_top',
             'mark_featured',
             'unmark_featured'])
        self.request.user = root
        self.assertEqual(
            list(self.admin.get_actions(self.request).keys()),
            ['delete_selected',
             'make_mine',
             'make_published',
             'make_hidden',
             'put_on_top',
             'mark_featured',
             'unmark_featured'])

    def test_get_actions_in_popup_mode_issue_291(self):
        user = User.objects.create_user(
            'user', 'user@exemple.com')
        request = self.request_factory.get('/?_popup=1')
        request.user = user
        self.assertEqual(
            list(self.admin.get_actions(request).keys()),
            [])

    def test_make_mine(self):
        user = Author.objects.create_user(
            'user', 'user@exemple.com')
        self.request.user = User.objects.get(pk=user.pk)
        self.request._messages = TestMessageBackend()
        self.assertEqual(user.entries.count(), 0)
        self.admin.make_mine(self.request, Entry.objects.all())
        self.assertEqual(user.entries.count(), 1)
        self.assertEqual(len(self.request._messages.messages), 1)

    def test_make_published(self):
        self.request._messages = TestMessageBackend()
        self.entry.sites.add(Site.objects.get_current())
        self.assertEqual(Entry.published.count(), 0)
        self.admin.make_published(self.request, Entry.objects.all())
        self.assertEqual(Entry.published.count(), 1)
        self.assertEqual(len(self.request._messages.messages), 1)

    def test_make_hidden(self):
        self.request._messages = TestMessageBackend()
        self.entry.status = PUBLISHED
        self.entry.save()
        self.entry.sites.add(Site.objects.get_current())
        self.assertEqual(Entry.published.count(), 1)
        self.admin.make_hidden(self.request, Entry.objects.all())
        self.assertEqual(Entry.published.count(), 0)
        self.assertEqual(len(self.request._messages.messages), 1)

    def test_put_on_top(self):
        self.request._messages = TestMessageBackend()
        self.entry.publication_date = datetime(2011, 1, 1, 12, 0)
        self.admin.put_on_top(self.request, Entry.objects.all())
        self.assertEqual(
            Entry.objects.get(pk=self.entry.pk).creation_date.date(),
            timezone.now().date())
        self.assertEqual(len(self.request._messages.messages), 1)

    def test_mark_unmark_featured(self):
        self.request._messages = TestMessageBackend()
        self.assertEqual(Entry.objects.filter(
            featured=True).count(), 0)
        self.admin.mark_featured(self.request, Entry.objects.all())
        self.assertEqual(Entry.objects.filter(featured=True).count(), 1)
        self.assertEqual(len(self.request._messages.messages), 1)
        self.admin.unmark_featured(self.request, Entry.objects.all())
        self.assertEqual(Entry.objects.filter(featured=True).count(), 0)
        self.assertEqual(len(self.request._messages.messages), 2)

class CategoryAdminTestCase(BaseAdminTestCase):
    """Test cases for Category Admin"""
    model_class = Category
    admin_class = CategoryAdmin

    def test_get_tree_path(self):
        category = Category.objects.create(title='Category', slug='cat')

        self.check_with_rich_and_poor_urls(
            self.admin.get_tree_path, (category,),
            '<a href="/categories/cat/" target="blank">/cat/</a>',
            '/cat/')


@skip_if_custom_user
@override_settings(
    DEBUG=True
)
class FunctionnalAdminTestCase(TestCase):
    """
    Functional testing admin integration.

    We just executing the view to see if the integration works.
    """

    def setUp(self):
        disconnect_entry_signals()
        self.author = Author.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password'
        )

        self.category = Category.objects.create(
            title='Category', slug='cat'
        )
        params = {
            'title': 'My title',
            'content': 'My content',
            'slug': 'my-title'
        }
        self.entry = Entry.objects.create(**params)
        self.client.force_login(self.author)

    def assert_admin(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_admin_entry_list(self):
        self.assert_admin(
            reverse('admin:zinnia_entry_changelist')
        )

    def test_admin_category_list(self):
        self.assert_admin(
            reverse('admin:zinnia_category_changelist')
        )

    def test_admin_entry_add(self):
        self.assert_admin(
            reverse('admin:zinnia_entry_add')
        )

    def test_admin_category_add(self):
        self.assert_admin(
            reverse('admin:zinnia_category_add')
        )

    def test_admin_entry_update(self):
        self.assert_admin(
            reverse('admin:zinnia_entry_change', args=[self.entry.pk])
        )

    def test_admin_category_update(self):
        self.assert_admin(
            reverse('admin:zinnia_category_change', args=[self.category.pk])
        )
