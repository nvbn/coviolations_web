from django_rq import job
import services.base


@job
def create_task(service, data):
    """Create task job"""
    task = services.base.library.get(service)(data)
    prepare_violations(task)


@job
def prepare_violations(task):
    """Prepare violations"""
    for violation in task.violations.all():
        violation.prepare()
        violation.save()
