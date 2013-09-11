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
        self.assertEqual(result['status'], STATUS_SUCCESS)
        self.assertEqual(result['plot']['failures'], 0)
        self.assertEqual(result['plot']['errors'], 0)
        self.assertEqual(result['plot']['test_count'], 50)

    def test_fail(self):
        """Test fail result"""
        data = {
            'raw': get_content('py_unittest_fail.out'),
        }
        result = py_unittest_violation(data)
        self.assertEqual(result['status'], STATUS_FAILED)
        self.assertEqual(result['plot']['failures'], 2)
        self.assertEqual(result['plot']['errors'], 1)
        self.assertEqual(result['plot']['test_count'], 50)
