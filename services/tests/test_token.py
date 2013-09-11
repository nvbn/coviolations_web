from testfixtures import LogCapture
from django.test import TestCase
from tools.mongo import MongoFlushMixin
from projects.tests.factories import ProjectFactory
from tasks.models import Tasks
from ..token import token_service


class TokenServiceCase(MongoFlushMixin, TestCase):
    """Token service case"""
    mongo_flush = ['tasks']

    def setUp(self):
        super(TokenServiceCase, self).setUp()
        self.project = ProjectFactory(name='test')

    def test_fail_with_wrong_token(self):
        """Test fail with wrong token"""
        task_id = Tasks.save({
            'project': 'test',
            'service': {
                'name': 'token',
                'token': self.project.token + '!',
            }
        })
        data = Tasks.find_one(task_id)
        with LogCapture() as log_capture:
            self.assertIsNone(token_service(data))
            self.assertIn('ERROR', list(log_capture.actual())[0])
        self.assertEqual(Tasks.find({}).count(), 0)

    def test_fail_with_wrong_project(self):
        """Test fail with wrong project"""
        task_id = Tasks.save({
            'project': 'test',
            'service': {
                'name': 'token',
                'token': ProjectFactory().token,
            }
        })
        data = Tasks.find_one(task_id)
        with LogCapture() as log_capture:
            self.assertIsNone(token_service(data))
            self.assertIn('ERROR', list(log_capture.actual())[0])
        self.assertEqual(Tasks.find({}).count(), 0)

    def test_success(self):
        """Test success"""
        task_id = Tasks.save({
            'project': 'test',
            'service': {
                'name': 'token',
                'token': self.project.token,
            }
        })
        data = Tasks.find_one(task_id)
        self.assertEqual(
            task_id, token_service(data),
        )
