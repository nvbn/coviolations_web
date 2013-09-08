from mock import MagicMock
from django.test import TestCase
from .. import base


class PushSenderCase(TestCase):
    """Push sender case"""

    def setUp(self):
        base.sender._r = MagicMock()

    def tearDown(self):
        del base.sender._r

    def test_send(self):
        """Test send"""
        base.sender.send(owner='test')
        self.assertEqual(base.sender.r.publish.call_count, 1)
