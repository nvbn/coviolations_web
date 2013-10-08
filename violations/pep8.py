from django.template.loader import render_to_string
from tasks.const import STATUS_SUCCESS, STATUS_FAILED
from .base import library


def _prepare_source_line(line):
    """Prepare source line"""
    source, violation = line.split(': ')
    file_name, line, symbol = source.split(':')
    return file_name, line, symbol, violation


def _prepare_lines_for_comments(lines):
    """Prepare lines to comments"""
    for line in lines:
        try:
            yield {
                'body': line[3],
                'line': int(line[1]),
                'path': line[0][2:] if line[0].startswith('./') else line[0],
                'position': int(line[2]),
            }
        except Exception:
            pass


@library.register('pep8')
def pep8_violation(data):
    """PEP8 violation parser

    :param data: task data
    :type data: dict
    :returns: dict
    """
    count = len(data['raw'].split('\n')) - 1
    data['status'] = STATUS_SUCCESS if count == 0 else STATUS_FAILED
    data['preview'] = render_to_string('violations/pep8/preview.html', {
        'count': count,
    })
    lines = map(_prepare_source_line, data['raw'].split('\n')[:-1])
    data['prepared'] = render_to_string('violations/pep8/prepared.html', {
        'violations': lines,
    })
    if not data.get('nocomment'):
        data['lines'] = list(_prepare_lines_for_comments(lines))
    data['plot'] = {
        'count': count,
    }
    return data
