from mock import MagicMock
from django.contrib.auth.models import User
from projects.models import Project


class MockGithubMixin(object):
    """Mock github calls mixin"""

    def setUp(self):
        super(MockGithubMixin, self).setUp()
        self._mock_github_call()

    def _mock_github_call(self):
        """Mock github call"""
        self._orig_github = User.github
        User.github = MagicMock()
        Project._repo = MagicMock()
        Project._repo.get_hooks.return_value = []

    def tearDown(self):
        User.github = self._orig_github
        del Project._repo

    def _create_repo(self, n):
        """Create repo"""
        repo = MagicMock(
            html_url='http://test{}.com'.format(n),
            organization=None,
            private=False,
        )
        repo.full_name = 'project {}'.format(n)
        repo.get_hooks.return_value = []
        return repo
