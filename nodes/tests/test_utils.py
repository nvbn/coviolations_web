import sure
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
