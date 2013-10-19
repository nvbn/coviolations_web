import sure
from django.test import TestCase
from tasks.const import STATUS_SUCCESS, STATUS_FAILED
from ..xunit import xunit_violation
from .base import get_content


class XUnitViolationCase(TestCase):
    """XUnit violation case"""

    def test_success(self):
        """Test success"""
        data = {
            'raw': get_content('xunit_success.out'),
        }
        result = xunit_violation(data)
        result['status'].should.be.equal(STATUS_SUCCESS)
        result['success_percent'].should.be.equal(100)
        result['plot']['tests'].should.be.equal(11)

    def test_fail(self):
        """Test fail"""
        data = {
            'raw': get_content('xunit_fail.out'),
        }
        result = xunit_violation(data)
        result['status'].should.be.equal(STATUS_FAILED)
        result['success_percent'].should.be.equal(73)
        result['plot']['fail'].should.be.equal(3)
