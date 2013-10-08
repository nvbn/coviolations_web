import sure
from django.test import TestCase
from tasks.const import STATUS_SUCCESS, STATUS_FAILED
from ..jslint import jslint_violation
from .base import get_content


class JSlintViolationCase(TestCase):
    """JSlint violation case"""

    def test_success(self):
        """Test success result"""
        data = {'raw': ''}
        result = jslint_violation(data)
        result['status'].should.be.equal(STATUS_SUCCESS)
        result['plot']['count'].should.be.equal(0)

    def test_fail_on_real(self):
        """Test fail on real data"""
        data = {
            'raw': get_content('jslint.out'),
        }
        result = jslint_violation(data)
        result['status'].should.be.equal(STATUS_FAILED)
        result['plot']['count'].should.be.equal(131)
