from tools.library import BaseLibrary
from .exceptions import ViolationDoesNotExists


class ViolationsLibrary(BaseLibrary):
    """Library for register and access available violations

    .. automethod:: register
    .. automethod:: get
    .. automethod:: has

    .. doctest::

        from violations.base import library

        @library.register('violation')
        def violation(data):
            return data

        library.get('violation')
        library.has('violation')
    """
    exception = ViolationDoesNotExists

library = ViolationsLibrary()
