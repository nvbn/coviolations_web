from django.template.loader import render_to_string
from tasks.const import STATUS_SUCCESS
from .base import library


@library.register('dummy')
def dummy_violation(data):
    """Return data without parsing

    :param data: task data
    :type data: dict
    :returns: dict
    """
    data['status'] = STATUS_SUCCESS
    prepared = render_to_string('violations/dummy.html', {
        'raw': data['raw'],
    })
    data['preview'] = prepared
    data['prepared'] = prepared
    return data
