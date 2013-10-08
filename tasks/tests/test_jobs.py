import sure
from mock import MagicMock
from django.test import TestCase
from django_rq import get_worker
from tools.mongo import MongoFlushMixin
from projects.tests.factories import ProjectFactory
from .. import jobs, models, const


class CreateTaskJobCase(MongoFlushMixin, TestCase):
    """Create task job case"""
    mongo_flush = ['tasks']

    def setUp(self):
        super(CreateTaskJobCase, self).setUp()
        self._mock_prepare_violations()
        self._mock_fill_task()
        self._create_task()

    def _mock_prepare_violations(self):
        """Mock prepare violations"""
        self._orig_prepare_violations = jobs.prepare_violations
        jobs.prepare_violations = MagicMock()

    def _mock_fill_task(self):
        """Mock fill task from github"""
        self._orig_fill_task = jobs._fill_task_from_github
        jobs._fill_task_from_github = MagicMock()

    def tearDown(self):
        jobs.prepare_violations = self._orig_prepare_violations
        jobs._fill_task_from_github = self._orig_fill_task

    def _create_task(self):
        """Create task"""
        ProjectFactory(name='test')
        data = {
            'service': {
                'name': 'dummy',
            },
            'project': 'test',
            'branch': 'develop',
            'commit': 'asdfg',
            'violations': [
                {'name': 'dummy', 'raw': '1'},
            ]
        }
        jobs.create_task(models.Tasks.save(data))
        get_worker().work(burst=True)

    def test_create(self):
        """Test create"""
        models.Tasks.count().should.be.equal(1)

    def test_propagating(self):
        """Test propagating to prepare violations"""
        task = models.Tasks.find_one()
        jobs.prepare_violations.delay.assert_called_once_with(task['_id'])


class PrepareViolationsJobCase(MongoFlushMixin, TestCase):
    """Prepare violations job case"""
    mongo_flush = ['tasks']

    def setUp(self):
        super(PrepareViolationsJobCase, self).setUp()
        self._mock_mark_commit()
        self._mock_comment_lines()

    def _mock_mark_commit(self):
        """Mock mark_commit_with_status job"""
        self._orig_mark_commit = jobs.mark_commit_with_status
        jobs.mark_commit_with_status = MagicMock()

    def _mock_comment_lines(self):
        """Mock comment lines"""
        self._orig_comment_lines = jobs.comment_lines
        jobs.comment_lines = MagicMock()

    def tearDown(self):
        jobs.mark_commit_with_status = self._orig_mark_commit
        jobs.comment_lines = self._orig_comment_lines

    def test_prepare(self):
        """Test prepare"""
        tasks = [{
            'violations': [
                {
                    'name': 'dummy',
                    'raw': 'test{}'.format(n),
                },
            ],
            'owner_id': 1,
            'project': 'test',
        } for n in range(10)]

        for task in tasks:
            task_id = models.Tasks.save(task)
            jobs.prepare_violations(task_id)
        get_worker().work(burst=True)
        sum(
            [len(task['violations']) for task in models.Tasks.find()]
        ).should.be.equal(10)

    def test_not_fail_all(self):
        """Not fail all if fail one"""
        task = {
            'violations': [
                {'name': 'dummy', 'raw': 'rew'},
                {'name': 'dummy!!!', 'raw': 'rwww'},
                {'name': 'dummy', 'raw': 'row'},
            ],
            'owner_id': 1,
            'project': 'test',
        }
        task_id = models.Tasks.insert(task)
        jobs.prepare_violations(task_id)
        get_worker().work(burst=True)

        task = models.Tasks.find_one(task_id)
        [
            violation for violation in task['violations']
            if violation['status'] is const.STATUS_SUCCESS
        ].should.have.length_of(2)
        [
            violation for violation in task['violations']
            if violation['status'] is const.STATUS_FAILED
        ].should.have.length_of(1)

    def test_nofail_argument(self):
        """Test nofail argument"""
        task = {
            'violations': [
                {'name': 'dummy!!!', 'raw': 'rwww', 'nofail': True},
            ],
            'owner_id': 1,
            'project': 'test',
        }
        task_id = models.Tasks.insert(task)
        jobs.prepare_violations(task_id)
        get_worker().work(burst=True)

        task = models.Tasks.find_one(task_id)
        task['violations'][0]['status'].should.be.equal(const.STATUS_SUCCESS)

    def test_mark_commit_with_status_called(self):
        """Test mark commit with status called"""
        task = {
            'violations': [],
            'owner_id': 1,
            'project': 'test',
        }
        task_id = models.Tasks.insert(task)
        jobs.prepare_violations(task_id)
        get_worker().work(burst=True)
        jobs.mark_commit_with_status.delay.call_count.should.be.equal(1)

    def test_comment_lines_called(self):
        """Test comment lines called"""
        task = {
            'violations': [],
            'owner_id': 1,
            'project': 'test',
        }
        task_id = models.Tasks.insert(task)
        jobs.prepare_violations(task_id)
        get_worker().work(burst=True)
        jobs.comment_lines.delay.call_count.should.be.equal(1)


class CommentPullRequestJob(MongoFlushMixin, TestCase):
    """Comment pull request job case"""
    mongo_flush = ['tasks']

    def setUp(self):
        super(CommentPullRequestJob, self).setUp()
        self._orig_github = jobs.Github
        jobs.Github = MagicMock()

    def tearDown(self):
        jobs.Github = self._orig_github

    def test_comment(self):
        """Test comment"""
        ProjectFactory(name='test')
        task = {
            'project': 'test',
            'pull_request_id': 2,
            'violations': [
                {'name': 'dummy', 'preview': 'rew'},
                {'name': 'dummy!!!', 'raw': 'rwww'},
                {'name': 'dummy', 'raw': 'row'},
            ],
            'commit': {'hash': 'test'},
        }
        jobs.comment_pull_request.when\
            .called_with(models.Tasks.save(task))\
            .should_not.throw(Exception)


class MarkCommitWithStatusCase(MongoFlushMixin, TestCase):
    """Test mark commit with status job"""
    mongo_flush = ['tasks']

    def setUp(self):
        super(MarkCommitWithStatusCase, self).setUp()
        self._mock_github()
        self._mock_make_https()
        ProjectFactory(name='test')

    def _mock_github(self):
        """Mock github"""
        jobs.Project._repo = MagicMock()

    def _mock_make_https(self):
        """Mock make https"""
        self._orig_make_https = jobs.make_https
        jobs.make_https = MagicMock(return_value='test')

    def tearDown(self):
        jobs.make_https = self._orig_make_https
        del jobs.Project._repo

    def test_mark_as_success(self):
        """Test mark as success"""
        task = {
            'project': 'test',
            'violations': [],
            'commit': {'hash': 'test'},
            'status': const.STATUS_SUCCESS,
        }
        jobs.mark_commit_with_status(models.Tasks.save(task))
        jobs.Project._repo.get_commit.return_value\
            .create_status.assert_called_once_with(
                'success', 'test',
                'coviolations.io mark commit as safe'
            )

    def test_mark_as_failed(self):
        """Test mark as failed"""
        task = {
            'project': 'test',
            'violations': [],
            'commit': {'hash': 'test'},
            'status': const.STATUS_FAILED,
        }
        jobs.mark_commit_with_status(models.Tasks.save(task))
        jobs.Project._repo.get_commit.return_value\
            .create_status.assert_called_once_with(
                'failure', 'test',
                'coviolations.io mark commit as unsafe'
            )


class CommentLinesCase(MongoFlushMixin, TestCase):
    """Comment lines case"""
    mongo_flush = ['tasks']

    def setUp(self):
        super(CommentLinesCase, self).setUp()
        self._mock_github()
        ProjectFactory(name='test')

    def _mock_github(self):
        """Mock github api"""
        self._orig_github = jobs.Github
        jobs.Github = MagicMock()

    def tearDown(self):
        jobs.Github = self._orig_github

    def test_not_comment_without_lines(self):
        """Test not comment without lines"""
        task = {
            'project': 'test',
            'violations': [{'name': 'dummy'}],
            'commit': {'hash': 'test'},
        }
        jobs.comment_lines(models.Tasks.save(task))
        jobs.Github.call_count.should.be.equal(0)

    def test_create_comments(self):
        """Test create comments"""
        task = {
            'project': 'test',
            'violations': [
                {
                    'name': 'dummy', 'lines': [
                        {
                            'body': 'test', 'line': 1,
                            'path': 'test', 'position': 12
                        },
                    ] * 2,
                }
            ] * 2,
            'commit': {'hash': 'test'},
        }
        jobs.comment_lines(models.Tasks.save(task))
        jobs.Github.return_value.get_repo.return_value\
            .get_commit.return_value.create_comment\
            .call_count.should.be.equal(4)
