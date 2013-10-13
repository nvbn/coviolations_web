from django.template.loader import render_to_string
from tasks.const import STATUS_SUCCESS
from .base import library


@library.register('coverage')
def coverage_violation(data):
    """Coverage violation parser

    :param data: task data
    :type data: dict
    :returns: dict
    """
    data['status'] = STATUS_SUCCESS
    line = data['raw'].split('\n')[-2]
    statements, miss, cover = [
        part for part in line.split(' ')
        if len(part) > 0 and 'TOTAL' not in part
    ]
    each_file = [
        filter(len, line.split(' '))
        for line in data['raw'].split('\n')[2:-3]
    ]
    data['preview'] = render_to_string('violations/coverage/preview.html', {
        'statements': statements,
        'miss': miss,
        'cover': cover,
    })
    data['prepared'] = render_to_string('violations/coverage/prepared.html', {
        'statements': statements,
        'miss': miss,
        'cover': cover,
        'each_file': each_file,
    })
    data['plot'] = {
        'cover': int(cover[:-1]),
    }
    data['success_percent'] = int(cover[:-1])
    return data
