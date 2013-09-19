import re
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
    runs = []
    tests = 0
    pass_ = 0
    fail = 0
    not_ok = False

    for line in lines:
        ok_match = re.match(r'^(.*ok) (\d*) (.*) - (.*)$', line)
        if ok_match:
            runs.append(ok_match.groups() + ([],))
            if ok_match.groups()[0] == 'not ok':
                not_ok = True

        if not len(line):
            not_ok = False

        if not_ok and line.find('        ') == 0:
            runs[-1][-1].append(line[8:])

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
        'tests': tests,
        'pass': pass_,
        'fail': fail,
        'runs': runs,
    })
    data['plot'] = {
        'tests': tests,
        'pass': pass_,
        'fail': fail,
    }
    return data
