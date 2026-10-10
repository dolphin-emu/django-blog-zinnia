"""Test cases for Zinnia's admin widgets"""
from django.test import TestCase
from django.test.utils import override_settings

from zinnia.admin.widgets import MPTTFilteredSelectMultiple
from zinnia.admin.widgets import MiniTextarea


class MPTTFilteredSelectMultipleTestCase(TestCase):
    maxDiff = None

    def test_optgroups(self):
        choices = [
            (1, 'Category 1', (1, 1)),
            (2, '|-- Category 2', (1, 2))
        ]

        widget = MPTTFilteredSelectMultiple(
            'test', False, choices=choices)

        optgroups = widget.optgroups('toto', '1')
        self.assertEqual(
            optgroups,
            [
                (
                    None, [
                        {
                            'index': '0',
                            'name': 'toto',
                            'template_name':
                            'django/forms/widgets/select_option.html',
                            'type': 'select',
                            'selected': True,
                            'attrs': {
                                'selected': True,
                                'data-tree-id': 1,
                                'data-left-value': 1
                            },
                            'value': 1,
                            'label': 'Category 1',
                            'wrap_label': True
                        }
                    ], 0
                ), (
                    None, [
                        {
                            'index': '1',
                            'name': 'toto',
                            'template_name':
                            'django/forms/widgets/select_option.html',
                            'type': 'select',
                            'selected': False,
                            'attrs': {
                                'data-tree-id': 1,
                                'data-left-value': 2
                            },
                            'value': 2,
                            'label': '|-- Category 2',
                            'wrap_label': True
                        }
                    ], 1
                )
            ]
        )

        optgroups = widget.optgroups('toto', ['2'])
        self.assertEqual(
            optgroups,
            [
                (
                    None, [
                        {
                            'index': '0',
                            'name': 'toto',
                            'template_name':
                            'django/forms/widgets/select_option.html',
                            'type': 'select',
                            'selected': False,
                            'attrs': {
                                'data-tree-id': 1,
                                'data-left-value': 1
                            },
                            'value': 1,
                            'label': 'Category 1',
                            'wrap_label': True
                        }
                    ], 0
                ), (
                    None, [
                        {
                            'index': '1',
                            'name': 'toto',
                            'template_name':
                            'django/forms/widgets/select_option.html',
                            'type': 'select',
                            'selected': True,
                            'attrs': {
                                'selected': True,
                                'data-tree-id': 1,
                                'data-left-value': 2
                            },
                            'value': 2,
                            'label': '|-- Category 2',
                            'wrap_label': True
                        }
                    ], 1
                )
            ]
        )

        optgroups = widget.optgroups('toto', '1', {'attribute': 'value'})
        self.assertEqual(
            optgroups,
            [
                (
                    None, [
                        {
                            'index': '0',
                            'name': 'toto',
                            'template_name':
                            'django/forms/widgets/select_option.html',
                            'type': 'select',
                            'selected': True,
                            'attrs': {
                                'selected': True,
                                'attribute': 'value',
                                'data-tree-id': 1,
                                'data-left-value': 1
                            },
                            'value': 1,
                            'label': 'Category 1',
                            'wrap_label': True
                        }
                    ], 0
                ), (
                    None, [
                        {
                            'index': '1',
                            'name': 'toto',
                            'template_name':
                            'django/forms/widgets/select_option.html',
                            'type': 'select',
                            'selected': False,
                            'attrs': {
                                'attribute': 'value',
                                'data-tree-id': 1,
                                'data-left-value': 2
                            },
                            'value': 2,
                            'label': '|-- Category 2',
                            'wrap_label': True
                        }
                    ], 1
                )
            ]
        )

    @override_settings(STATIC_URL='/s/')
    def test_media(self):
        medias = MPTTFilteredSelectMultiple('test', False).media
        self.assertEqual(medias._css, {})
        self.assertEqual(medias._js, [
            '/s/admin/js/core.js',
            '/s/zinnia/admin/mptt/js/mptt_m2m_selectbox.js',
            '/s/admin/js/SelectFilter2.js'])


class MiniTextareaTestCase(TestCase):

    def test_render(self):
        widget = MiniTextarea()
        self.assertHTMLEqual(
            widget.render('field', 'value'),
            '<textarea class="vLargeTextField" '
            'cols="40" name="field" rows="2">'
            '\r\nvalue</textarea>')
