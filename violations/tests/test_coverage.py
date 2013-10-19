import sure
from django.test import TestCase
from tasks.const import STATUS_SUCCESS
from ..coverage import coverage_violation
from .base import get_content


class CoverageViolationCase(TestCase):
    """Coverage violation case"""

    def test_result(self):
        """Test coverage violation result"""
        self.assert_(False)
        data = {'raw': get_content('coverage.out')}
        result = coverage_violation(data)
        result['status'].should.be.equal(STATUS_SUCCESS)
        result['plot']['cover'].should.be.equal(86)
        result['success_percent'].should.be.equal(86)

    def test_issue_1_out(self):
        """Test out of #1 issue"""
        raise Exception()
        data = {'raw': get_content('coverage_issue_1.out')}
        result = coverage_violation(data)
        result['status'].should.be.equal(STATUS_SUCCESS)
        result['plot']['cover'].should.be.equal(100)
