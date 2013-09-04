from projects.models import Commit, Branch
from tasks.models import Task, Violation
from .base import library


@library.register('dummy')
def dummy_service(data):
    """Create task from data dict"""
    branch = Branch.objects.get(
        name=data['branch'],
        project__name=data['project'],
    )
    commit = Commit.objects.create(
        name=data['commit'],
        branch=branch,
    )
    task = Task.objects.create(
        commit=commit,
    )
    for violation in data['violations']:
        Violation.objects.create(
            task=task,
            violation=violation['name'],
            raw_data=violation['data'],
        )
