from functools import partial
from django.conf import settings
from .exceptions import ViolationDoesNotExists


class ViolationsLibrary(object):
    """Violations library"""

    def __init__(self):
        self._violations = {}

    def _register_fnc(self, name, fnc):
        if name in settings.VIOLATIONS:
            self._violations[name] = fnc
        return fnc

    def register(self, name):
        """Register violation in library"""
        return partial(self._register_fnc, name)

    def get(self, name):
        """Get violation"""
        try:
            return self._violations[name]
        except KeyError:
            raise ViolationDoesNotExists(name)


library = ViolationsLibrary()
