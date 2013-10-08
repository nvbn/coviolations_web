import sure
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
        result['status'].should.be.equal(STATUS_SUCCESS)
        result['plot']['tests'].should.be.equal(34)
        result['plot']['pass'].should.be.equal(34)
        result['plot']['fail'].should.be.equal(0)

    def test_fail(self):
        data = {
            'raw': get_content('testem_fail.out'),
        }
        result = testem_violation(data)
        result['status'].should.be.equal(STATUS_FAILED)
        result['plot']['tests'].should.be.equal(35)
        result['plot']['pass'].should.be.equal(34)
        result['plot']['fail'].should.be.equal(1)
