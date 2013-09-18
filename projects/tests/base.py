from mock import MagicMock
from .. import models


class MockGithubMixin(object):
    """Mock github calls mixin"""

    def setUp(self):
        self._mock_github_call()

    def _mock_github_call(self):
        """Mock github call"""
        self._orig_get_remote_projects =\
            models.ProjectManager._get_remote_projects
        models.ProjectManager._get_remote_projects = MagicMock()

    def tearDown(self):
        models.ProjectManager._get_remote_projects =\
            self._orig_get_remote_projects

    def _create_repo(self, n):
        """Create repo"""
        repo = MagicMock(
            url='http://test{}.com'.format(n),
            organization=None,
            private=False,
        )
        repo.full_name = 'project {}'.format(n)
        return repo
