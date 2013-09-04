from functools import partial
from django.conf import settings


class BaseLibrary(object):
    """Base library"""
    exception = None
    enabled_settings = None

    def __init__(self):
        self._items = {}

    def _register_fnc(self, name, fnc):
        if name in getattr(settings, self.enabled_settings):
            self._items[name] = fnc
        return fnc

    def register(self, name):
        """Register in library"""
        return partial(self._register_fnc, name)

    def get(self, name):
        """Get item"""
        try:
            return self._items[name]
        except KeyError:
            raise self.exception(name)
