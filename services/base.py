from tools.library import BaseLibrary
from .exceptions import ServiceDoesNotExists


class ServicesLibrary(BaseLibrary):
    """Services library"""
    exception = ServiceDoesNotExists

library = ServicesLibrary()
