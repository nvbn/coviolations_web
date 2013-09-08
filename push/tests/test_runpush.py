import json
from mock import MagicMock
from tornado.testing import AsyncTestCase
from ..management.commands import runpush


class SubscriptionConnectionCase(AsyncTestCase):
    """Subscription connection case"""

    def setUp(self):
        super(SubscriptionConnectionCase, self).setUp()
        self._orig_redis = runpush.tornadoredis.Client
        runpush.tornadoredis.Client = MagicMock()
        self.connection = runpush.SubscriptionsConnection(None)

    def tearDown(self):
        runpush.tornadoredis.Client = self._orig_redis

    def test_subscribe(self):
        """Test subscription to notifications"""
        self.connection.on_message(json.dumps({
            'method': 'subscribe',
            'owner': 'test',
        }))
        self.assertEqual(self.connection.owner, 'test')

    def test_on_redis(self):
        """Test on redis message"""
        self.connection.send = MagicMock()
        self.connection.owner = 'test'
        self.connection.on_redis(MagicMock(
            kind='message',
            body=json.dumps({
                'owner': 'test',
            }),
        ))
        self.assertEqual(self.connection.send.call_count, 1)
