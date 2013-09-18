from django.template.loader import render_to_string
from tasks.const import STATUS_SUCCESS, STATUS_FAILED
from .base import library


@library.register('pip_review')
def pip_review_violation(data):
    """pip-review violation parser

    :param data: task data
    :type data: dict
    :returns: dict
    """
    count = len(data['raw'].split('\n')) - 1
    data['status'] = STATUS_SUCCESS if count == 0 else STATUS_FAILED
    data['preview'] = render_to_string('violations/pip_review/preview.html', {
        'count': count,
    })
    data['prepared'] = render_to_string(
        'violations/pip_review/prepared.html', {'raw': data['raw']},
    )
    data['plot'] = {
        'outdated': count,
    }
    return data
