from django.template.loader import render_to_string
from tasks.const import STATUS_SUCCESS
from .base import library


@library.register('sloccount')
def sloccount_violation(data):
    """PEP8 violation parser"""
    lines = data['raw'].split('\n')
    langs = {}
    line = ''
    total = 0
    while len(lines):
        if line.find("Totals grouped by language (dominant language first):") == 0:
            line = lines.pop(0)

            while len(line) != 0:
                lang, count, per = line.split()
                langs[lang[:-1]] = count
                line = lines.pop(0)

        if line.find('Total Physical Source Lines of Code') == 0:
            total = line.split('=')[1].strip()

        if len(lines):
            line = lines.pop(0)

    data['status'] = STATUS_SUCCESS

    data['preview'] = render_to_string('violations/sloccount/preview.html', {
        'total': total,
    })
    data['prepared'] = render_to_string('violations/sloccount/prepared.html', {
        'total': total,
        'langs': langs,
    })
    data['plot'] = {
        'total': total,
    }
    return data
