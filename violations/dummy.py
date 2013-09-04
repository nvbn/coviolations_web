from .base import library


@library.register('dummy')
def dummy_violation(data):
    """Return data without parsing"""
    return data
