from tools.library import BaseLibrary
from .exceptions import ServiceDoesNotExists


class ServicesLibrary(BaseLibrary):
    """Library for register and access available services

    .. automethod:: register
    .. automethod:: get
    .. automethod:: has

    .. doctest::

        from services.base import library

        @library.register('service')
        def service(data):
            return data

        library.get('service')
        library.has('service')
    """
    exception = ServiceDoesNotExists

library = ServicesLibrary()
