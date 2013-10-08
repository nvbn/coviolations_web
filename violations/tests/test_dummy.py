import sure
from django.test import TestCase
from tasks.const import STATUS_SUCCESS
from ..dummy import dummy_violation


class DummyViolationCase(TestCase):
    """Dummy violation case"""

    def test_result(self):
        """Test dummy violation result"""
        data = {'raw': ''}
        result = dummy_violation(data)
        result['status'].should.be.equal(STATUS_SUCCESS)
