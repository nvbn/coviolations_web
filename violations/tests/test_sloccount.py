import sure
from django.test import TestCase
from tasks.const import STATUS_SUCCESS
from ..sloccount import sloccount_violation
from .base import get_content


class SloccountViolationCase(TestCase):
    """Sloccount violation case"""

    def test_result(self):
        """Test sloccount violation result"""
        data = {
            'raw': get_content('sloccount.out'),
        }
        result = sloccount_violation(data)
        result['status'].should.be.equal(STATUS_SUCCESS)
        result['plot']['total'].should.be.equal(2629)
