import sure
from mock import MagicMock
from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
from projects.tests.factories import ProjectFactory
from projects.models import Project
from ..exceptions import TaskAlreadyPerformed
from .. import models
from . import factories
from .base import WithKeysMixin


class ProjectKeysCase(WithKeysMixin, TestCase):
    """Project keys case"""

    def test_generate_keys_on_save(self):
        """Test generate keys on save"""
        keys = factories.ProjectKeysFactory()
        keys.private_key.should.be.ok
        keys.public_key.should.be.ok

    def test_register_key_on_github(self):
        """Test register key on github"""
        ProjectFactory(run_here=True)
        models.Project.repo.create_key.call_count.should.be.equal(1)

    def test_file_paths(self):
        """Test file paths"""
        keys = factories.ProjectKeysFactory()
        keys.file_paths.should.be.ok

    def test_create_when_project_enabled(self):
        """Test create keys when project enabled"""
        project = ProjectFactory.create(run_here=True)
        models.ProjectKeys.objects.filter(project=project).exists()\
            .should.be.true

    def test_not_create_duplicated_keys_on_save(self):
        """Test not create duplicated keys on save"""
        project = ProjectFactory.create(run_here=True)
        project.save()
        models.ProjectKeys.objects.filter(project=project).count()\
            .should.be.equal(1)


class ProjectPostSaveCase(WithKeysMixin, TestCase):
    """Project post_save case"""

    def test_add_hook_if_need(self):
        """Test add hook if need"""
        project = ProjectFactory.create(run_here=True)
        project.repo.create_hook.call_count.should.be.equal(1)

    def test_remove_hook_if_need(self):
        """Test remove hook if need"""
        project = ProjectFactory.create(run_here=False)
        hook = MagicMock()
        hook.name = settings.GITHUB_HOOK_NAME
        project.repo.get_hooks.return_value = [hook]
        project.save()
        hook.delete.call_count.should.be.equal(1)


class NodeTaskCase(WithKeysMixin, TestCase):
    """Node task case"""

    def setUp(self):
        super(NodeTaskCase, self).setUp()
        self._mock_connect_to_node()
        self._mock_get_covio()
        self._mock_user_github()

    def _mock_connect_to_node(self):
        """Mock connect to node"""
        self._orig_connect_to_node = models.connect_to_node
        models.connect_to_node = MagicMock()
        self.node = MagicMock(id='node_id')
        self.node.execute.return_value = MagicMock(
            script='in', stdout='out', stderr='err',
        )
        models.connect_to_node.return_value.__enter__.return_value = self.node

    def _mock_get_covio(self):
        """Mock get_covio"""
        self._orig_get_covio = models.Project.get_covio
        models.Project.get_covio = MagicMock(return_value={'image': 'raw'})

    def _mock_user_github(self):
        """Mock user github"""
        self._orig_github_token = User.github_token
        User.github_token = 'token'

    def _create_task(self, **kwargs):
        """Create NodeTask and keys"""
        defaults = {
            'project__run_here': True,
        }
        defaults.update(kwargs)
        task = factories.NodeTaskFactory(**defaults)
        return task

    def tearDown(self):
        super(NodeTaskCase, self).tearDown()
        models.connect_to_node = self._orig_connect_to_node
        models.Project.get_covio = self._orig_get_covio
        User.github_token = property(self._orig_github_token)

    def test_perform_task(self):
        """Test perform task"""
        task = self._create_task()
        task.perform()
        task.state.should.be.equal(models.NodeTask.STATE_FINISHED)

    def test_set_input_and_outputs(self):
        """Test set inputs and outputs"""
        task = self._create_task()
        task.perform()
        task.input.should.be.equal('in')
        task.stdout.should.be.equal('out')
        task.stderr.should.be.equal('err')

    def test_perform_only_new(self):
        """Test perform only new tasks"""
        task = self._create_task(state=models.NodeTask.STATE_ACTIVE)
        task.perform.when.called_with().should.throw(TaskAlreadyPerformed)

    def test_set_failed_state_when_failed(self):
        """Test set failed state when failed"""
        self.node.execute.side_effect = Exception()
        task = self._create_task()
        task.perform()
        task.state.should.be.equal(models.NodeTask.STATE_FAILED)
