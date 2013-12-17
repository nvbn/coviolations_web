import os
from StringIO import StringIO
from datetime import datetime
import paramiko
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from projects.models import Project
from .utils import connect_to_node, get_image, logger, kill_node
from .exceptions import TaskAlreadyPerformed


class ProjectKeys(models.Model):
    """Project keys model"""
    project = models.ForeignKey(Project, verbose_name=_('project'))
    public_key = models.TextField(verbose_name=_('public key'))
    private_key = models.TextField(verbose_name=_('private key'))

    class Meta:
        verbose_name = _('Project Keys')
        verbose_name_plural = _('Project Keys')

    def __unicode__(self):
        return u'{}: {}'.format(self.project, self.public_key)

    def save(self, *args, **kwargs):
        """Generate keys and save"""
        if not (self.public_key or self.private_key):
            self._generate_keys()
            self._add_to_github()
        return super(ProjectKeys, self).save(*args, **kwargs)

    def _generate_keys(self):
        """Generate keys"""
        key = paramiko.RSAKey.generate(2048)
        private_key = StringIO()
        key.write_private_key(private_key)
        self.public_key = key.get_base64()
        self.private_key = private_key.getvalue()

    def _add_to_github(self):
        """Add keys to github"""
        self.project.repo.create_key(
            'coviolations.io ci key', 'ssh-rsa {} ci@coviolations.io'.format(
                self.public_key,
            ),
        )

    @property
    def file_paths(self):
        """Get file paths"""
        if not hasattr(self, '_file_paths'):
            path = os.path.join(
                settings.KEYS_TEMPORARY_ROOT, 'keys_{}'.format(self.id),
            )
            if not os.path.exists(path):
                os.makedirs(path)
            public_path = os.path.join(path, 'id_rsa.pub')
            with open(public_path, 'w') as key_file:
                key_file.write(self.public_key)
            private_path = os.path.join(path, 'id_rsa')
            with open(private_path, 'w') as key_file:
                key_file.write(self.private_key)
            self._file_paths = public_path, private_path
        return self._file_paths


@receiver(post_save, sender=Project)
def generate_project_keys(instance, **kwargs):
    """Generate project keys on save"""
    if (
        instance.run_here and
        not ProjectKeys.objects.filter(project=instance).exists()
    ):
        ProjectKeys.objects.create(project=instance)


class NodeTask(models.Model):
    """Node task"""
    STATE_NEW = 0
    STATE_ACTIVE = 1
    STATE_FINISHED = 2
    STATE_FAILED = 3
    STATES = (
        (STATE_NEW, _('new')),
        (STATE_ACTIVE, _('active')),
        (STATE_FINISHED, _('finished')),
        (STATE_FAILED, _('failed'))
    )

    project = models.ForeignKey(Project, verbose_name=_('project'))
    revision = models.CharField(max_length=42, verbose_name=_('revision'))
    branch = models.CharField(max_length=300, verbose_name=_('branch'))
    pull_request_id = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_('pull request id'),
    )
    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created'),
    )
    finished = models.DateTimeField(
        blank=True, null=True, verbose_name=_('finished'),
    )
    state = models.PositiveSmallIntegerField(
        choices=STATES, default=STATE_NEW, verbose_name=_('state'),
    )
    input = models.TextField(blank=True, null=True, verbose_name=_('input'))
    stdout = models.TextField(blank=True, null=True, verbose_name=_('stdout'))
    stderr = models.TextField(blank=True, null=True, verbose_name=_('stderr'))
    node = models.CharField(
        max_length=30, blank=True, null=True, verbose_name=_('node'),
    )

    class Meta:
        verbose_name = _('Node Task')
        verbose_name_plural = _('Node Tasks')

    def __unicode__(self):
        return '{}: {}'.format(self.project, self.node)

    def _make_active(self):
        """Make task active"""
        if self.state != self.STATE_NEW:
            raise TaskAlreadyPerformed(self)
        self.state = self.STATE_ACTIVE
        self.save()

    def perform(self):
        """Perform task"""
        self._make_active()
        covio = self.project.get_covio(self.revision)
        image = get_image(covio.get('image'))
        with connect_to_node(image_name=image) as node:
            self.node = node.id
            self.save()
            try:
                keys = ProjectKeys.objects.get(project=self.project)
                node.upload_keys(keys)
                result = node.execute(self._get_script(image))
                self.input = result.script
                self.stdout = result.stdout
                self.stderr = result.stderr
                self.state = self.STATE_FINISHED
            except Exception as e:
                logger.exception(e)
                self.state = self.STATE_FAILED
        self.finished = datetime.now()
        self.save()

    def _get_script(self, image):
        """Get script for image"""
        return '''
            sudo -u covio bash -c "
                export RUN_ON_COVIO_SIDE='true'
                export COVIO_TOKEN='{token}'
                export GITHUB_TOKEN='{github_token}'
                export REPO_NAME='{project_name}'
                export NODE_TASK='{node_task}'
                sudo cp /root/{image}/launch.sh /home/covio/
                sudo chown covio /home/covio/launch.sh
                cd /home/covio/
                source launch.sh
                git clone {repo_url}
                cd {repo_name}
                git checkout {revision}
                covio
            "
        '''.format(
            token=self.project.token,
            image=image,
            github_token=self.project.owner.github_token,
            node_task=self.id,
            project_name=self.project.name,
            repo_name=self.project.repo.name,
            repo_url=self.project.repo.ssh_url,
            revision=self.revision,
        )

    def kill(self):
        """Kill node"""
        logger.warning('Node killed: {}'.format(self.id))
        if self.node:
            kill_node(self.node)
        self.state = self.STATE_FAILED
        self.finished = datetime.now()
        self.save()
