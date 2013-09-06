from tools.library import BaseLibrary
from .exceptions import ViolationDoesNotExists


class ViolationsLibrary(BaseLibrary):
    """Violations library"""
    exception = ViolationDoesNotExists

library = ViolationsLibrary()
