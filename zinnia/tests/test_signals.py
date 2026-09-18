"""Test cases for Zinnia's signals"""
from django.test import TestCase

from zinnia.signals import disable_for_loaddata
from zinnia.signals import disconnect_discussion_signals
from zinnia.signals import disconnect_entry_signals


class SignalsTestCase(TestCase):
    """Test cases for signals"""

    def setUp(self):
        disconnect_entry_signals()
        disconnect_discussion_signals()

    def test_disable_for_loaddata(self):
        self.top = 0

        @disable_for_loaddata
        def make_top():
            self.top += 1

        def call():
            return make_top()

        call()
        self.assertEqual(self.top, 1)
        # Okay the command is executed
