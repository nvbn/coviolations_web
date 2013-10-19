import re
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
    data['lines'] = []

    files = []
    for line in stripped:
        if line[0] not in ('#', ' '):
            if 'is OK.' in line:
                files.append([line.split(' ')[0], True, []])
            else:
                files.append([line, False, []])
        elif line[0] == '#':
            files[-1][2].append([line, []])
        elif line.find('    ') == 0:
            files[-1][2][-1][1].append(line.strip())

        line_match = re.match(r'.*\/\/ Line (\d+), Pos (\d+)', line)
        if line_match:
            line, position = line_match.groups()
            error_title = re.match(
                r'#\d+ (.*)', files[-1][2][-1][0],
            ).groups()[0]
            data['lines'].append({
                'body': error_title,
                'line': int(line),
                'path': files[-1][0],
                'position': int(position),
            })

    data['prepared'] = render_to_string('violations/jslint/prepared.html', {
        'violations': files,
    })
    data['plot'] = {
        'count': count,
    }
    return data
