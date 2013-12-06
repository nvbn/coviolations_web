import os
from django.core.management import BaseCommand
from django.conf import settings
from ...utils import connect_to_node, logger


class Command(BaseCommand):
    help = 'create nodes images'

    def handle(self, *args, **kwargs):
        self._root = os.path.join(settings.PROJECT_ROOT, 'nodes', 'images')
        self._create_image('raw')
        for image in os.listdir(self._root):
            self._create_image(image, image_id='raw')

    def _create_image(self, name, **kwargs):
        """Create image"""
        raw_root = os.path.join(self._root, 'raw')
        with connect_to_node(*kwargs) as node:
            node.put(raw_root, '/root/{name}/')
            out = node.execute('''cd /root/{name}/
            bash bootstrap.sh
            '''.format(name))
            logger.info(out.stdout)
            logger.info(out.stderr)
            node.save_image(name)
