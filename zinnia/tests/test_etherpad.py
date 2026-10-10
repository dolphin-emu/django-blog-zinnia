"""Optional pad creation, signed webhooks, and collaborative admin editing."""
import hashlib
import hmac
import json
from unittest.mock import patch

import requests
from django.contrib import admin
from django.contrib.sites.models import Site
from django.forms.models import model_to_dict
from django.test import TestCase, override_settings
from django.urls import reverse

from zinnia.admin.forms import EntryAdminForm
from zinnia.admin.widgets import EtherpadWidget
from zinnia.managers import DRAFT, PUBLISHED
from zinnia.models import Entry


@patch.multiple('zinnia.etherpad', ETHERPAD_URL='https://pad.example/',
                ETHERPAD_API_KEY='api-key')
class PadCreationTests(TestCase):
    def setUp(self):
        patcher = patch('zinnia.etherpad.requests.post')
        self.post = patcher.start()
        self.addCleanup(patcher.stop)
        self.post.return_value.json.return_value = {'code': 0}

    def create_entry(self, **kwargs):
        return Entry.objects.create(title='Draft', slug='draft', content='Original draft', **kwargs)

    def test_create_pad_once(self):
        entry = self.create_entry()
        self.assertTrue(entry.etherpad_id)
        entry.refresh_from_db()
        self.assertTrue(entry.etherpad_id)
        self.post.assert_called_once_with(
            'https://pad.example/api/1/createPad', timeout=5,
            data={'apikey': 'api-key', 'padID': entry.etherpad_id, 'text': 'Original draft'})
        entry.save()
        self.post.assert_called_once()

    def test_existing_pad_is_preserved(self):
        entry = self.create_entry(etherpad_id='existing-pad')
        self.post.assert_not_called()
        self.assertEqual(entry.etherpad_id, 'existing-pad')

    def test_disabled(self):
        with patch('zinnia.etherpad.ETHERPAD_URL', ''):
            self.assertIsNone(self.create_entry().etherpad_id)
            self.post.assert_not_called()

    def test_missing_api_key(self):
        with patch('zinnia.etherpad.ETHERPAD_API_KEY', ''):
            self.assertIsNone(self.create_entry().etherpad_id)
            self.post.assert_not_called()

    def test_network_failure_can_retry(self):
        self.post.side_effect = requests.ConnectionError('unavailable')
        with self.assertLogs('zinnia.etherpad', level='WARNING'):
            entry = self.create_entry()
        entry.refresh_from_db()
        self.assertIsNone(entry.etherpad_id)
        self.post.side_effect = None
        entry.save()
        entry.refresh_from_db()
        self.assertTrue(entry.etherpad_id)

    def test_api_rejection_does_not_record_pad(self):
        self.post.return_value.json.return_value = {'code': 1}
        with self.assertLogs('zinnia.etherpad', level='WARNING'):
            entry = self.create_entry()
        entry.refresh_from_db()
        self.assertIsNone(entry.etherpad_id)


@override_settings(ROOT_URLCONF='zinnia.tests.implementations.urls.default')
@patch.multiple('zinnia.views.etherpad', ETHERPAD_URL='https://pad.example',
                ETHERPAD_HMAC_KEY='secret')
class EtherpadWebhookTests(TestCase):
    def setUp(self):
        self.draft = Entry.objects.create(title='Draft', slug='draft', etherpad_id='draft-pad', content='Original')
        self.published = Entry.objects.create(title='Published', slug='published', etherpad_id='published-pad', content='Published original', status=PUBLISHED)
        self.url = reverse('zinnia:etherpad_event')

    def post_content(self, content, key=b'secret'):
        signature = hmac.new(key, content, hashlib.sha256).hexdigest().encode('ascii')
        return self.client.post(self.url, signature + b' ' + content, content_type='application/octet-stream')

    def test_updates_drafts_and_ignores_published_and_unknown_pads(self):
        old_update = self.draft.last_update
        events = [
            {'type': 'pad_update', 'id': 'draft-pad', 'text': 'First update'},
            {'type': 'pad_update', 'id': 'published-pad', 'text': 'Do not publish this'},
            {'type': 'pad_update', 'id': 'unknown-pad', 'text': 'Ignore this'},
            {'type': 'pad_update', 'id': 'draft-pad', 'text': 'Latest update'},
        ]
        self.assertEqual(self.post_content(json.dumps(events).encode()).status_code, 200)
        self.draft.refresh_from_db()
        self.published.refresh_from_db()
        self.assertEqual(self.draft.content, 'Latest update')
        self.assertGreater(self.draft.last_update, old_update)
        self.assertEqual(self.published.content, 'Published original')

    def test_wrong_signature(self):
        self.assertEqual(self.post_content(b'[]', b'wrong').status_code, 403)

    def test_malformed_payload(self):
        for content in (b'not-json', b'{}', b'[1]', b'[{"type":"pad_update"}]'):
            with self.subTest(content=content):
                self.assertEqual(self.post_content(content).status_code, 400)
        self.assertEqual(self.client.post(self.url, b'no-space', content_type='application/octet-stream').status_code, 400)

    def test_missing_hmac_key(self):
        with patch('zinnia.views.etherpad.ETHERPAD_HMAC_KEY', ''):
            self.assertEqual(self.post_content(b'[]').status_code, 404)

    def test_disabled(self):
        with patch('zinnia.views.etherpad.ETHERPAD_URL', ''):
            self.assertEqual(self.post_content(b'[]').status_code, 404)

    def test_get_is_not_accepted(self):
        self.assertEqual(self.client.get(self.url).status_code, 404)


@patch('zinnia.admin.forms.ETHERPAD_URL', 'https://pad.example')
@patch('zinnia.admin.widgets.ETHERPAD_URL', 'https://pad.example')
class EtherpadAdminTests(TestCase):
    def setUp(self):
        EntryAdminForm.admin_site = admin.site
        self.entry = Entry.objects.create(title='Draft', slug='draft', content='Original', etherpad_id='draft-pad', status=DRAFT)
        self.entry.sites.add(Site.objects.get_current())

    def test_admin_uses_pad_widget_and_preserves_webhook_content(self):
        data = model_to_dict(self.entry)
        data['content'] = 'Posted stale content'
        form = EntryAdminForm(data=data, instance=self.entry)
        self.assertIsInstance(form.fields['content'].widget, EtherpadWidget)
        self.assertTrue(form.fields['content'].disabled)
        self.assertTrue(form.is_valid(), form.errors)
        Entry.objects.filter(pk=self.entry.pk).update(content='Latest webhook content')
        form.save()
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.content, 'Latest webhook content')

    def test_disabled_uses_regular_editor(self):
        with patch('zinnia.admin.forms.ETHERPAD_URL', ''):
            form = EntryAdminForm(instance=self.entry)
            self.assertNotIsInstance(form.fields['content'].widget, EtherpadWidget)
            self.assertFalse(form.fields['content'].disabled)

    def test_published_uses_regular_editor(self):
        self.entry.status = PUBLISHED
        form = EntryAdminForm(instance=self.entry)
        self.assertNotIsInstance(form.fields['content'].widget, EtherpadWidget)

    def test_widget_url(self):
        html = EtherpadWidget('pad/with spaces').render('content', '')
        self.assertIn('https://pad.example/p/pad%2Fwith%20spaces?', html)
