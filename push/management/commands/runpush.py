import json
from django.core.management import BaseCommand
from tornado import web, ioloop, gen
import tornadoredis
from sockjs.tornado import SockJSRouter, SockJSConnection
from django.conf import settings


class SubscriptionsConnection(SockJSConnection):
    """Subscription connection"""

    def _create_redis(self):
        """Create redis connection"""
        self.client = tornadoredis.Client()
        self.client.connect()

    @gen.engine
    def listen(self):
        """Start listening"""
        self._create_redis()
        yield gen.Task(self.client.subscribe, settings.REDIS_PUSH)
        self.client.listen(self.on_redis)

    def on_message(self, msg):
        """On new message"""
        data = json.loads(msg)
        if data['method'] == 'subscribe':
            self.owner = data['owner']
            self.listen()

    def on_redis(self, msg):
        """On redis message"""
        if msg.kind == 'message':
            data = json.loads(msg.body)
            if data['owner'] == self.owner:
                self.send(json.dumps(data))


class Command(BaseCommand):
    help = 'run tornado push notifiactions server'

    def handle(self, port=9999, *args, **kwargs):
        router = SockJSRouter(SubscriptionsConnection, '/sub')
        app = web.Application(router.urls)
        app.listen(port)
        ioloop.IOLoop.instance().start()
