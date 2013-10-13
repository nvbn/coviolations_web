import sure
from django.test import TestCase
from tasks.const import STATUS_SUCCESS, STATUS_FAILED
from ..py_unittest import py_unittest_violation
from .base import get_content


class PyUnittestViolationCase(TestCase):
    """Python unittest violation case"""

    def test_success(self):
        """Test success result"""
        data = {
            'raw': get_content('py_unittest_success.out'),
        }
        result = py_unittest_violation(data)
        result['status'].should.be.equal(STATUS_SUCCESS)
        result['plot']['failures'].should.be.equal(0)
        result['plot']['errors'].should.be.equal(0)
        result['plot']['test_count'].should.be.equal(50)
        result['success_percent'].should.be.equal(100)

    def test_fail(self):
        """Test fail result"""
        data = {
            'raw': get_content('py_unittest_fail.out'),
        }
        result = py_unittest_violation(data)
        result['status'].should.be.equal(STATUS_FAILED)
        result['plot']['failures'].should.be.equal(2)
        result['plot']['errors'].should.be.equal(1)
        result['plot']['test_count'].should.be.equal(50)
        result['success_percent'].should.be.equal(94)
