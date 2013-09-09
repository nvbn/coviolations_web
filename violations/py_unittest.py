import re
from django.template.loader import render_to_string
from tasks.const import STATUS_SUCCESS, STATUS_FAILED
from .base import library


@library.register('py_unittest')
def py_unittest_violation(data):
    """Python unittest violation parser"""
    lines = data['raw'].split('\n')
    line = ''
    while len(lines) and not line.startswith('Ran'):
        line = lines.pop(0)

    summary = line
    status = lines.pop(1)

    data['status'] =\
        STATUS_SUCCESS if status.find('OK') == 0 else STATUS_FAILED

    data['preview'] = render_to_string('violations/py_tests/preview.html', {
        'summary': summary,
        'status': status,
    })
    data['prepared'] = render_to_string('violations/py_tests/prepared.html', {
        'raw': data['raw'],
    })

    plot = {'failures': 0, 'errors': 0}
    fail_match = re.match(r'.*failures=(\d*).*', status)
    if fail_match:
        plot['failures'] = int(fail_match.groups()[0])
    error_match = re.match(r'.*errors=(\d*).*', status)
    if error_match:
        plot['errors'] = int(error_match.groups()[0])
    total_match = re.match(r'Ran (\d*) tests .*', summary)
    if total_match:
        plot['test_count'] = int(total_match.groups()[0])

    data['plot'] = plot
    return data
