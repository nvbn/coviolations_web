import logging
import pyrax
import paramiko
from scp import SCPClient
from gevent import sleep
from django.conf import settings



logger = logging.getLogger('nodes')
pyrax.set_setting(*settings.PYRAX_SETTINGS)
pyrax.set_credentials(*settings.PYRAX_CREDENTIALS)


class NodeOutput(object):
    """Node output"""

    def __init__(self, stdout, stderr, script):
        self.stdout = self._prepare(stdout)
        self.stderr = self._prepare(stderr)
        self.script = script

    def _prepare(self, channel):
        """Prepare output channel"""
        return channel.read().decode('utf8')


class NodeConnection(object):
    """Remote node"""

    def __init__(
        self, image_id=settings.PYRAX_DEFAULT_IMAGE,
        flavor_id=settings.PYRAX_DEFAULT_FLAVOR,
    ):
        self._image = pyrax.cloudservers.images.find(human_id=image_id)
        self._flavor = pyrax.cloudservers.flavors.find(
            human_id=flavor_id,
        )
        self._name = pyrax.utils.random_ascii(8)

    def _get_ip(self):
        """Get server ip"""
        for addr in self._server.addresses['public']:
            if addr['version'] == 4:
                return addr['addr']

    def _wait(self):
        """Waite when server building"""
        while self._server.status != 'ACTIVE':
            sleep(1)
            self._server = pyrax.cloudservers.servers.find(
                id=self._server.id,
            )
            logger.info('Server wait: {}'.format(self._name))

    def _create_server(self):
        """Create server"""
        logger.info('Start creating server: {}'.format(self._name))
        self._server = pyrax.cloudservers.servers.create(
            self._name, self._image.id, self._flavor.id,
        )
        self._wait()
        self._server.change_password(settings.PYRAX_PASSWORD)
        self._wait()
        logger.info('Server created: {}'.format(self._name))

    def _create_ssh(self):
        """Create ssh connection"""
        try:
            self._client = paramiko.SSHClient()
            self._client.set_missing_host_key_policy(
                paramiko.AutoAddPolicy(),
            )
            self._client.connect(
                self._get_ip(), username='root',
                password=settings.PYRAX_PASSWORD,
            )
        except paramiko.AuthenticationException as e:
            logger.info('SSH connection wait:{}'.format(e))
            self._create_ssh()
        logger.info('SSH connection ready:{}'.format(self._name))

    def __enter__(self):
        self._create_server()
        self._create_ssh()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._client.close()
        self._server.delete()

    def __repr__(self):
        return self._name

    def execute(self, script):
        """Execute script on node"""
        logger.info('Execute {}:\n{}'.format(self._name, script))
        _, stdout, stderr = self._client.exec_command(script)
        return NodeOutput(stdout, stderr, script)

    def save_image(self, name):
        """Save node image"""
        logger.info('Save image on {}: {}'.format(self._name, name))
        for image in pyrax.cloudservers.images.findall(name=name):
            image.delete()
        pyrax.cloudservers.servers.create_image(self._server.id, name)

    def put(self, local_path, remote_path):
        """Put files to node"""
        logger.info('Put files on {}: {}'.format(self._name, local_path))
        client = SCPClient(self._client.get_transport())
        client.put(local_path, remote_path, recursive=True)


def connect_to_node(*args, **kwargs):
    """Connect to node"""
    return NodeConnection(*args, **kwargs)
