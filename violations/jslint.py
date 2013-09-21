from django.template.loader import render_to_string
from tasks.const import STATUS_SUCCESS, STATUS_FAILED
from .base import library


@library.register('jslint')
def jslint_violation(data):
    """jslint violation parser

    :param data: task data
    :type data: dict
    :returns: dict
    """
    stripped = [
        line.strip() if 0 <= line.find('#') < 5 else line
        for line in data['raw'].split('\n') if line
    ]
    count = len([line.find('#') == 0 for line in stripped])
    data['status'] = STATUS_SUCCESS if count == 0 else STATUS_FAILED
    data['preview'] = render_to_string('violations/jslint/preview.html', {
        'count': count,
    })

    files = []
    for line in stripped:
        if line[0] not in ('#', ' '):
            if 'is OK.' in line:
                files.append([line.split(' ')[0], True, []])
            else:
                files.append([line, False, []])
        elif line[0] == '#':
            files[-1][2] = [line, []]
        elif line.find('    ') == 0:
            files[-1][2][1].append(line.strip())

    data['prepared'] = render_to_string('violations/jslint/prepared.html', {
        'violations': files,
    })
    data['plot'] = {
        'count': count,
    }
    return data
