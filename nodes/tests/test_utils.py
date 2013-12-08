from __future__ import print_function
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
