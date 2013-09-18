from django.test import TestCase
from tasks.const import STATUS_SUCCESS, STATUS_FAILED
from ..testem import testem_violation
from .base import get_content


class TestemViolationCase(TestCase):
    """Testem violation case"""

    def test_success(self):
        """Test success result"""
        data = {
            'raw': get_content('testem_success.out'),
        }
        result = testem_violation(data)
        self.assertEqual(result['status'], STATUS_SUCCESS)
        self.assertEqual(result['plot']['tests'], 34)
        self.assertEqual(result['plot']['pass'], 34)
        self.assertEqual(result['plot']['fail'], 0)

    def test_fail(self):
        data = {
            'raw': get_content('testem_fail.out'),
        }
        result = testem_violation(data)
        self.assertEqual(result['status'], STATUS_FAILED)
        self.assertEqual(result['plot']['tests'], 35)
        self.assertEqual(result['plot']['pass'], 34)
        self.assertEqual(result['plot']['fail'], 1)
