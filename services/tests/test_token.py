import sure
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
            token_service(data).should.be.none
            list(log_capture.actual())[0].should.contain('ERROR')
        Tasks.find({}).count().should.be.equal(0)

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
            token_service(data).should.be.none
            list(log_capture.actual())[0].should.contain('ERROR')
        Tasks.find({}).count().should.be.equal(0)

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
        task_id.should.be.equal(token_service(data))
