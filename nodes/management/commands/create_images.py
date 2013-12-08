from gevent import monkey
monkey.patch_all()

import gevent
import os
from django.core.management import BaseCommand
from django.conf import settings
from ...utils import connect_to_node, logger


class Command(BaseCommand):
    help = 'create nodes images'

    def handle(self, *args, **kwargs):
        self._root = os.path.join(settings.PROJECT_ROOT, 'nodes', 'images')
        self._create_image('raw')
        tasks = [
            gevent.spawn(self._create_image, image, image_name='raw')
            for image in os.listdir(self._root) if image != 'raw'
        ]
        gevent.joinall(tasks)

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
