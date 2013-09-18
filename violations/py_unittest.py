import re
from django.template.loader import render_to_string
from tasks.const import STATUS_SUCCESS, STATUS_FAILED
from .base import library


@library.register('py_unittest')
def py_unittest_violation(data):
    """Python unittest violation parser

    :param data: task data
    :type data: dict
    :returns: dict
    """
    lines = data['raw'].split('\n')
    line = ''
    fails = []
    fail = {}
    traceback_started = False

    while len(lines) and not line.startswith('Ran'):
        if line.startswith('ERROR') or line.startswith('FAIL'):
            fail['status'], fail['test_name'] = line.split(': ')
        elif fail.get('status'):
            if len(line) == 0 and traceback_started:
                fails.append(fail)
                fail = {}
                traceback_started = False
            elif all(map(lambda symbol: symbol == '-', line)):
                traceback_started = True
            elif not traceback_started:
                fail['description'] = fail.get('description', []) + [line]
            elif traceback_started:
                fail['traceback'] = fail.get('traceback', []) + [line]

        line = lines.pop(0)

    summary = line
    status = lines.pop(1)

    data['status'] =\
        STATUS_SUCCESS if status.find('OK') == 0 else STATUS_FAILED

    data['preview'] = render_to_string('violations/py_tests/preview.html', {
        'summary': summary,
        'status': status,
    })

    prepared_data = {
        'fails': fails,
        'failures': 0,
        'errors': 0,
        'total': 0,
    }

    plot = {'failures': 0, 'errors': 0}
    fail_match = re.match(r'.*failures=(\d*).*', status)
    if fail_match:
        plot['failures'] = int(fail_match.groups()[0])
        prepared_data['failures'] = int(fail_match.groups()[0])
    error_match = re.match(r'.*errors=(\d*).*', status)
    if error_match:
        plot['errors'] = int(error_match.groups()[0])
        prepared_data['errors'] = int(error_match.groups()[0])
    total_match = re.match(r'Ran (\d*) tests .*', summary)
    if total_match:
        plot['test_count'] = int(total_match.groups()[0])
        prepared_data['total'] = int(total_match.groups()[0])

    data['prepared'] = render_to_string(
        'violations/py_tests/prepared.html', prepared_data,
    )

    data['plot'] = plot
    return data
