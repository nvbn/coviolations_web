from django.template.loader import render_to_string
from tasks.const import STATUS_SUCCESS, STATUS_FAILED
from .base import library


@library.register('pep8')
def pep8_violation(data):
    """PEP8 violation parser"""
    count = len(data['raw'].split('\n'))
    data['status'] = STATUS_SUCCESS if count == 0 else STATUS_FAILED
    data['preview'] = render_to_string('violations/pep8/preview.html', {
        'count': count,
    })
    data['prepared'] = render_to_string('violations/pep8/prepared.html', {
        'raw': data['raw'],
    })
    data['plot'] = {
        'count': count,
    }
    return data
