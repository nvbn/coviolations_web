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

    def test_issue_1_out(self):
        """Test out of #1 issue"""
        data = {'raw': get_content('coverage_issue_1.out')}
        result = coverage_violation(data)
        self.assertEqual(result['status'], STATUS_SUCCESS)
        self.assertEqual(result['plot']['cover'], 100)
