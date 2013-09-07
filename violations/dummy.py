from tasks.const import STATUS_SUCCESS
from .base import library


@library.register('dummy')
def dummy_violation(data):
    """Return data without parsing"""
    data['status'] = STATUS_SUCCESS
    data['preview'] = '<pre>{}</pre>'.format(data['raw'])
    data['prepared'] = '<pre>{}</pre>'.format(data['raw'])
    return data
