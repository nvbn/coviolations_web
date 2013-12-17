import sure
from mock import MagicMock
from django.core.management import call_command
from django.test import TestCase
from ..management.commands import create_images


class CreateImagesCase(TestCase):
    """Create images case"""

    def setUp(self):
        self._mock_connect_to_node()
        self._mock_logger()
        self._mock_iterate_images()

    def _mock_connect_to_node(self):
        """Mock connect_to_node"""
        self._orig_connect_to_node = create_images.connect_to_node
        create_images.connect_to_node = MagicMock()

    def _mock_logger(self):
        """Mock logger"""
        self._orig_logger = create_images.logger
        create_images.logger = MagicMock()

    def _mock_iterate_images(self):
        """Mock iterate images"""
        self._orig_iterate_images = create_images.Command._iterate_images
        create_images.Command._iterate_images = MagicMock(return_value=[])

    def tearDown(self):
        create_images.connect_to_node = self._orig_connect_to_node
        create_images.logger = self._orig_logger
        create_images.Command._iterate_images = self._orig_iterate_images

    def test_create_raw_image(self):
        """Test create raw image"""
        node = MagicMock()
        create_images.connect_to_node.return_value.__enter__.\
            return_value = node
        call_command('create_images')
        node.save_image.assert_called_once_with('raw')

    def test_create_other_images(self):
        """Test create other images"""
        node = MagicMock()
        create_images.connect_to_node.return_value.__enter__.\
            return_value = node
        create_images.Command._iterate_images.return_value = ['cat', 'dog']
        call_command('create_images')
        node.save_image.call_count.should.be.equal(3)
