import os
import logging
import pyrax as eager_pyrax
import paramiko
from scp import SCPClient
from gevent import sleep
from django.conf import settings


logger = logging.getLogger('nodes')


class LazyPyraxProxy(object):
    """Lazy proxy to pyrax"""

    def __init__(self):
        self._is_initialized = False

    def _initialize_pyrax(self):
        """Initialize pyrax"""
        eager_pyrax.set_setting(*settings.PYRAX_SETTINGS)
        eager_pyrax.set_credentials(*settings.PYRAX_CREDENTIALS)
        self._is_initialized = True

    @property
    def pyrax(self):
        if not self._is_initialized:
            self._initialize_pyrax()
        return eager_pyrax

    def __getattr__(self, item):
        return getattr(self.pyrax, item)


pyrax = LazyPyraxProxy()


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
        image_name=None,
    ):
        self._image = pyrax.cloudservers.images.find(**self._get_image_kwargs(
            image_id, image_name,
        ))
        self._flavor = pyrax.cloudservers.flavors.find(
            human_id=flavor_id,
        )
        self._name = pyrax.utils.random_ascii(8)

    def _get_image_kwargs(self, image_id, image_name):
        """Get image kwargs"""
        if image_name:
            return {'name': image_name}
        else:
            return {'human_id': image_id}

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

    def _wait_image(self, name):
        """Wait when image creating"""
        sleep(1)
        logger.info('Wait for {} image'.format(name))
        try:
            if pyrax.cloudservers.images.find(name=name).status != 'ACTIVE':
                self._wait_image(name)
        except Exception:
            self._wait_image(name)

    def save_image(self, name):
        """Save node image"""
        logger.info('Save image on {}: {}'.format(self._name, name))
        for image in pyrax.cloudservers.images.findall(name=name):
            image.delete()
        pyrax.cloudservers.servers.create_image(self._server.id, name)
        self._wait_image(name)

    def put(self, local_path, remote_path):
        """Put files to node"""
        logger.info('Put files on {}: {}'.format(self._name, local_path))
        client = SCPClient(self._client.get_transport())
        client.put(local_path, remote_path, recursive=True)

    def upload_keys(self, keys):
        """Upload keys to node"""
        logger.info('Upload keys on {}: {}'.format(self._name, keys))
        self.execute('mkdir /home/covio/.ssh/')
        self.execute(
            'ssh-keyscan -H github.com > /home/covio/.ssh/known_hosts',
        )
        self.put(keys.file_paths, '/home/covio/.ssh/')
        self.execute('chown -R covio /home/covio/.ssh')
        self.execute('chmod -R 700 /home/covio/.ssh')

    @property
    def id(self):
        """Get node id"""
        return self._server.id


def connect_to_node(*args, **kwargs):
    """Connect to node"""
    return NodeConnection(*args, **kwargs)


def get_image(name):
    """Get correct image by name"""
    root = os.path.join(settings.PROJECT_ROOT, 'nodes', 'images')
    if name in os.listdir(root):
        return name
    else:
        return 'raw'
