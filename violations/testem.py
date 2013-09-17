from django.template.loader import render_to_string
from tasks.const import STATUS_SUCCESS, STATUS_FAILED
from .base import library


@library.register('testem')
def testem_violation(data):
    """Testem violation

    :param data: task data
    :type data: dict
    :returns: dict
    """
    lines = data['raw'].split('\n')
    tests = 0
    pass_ = 0
    fail = 0
    for line in lines:
        if line.find('# tests') == 0:
            tests = int(line.split(' ')[-1])

        if line.find('# pass') == 0:
            pass_ = int(line.split(' ')[-1])

        if line.find('# fail') == 0:
            fail = int(line.split(' ')[-1])

    data['status'] = STATUS_SUCCESS if fail == 0 else STATUS_FAILED
    data['preview'] = render_to_string('violations/testem/preview.html', {
        'tests': tests,
        'pass': pass_,
        'fail': fail,
    })
    data['prepared'] = render_to_string('violations/testem/prepared.html', {
        'raw': data['raw'],
    })
    data['plot'] = {
        'tests': tests,
        'pass': pass_,
        'fail': fail,
    }
    return data
