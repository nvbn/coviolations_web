from logging import getLogger
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import redirect_to_login
from braces.views import AccessMixin
from .models import Project


logger = getLogger('coviolations_projects')


class ProjectAccessMixin(AccessMixin):
    """Project access mixin"""

    def dispatch(self, request, *args, **kwargs):
        check_result = self.check_can_access(request)
        if check_result:
            return check_result
        else:
            return super(ProjectAccessMixin, self).dispatch(
                request, *args, **kwargs
            )

    def check_can_access(self, request, can_retry=True):
        """Check can user access"""
        project = self.get_project()
        if not project.can_access(request.user):
            if (
                project.organization and
                can_retry and
                request.user.is_authenticated()
            ):
                Project.objects.update_user_projects(request.user)
                return self.check_can_access(request, False)
            elif not request.user.is_authenticated():
                return redirect_to_login(
                    request.get_full_path(),
                    self.get_login_url(),
                    self.get_redirect_field_name(),
                )
            raise PermissionDenied
