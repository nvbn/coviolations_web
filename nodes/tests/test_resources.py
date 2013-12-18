import sure
from mock import MagicMock
from tastypie.test import ResourceTestCase
from tools.tests import MockGithubMixin
from projects.tests.factories import ProjectFactory
from ..models import NodeTask
from .. import resources


class NodeTaskHookResourceCase(MockGithubMixin, ResourceTestCase):
    """Test case for node tasks"""

    def setUp(self):
        super(NodeTaskHookResourceCase, self).setUp()
        self._mock_job()
        self._url = '/api/v1/nodes/hook/'
        self._data = {
            "after": "1481a2de7b2a7d02428ad93446ab166be7793fbb",
            "before": "17c497ccc7cca9c2f735aa07e9e3813060ce9a6a",
            "commits": [],
            "ref": "refs/heads/master",
            "repository": {
                "name": "testing",
                "owner": {
                     "email": "lolwut@noway.biz",
                     "name": "octokitty"
                },
            },
        }

    def _mock_job(self):
        """Mock task performing job"""
        self._orig_job = resources.enqueue
        resources.enqueue = MagicMock()

    def tearDown(self):
        super(NodeTaskHookResourceCase, self).tearDown()
        resources.enqueue = self._orig_job

    def test_create_task(self):
        """Test create node task"""
        ProjectFactory(
            name='octokitty/testing',
            run_here=True, is_enabled=True,
        )
        response = self.api_client.post(self._url, data=self._data)
        response.status_code.should.be.equal(201)
        NodeTask.objects.count().should.be.equal(1)

    def test_404_if_project_not_available(self):
        """Test send 404 if project not available"""
        response = self.api_client.post(self._url, data=self._data)
        response.status_code.should.be.equal(404)
