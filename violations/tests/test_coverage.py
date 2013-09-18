from django.test import TestCase
from tasks.const import STATUS_SUCCESS
from ..coverage import coverage_violation
from .base import get_content


class CoverageViolationCase(TestCase):
    """Coverage violation case"""

    def test_result(self):
        """Test coverage violation result"""
        data = {'raw': get_content('coverage.out')}
        result = coverage_violation(data)
        self.assertEqual(result['status'], STATUS_SUCCESS)
        self.assertEqual(result['plot']['cover'], 86)
