from functools import partial
from operator import is_not
import re
from django.template.loader import render_to_string
from tasks.const import STATUS_SUCCESS, STATUS_FAILED
from .base import library


match_line = partial(re.match, r'^(.*)==(.*) is available \(you have (.*)\)$')
not_none = partial(is_not, None)


@library.register('pip_review')
def pip_review_violation(data):
    """pip-review violation parser

    :param data: task data
    :type data: dict
    :returns: dict
    """
    count = len(data['raw'].split('\n')) - 1

    packages = [
        match.groups()
        for match in map(match_line, data['raw'].split('\n')) if match
    ]
    data['status'] = STATUS_SUCCESS if count == 0 else STATUS_FAILED
    data['preview'] = render_to_string('violations/pip_review/preview.html', {
        'count': count,
    })
    data['prepared'] = render_to_string(
        'violations/pip_review/prepared.html', {'packages': packages},
    )
    data['plot'] = {
        'outdated': count,
    }
    return data
