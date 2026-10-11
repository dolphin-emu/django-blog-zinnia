"""Test cases for Zinnia's markups"""
import builtins
import warnings
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from django.test import override_settings

from zinnia import markups
from zinnia.markups import html_format
from zinnia.markups import markdown
from zinnia.models.entry import Entry
from zinnia.tests.utils import skip_if_lib_not_available


class MarkupsTestCase(TestCase):
    text = 'Hello *World* !'

    @skip_if_lib_not_available('markdown')
    def test_markdown(self):
        self.assertHTMLEqual(
            markdown(self.text).strip(),
            '<p>Hello <em>World</em> !</p>'
        )

    @skip_if_lib_not_available('markdown')
    def test_markdown_extensions(self):
        cache.clear()
        self.addCleanup(cache.clear)
        text = '[TOC]\n\n# Header 1\n\n## Header 2'
        self.assertHTMLEqual(
            markdown(text).strip(),
            '<p>[TOC]</p>\n<h1>Header 1</h1>'
            '\n<h2>Header 2</h2>'
        )
        cache.clear()
        self.assertHTMLEqual(
            markdown(text, extensions=['markdown.extensions.toc']).strip(),
            '<div class="toc">\n<ul>\n<li><a href="#header-1">'
            'Header 1</a><ul>\n<li><a href="#header-2">'
            'Header 2</a></li>\n</ul>\n</li>\n</ul>\n</div>'
            '\n<h1 id="header-1">Header 1</h1>\n'
            '<h2 id="header-2">Header 2</h2>'
        )
        from markdown.extensions.toc import TocExtension
        tocext = TocExtension(marker='--TOC--', permalink='PL')
        cache.clear()
        self.assertHTMLEqual(
            markdown(text, extensions=[tocext]).strip(),
            '<p>[TOC]</p>\n<h1 id="header-1">Header 1'
            '<a class="headerlink" href="#header-1" '
            'title="Permanent link">PL</a></h1>\n'
            '<h2 id="header-2">Header 2'
            '<a class="headerlink" href="#header-2" '
            'title="Permanent link">PL</a></h2>'
        )


class MarkupFailImportTestCase(TestCase):
    exclude_list = ['markdown']

    def setUp(self):
        self.original_import = builtins.__import__
        builtins.__import__ = self.import_hook

    def tearDown(self):
        builtins.__import__ = self.original_import

    def import_hook(self, name, *args, **kwargs):
        if name in self.exclude_list:
            raise ImportError('%s module has been disabled' % name)
        else:
            self.original_import(name, *args, **kwargs)

    def test_markdown(self):
        with warnings.catch_warnings(record=True) as w:
            result = markdown('My *text*')
        self.tearDown()
        self.assertEqual(result, 'My *text*')
        self.assertTrue(issubclass(w[-1].category, RuntimeWarning))
        self.assertEqual(
            str(w[-1].message),
            "The Python markdown library isn't installed.")


class HtmlFormatTestCase(TestCase):

    def setUp(self):
        self.original_rendering = markups.MARKUP_LANGUAGE

    def tearDown(self):
        markups.MARKUP_LANGUAGE = self.original_rendering

    def test_html_format_default(self):
        markups.MARKUP_LANGUAGE = None
        self.assertHTMLEqual(html_format(''), '')
        self.assertHTMLEqual(html_format('Content'), '<p>Content</p>')
        self.assertEqual(html_format('Content</p>'), 'Content</p>')
        self.assertHTMLEqual(
            html_format('Hello\nworld!'),
            '<p>Hello<br />world!</p>'
        )

    @skip_if_lib_not_available('markdown')
    def test_html_content_markdown(self):
        markups.MARKUP_LANGUAGE = 'markdown'
        value = 'Hello world !\n\n' \
                'this is my content :\n\n' \
                '* Item 1\n* Item 2'
        self.assertHTMLEqual(
            html_format(value),
            '<p>Hello world !</p>\n'
            '<p>this is my content :</p>'
            '\n<ul>\n<li>Item 1</li>\n'
            '<li>Item 2</li>\n</ul>'
        )


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'zinnia-markdown-tests',
    }
})
class MarkdownCacheTestCase(TestCase):

    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)

    @skip_if_lib_not_available('markdown')
    def test_render_once_across_instances_and_refresh_after_edit(self):
        import markdown as renderer

        saved = Entry.objects.create(
            title='Cached', slug='cached', content='**Content**',
            excerpt='**Excerpt**', lead='**Lead**')
        with patch('zinnia.models.entry.MARKUP_LANGUAGE', 'markdown'), \
                patch('zinnia.markups.MARKUP_LANGUAGE', 'markdown'), \
                patch('markdown.markdown', wraps=renderer.markdown) as render:
            for instance in (saved, Entry.objects.get(pk=saved.pk)):
                self.assertEqual(instance.html_content,
                                 '<p><strong>Content</strong></p>')
                self.assertEqual(instance.html_excerpt,
                                 '<p><strong>Excerpt</strong></p>')
                self.assertEqual(instance.html_lead,
                                 '<p><strong>Lead</strong></p>')
            self.assertEqual(render.call_count, 3)

            saved.content = '*Edited*'
            self.assertEqual(saved.html_content, '<p><em>Edited</em></p>')
            saved.save()
            self.assertEqual(Entry.objects.get(pk=saved.pk).html_content,
                             '<p><em>Edited</em></p>')
            self.assertEqual(render.call_count, 4)

    @skip_if_lib_not_available('markdown')
    def test_extension_changes_require_cache_clear(self):
        import markdown as renderer

        with patch('markdown.markdown', wraps=renderer.markdown) as render:
            plain = markdown('# Heading')
            self.assertEqual(markdown('# Heading', ['toc']), plain)
            self.assertEqual(render.call_count, 1)

            cache.clear()
            linked = markdown('# Heading', ['toc'])
            self.assertNotEqual(plain, linked)
            self.assertEqual(markdown('# Heading', ['toc']), linked)
            self.assertEqual(render.call_count, 2)

    @skip_if_lib_not_available('markdown')
    def test_empty_result_and_eviction(self):
        import markdown as renderer

        with patch('markdown.markdown', wraps=renderer.markdown) as render:
            self.assertEqual(markdown(''), '')
            self.assertEqual(markdown(''), '')
            self.assertEqual(render.call_count, 1)
            cache.clear()
            self.assertEqual(markdown(''), '')
            self.assertEqual(render.call_count, 2)
