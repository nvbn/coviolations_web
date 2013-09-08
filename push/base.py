import json
import redis
from django.conf import settings


class PushSender(object):
    """Push sender"""

    @property
    def r(self):
        """Init redis connection"""
        if not hasattr(self, '_r'):
            self._r = redis.Redis()
        return self._r

    def send(self, **msg):
        """Send message to redis channel"""
        self.r.publish(settings.REDIS_PUSH, json.dumps(msg))


sender = PushSender()
