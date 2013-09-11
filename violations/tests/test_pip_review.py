from django.test import TestCase
from tasks.const import STATUS_SUCCESS, STATUS_FAILED
from ..pip_review import pip_review_violation
from .base import get_content


class PipReviewViolationCase(TestCase):
    """Pip review violation case"""

    def test_success(self):
        """Test success result"""
        data = {'raw': ''}
        result = pip_review_violation(data)
        self.assertEqual(result['status'], STATUS_SUCCESS)
        self.assertEqual(result['plot']['outdated'], 0)

    def test_fail_on_real(self):
        """Test fail on real data"""
        data = {
            'raw': get_content('pip_review.out'),
        }
        result = pip_review_violation(data)
        self.assertEqual(result['status'], STATUS_FAILED)
        self.assertEqual(result['plot']['outdated'], 12)
