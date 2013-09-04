from django.test import TestCase
from . import factories


class RelationsCase(TestCase):
    """Relations case"""

    def test_project_branch_relations(self):
        """Test project - branch relations"""
        project = factories.ProjectFactory()
        factories.BranchFactory.create_batch(10, project=project)
        self.assertEqual(project.branches.count(), 10)

    def test_branch_commit_relations(self):
        """Test branch - commit relations"""
        branch = factories.BranchFactory()
        factories.CommitFactory.create_batch(10, branch=branch)
        self.assertEqual(branch.commits.count(), 10)
