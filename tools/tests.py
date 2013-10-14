from mock import MagicMock
from django.contrib.auth.models import User


class MockGithubMixin(object):
    """Mock github calls mixin"""

    def setUp(self):
        self._mock_github_call()

    def _mock_github_call(self):
        """Mock github call"""
        self._orig_github = User.github
        User.github = MagicMock()

    def tearDown(self):
        User.github = self._orig_github

    def _create_repo(self, n):
        """Create repo"""
        repo = MagicMock(
            html_url='http://test{}.com'.format(n),
            organization=None,
            private=False,
        )
        repo.full_name = 'project {}'.format(n)
        return repo
