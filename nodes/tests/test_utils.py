import sure
import pyrax
from mock import MagicMock
from django.test import TestCase
from .. import utils


class NodeOutputCase(TestCase):
    """Node output case"""

    def test_stdout_should_be_prepared(self):
        """Test stdout should be prepared"""
        stdout = MagicMock()
        stdout.read.return_value.decode.return_value = 'stdout'
        utils.NodeOutput(stdout, stdout, 'test').stdout.should\
            .be.equal('stdout')

    def test_stderr_should_be_prepared(self):
        """Test stderr should be prepared"""
        stderr = MagicMock()
        stderr.read.return_value.decode.return_value = 'stderr'
        utils.NodeOutput(stderr, stderr, 'test').stderr.should\
            .be.equal('stderr')


class LazyPyraxProxyCase(TestCase):
    """Case for lazy pyrax proxy"""

    def setUp(self):
        self._mock_initialization()

    def _mock_initialization(self):
        """Mock pyrax initialization"""
        self._orig_initialize = utils.LazyPyraxProxy._initialize_pyrax
        utils.LazyPyraxProxy._initialize_pyrax = MagicMock()

    def tearDown(self):
        utils.LazyPyraxProxy._initialize_pyrax = self._orig_initialize

    def test_pyrax_not_initialized_by_default(self):
        """Test pyrax not initialized by default"""
        utils.LazyPyraxProxy()._initialize_pyrax.call_count\
            .should.be.equal(0)

    def test_pyrax_should_be_initialized_only_once(self):
        """Test pyrax should be initialized only once"""
        lazy_pyrax = utils.LazyPyraxProxy()
        lazy_pyrax._initialize_pyrax.side_effect = lambda: setattr(
            lazy_pyrax, '_is_initialized', True,
        )
        lazy_pyrax.pyrax.should.be.ok
        lazy_pyrax.pyrax.should.be.ok
        utils.LazyPyraxProxy()._initialize_pyrax\
            .assert_called_once_with()

    def test_proxy_work(self):
        """Test proxy to pyrax work"""
        utils.LazyPyraxProxy().cloudservers.should.be\
            .equal(pyrax.cloudservers)


class NodeConnectionCase(TestCase):
    """Node connection case"""

    def setUp(self):
        self._mock_pyrax()
        self._mock_logger()
        self._mock_connection()

    def _mock_pyrax(self):
        """Mock pyrax"""
        self._orig_pyrax = utils.pyrax
        utils.pyrax = MagicMock()
        utils.pyrax.utils.random_ascii.return_value = 'server'

    def _mock_logger(self):
        """Mock logger"""
        self._orig_logger = utils.logger
        utils.logger = MagicMock()

    def _mock_connection(self):
        """Mock node connection"""
        self._orig_create_server = utils.NodeConnection._create_server
        utils.NodeConnection._create_server = MagicMock(
            side_effect=lambda: setattr(
                utils.NodeConnection, '_server', MagicMock(name='server'),
            ),
        )
        self._orig_create_ssh = utils.NodeConnection._create_ssh
        utils.NodeConnection._create_ssh = MagicMock(
            side_effect=lambda: setattr(
                utils.NodeConnection, '_client', MagicMock(),
            ),
        )

    def tearDown(self):
        utils.NodeConnection._create_server = self._orig_create_server
        utils.NodeConnection._create_ssh = self._orig_create_ssh
        utils.pyrax = self._orig_pyrax
        utils.logger = self._orig_logger

    def test_create_node(self):
        """Test create node"""
        with utils.connect_to_node() as node:
            node.should.be.ok
