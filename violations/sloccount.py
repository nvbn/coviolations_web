from django.template.loader import render_to_string
from tasks.const import STATUS_SUCCESS
from .base import library


@library.register('sloccount')
def sloccount_violation(data):
    """PEP8 violation parser

    :param data: task data
    :type data: dict
    :returns: dict
    """
    lines = data['raw'].split('\n')
    dirs = []
    langs = []
    line = ''
    totals = []
    total_reached = False
    fill_dirs = False

    while len(lines):
        if (
            'SLOC' in line
            and 'Directory' in line
            and 'SLOC-by-Language (Sorted)' in line
        ):
            fill_dirs = True
            line = lines.pop(0)

        if not len(line):
            fill_dirs = False

        if fill_dirs:
            dirs.append(filter(len, line.split(' ')))

        if line.find(
            "Totals grouped by language (dominant language first):"
        ) == 0:
            line = lines.pop(0)

            while len(line) != 0:
                lang, count, per = filter(len, line.split(' '))
                langs.append([lang[:-1], count, per[1:-1]])
                line = lines.pop(0)

        if line.find('Total Physical Source Lines of Code') == 0:
            total_reached = True

        if total_reached and len(line) and line[0] != ' ' and '=' in line:
            totals.append([part.strip() for part in line.split('=')])

        if len(lines):
            line = lines.pop(0)

    data['status'] = STATUS_SUCCESS

    data['preview'] = render_to_string('violations/sloccount/preview.html', {
        'totals': totals,
    })
    data['prepared'] = render_to_string('violations/sloccount/prepared.html', {
        'totals': totals,
        'langs': langs,
        'dirs': dirs,
    })
    data['plot'] = {
        'total': int(totals[0][1].replace(',', '.').replace('.', '')),
    }
    return data
