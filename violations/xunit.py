from BeautifulSoup import BeautifulStoneSoup
from django.template.loader import render_to_string
from tasks.const import STATUS_SUCCESS, STATUS_FAILED
from .base import library


def _get_status(case):
    """Get case status"""
    if case.find('error'):
        return 'ERROR'
    elif case.find('failure'):
        return 'FAIL'
    else:
        return 'OK'


def _get_output(case):
    """Get case output"""
    if case.find('error'):
        return case.find('error').text
    elif case.find('failure'):
        return case.find('failure').text
    else:
        return ''


def _prepare_test_case(case):
    """Prepare test case"""
    return {
        'name': case['name'],
        'class_name': case['classname'],
        'status': _get_status(case),
        'output': _get_output(case),
    }


@library.register('xunit')
def xunit_violation(data):
    """XUnit violation"""
    soup = BeautifulStoneSoup(data['raw'])
    cases = soup.findAll('testcase')
    cases_count = len(cases)
    errors_count = len(soup.findAll('error'))
    failures_count = len(soup.findAll('failure'))

    data['preview'] = render_to_string('violations/xunit/preview.html', {
        'tests': cases_count,
        'pass': cases_count - errors_count - failures_count,
        'fail': errors_count + failures_count,
    })

    data['status'] = STATUS_SUCCESS\
        if (errors_count + failures_count) == 0 else STATUS_FAILED

    data['plot'] = {
        'tests': cases_count,
        'pass': cases_count - errors_count - failures_count,
        'fail': errors_count + failures_count,
    }

    data['prepared'] = render_to_string('violations/xunit/prepared.html', {
        'cases': map(_prepare_test_case, cases),
        'tests': cases_count,
        'failures': failures_count,
        'errors': errors_count,
    })

    failed_percent = (errors_count + failures_count) * 100 / cases_count
    data['success_percent'] = 100 - failed_percent
    return data
