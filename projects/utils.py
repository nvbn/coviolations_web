from logging import getLogger
from .models import Project


logger = getLogger('coviolations_projects')


class ProjectAccessMixin(object):
    """Project access mixin"""

    def check_can_access(self, project, can_retry=True):
        """Check can user access"""
        if project.can_access(self.request.user):
            return True
        else:
            if (
                project.organization and
                can_retry and
                self.request.user.is_authenticated()
            ):
                Project.objects.update_user_projects(self.request.user)
                return self.check_can_access(project, False)
            return False
