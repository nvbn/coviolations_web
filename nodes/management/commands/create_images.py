import os
from time import sleep
from django.core.management import BaseCommand
from django.conf import settings
from ...utils import connect_to_node, logger, pyrax


class Command(BaseCommand):
    help = 'create nodes images'

    def handle(self, *args, **kwargs):
        self._root = os.path.join(settings.PROJECT_ROOT, 'nodes', 'images')
        self._create_image('raw')
        for image in os.listdir(self._root):
            if image != 'raw':
                self._create_image(image, image_name='raw')

    def _wait_image(self, name):
        """Wait raw image"""
        sleep(1)
        logger.info('Wait for raw image')
        try:
            if pyrax.cloudservers.images.find(name=name).status != 'ACTIVE':
                self._wait_raw_image()
        except Exception:
            self._wait_raw_image()

    def _create_image(self, name, **kwargs):
        """Create image"""
        image_root = os.path.join(self._root, name)
        with connect_to_node(**kwargs) as node:
            node.put(image_root, '/root/{name}/'.format(name=name))
            out = node.execute('''
                cd /root/{name}/
                bash bootstrap.sh
            '''.format(name=name))
            logger.info(out.stdout)
            logger.info(out.stderr)
            node.save_image(name)
            self._wait_image(name)
