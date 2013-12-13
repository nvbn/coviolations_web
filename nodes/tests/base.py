from mock import MagicMock
from .. import models


class WithKeysMixin(object):
    """With project keys misin"""

    def setUp(self):
        self._mock_project()

    def _mock_project(self):
        """Mock project github repo"""
        self._orig_repo = models.Project.repo
        models.Project.repo = MagicMock()

    def tearDown(self):
        models.Project.repo = self._orig_repo
