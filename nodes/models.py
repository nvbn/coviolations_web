from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from projects.models import Project
from .utils import connect_to_node, get_image, logger
from .exceptions import TaskAlreadyPerformed


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
        image = get_image(self.project.get_covio().get('image'))
        with connect_to_node(image_name=image) as node:
            try:
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
            export COVIO_TOKEN='{token}'
            export GITHUB_TOKEN='{github_token}'
            cp /root/{image}/launch.sh /home/covio/
            chown covio /home/covio/launch.sh
            cd /home/covio/
            sudo -u covio bash launch.sh
            sudo -u covio covio
        '''.format(
            token=self.project.token,
            image=image,
            github_token=self.project.owner.github_token,
        )
