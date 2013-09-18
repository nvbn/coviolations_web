from django.template.loader import render_to_string
from tasks.const import STATUS_SUCCESS, STATUS_FAILED
from .base import library


def _prepare_source_line(line):
    """Prepare source line"""
    source, violation = line.split(': ')
    file_name, line, symbol = source.split(':')
    return file_name, line, symbol, violation


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
    data['prepared'] = render_to_string('violations/pep8/prepared.html', {
        'violations': map(_prepare_source_line, data['raw'].split('\n')[:-1]),
    })
    data['plot'] = {
        'count': count,
    }
    return data
