from datetime import datetime
from html2text import html2text
from github import Github
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.conf import settings
from django_rq import job
from violations.exceptions import ViolationDoesNotExists
import services.base
import violations.base
from push.base import sender
from projects.models import Project
from .models import Tasks
from .utils import logger
from . import const


@job
def create_task(task_id):
    """Create task job"""
    data = Tasks.find_one(task_id)
    data['created'] = datetime.now()
    task = services.base.library.get(data['service']['name'])(data)

    if task:
        prepare_violations.delay(task)
    else:
        logger.warning(
            'Task failed: {}'.format(task_id), exc_info=True, extra={
                'task': task
            },
        )


def _prepare_violation(violation):
    """Prepare single violation"""
    try:
        violation_creator = violations.base.library.get(violation['name'])
        return violation_creator(violation)
    except ViolationDoesNotExists as e:
        logger.warning(
            "Violation doesn't exists: {}".format(e), exc_info=True, extra={
                'violation': violation,
            },
        )

        violation['status'] = const.STATUS_FAILED
        return violation
    except Exception as e:
        logger.exception('Violation failed: {}'.format(e))
        return violation


@job
def prepare_violations(task_id):
    """Prepare violations"""
    task = Tasks.find_one(task_id)
    task['violations'] = map(_prepare_violation, task['violations'])
    task['status'] = const.STATUS_SUCCESS if all([
        violation.get('status') != const.STATUS_FAILED
        for violation in task['violations']
    ]) else const.STATUS_FAILED
    Tasks.save(task)

    sender.send(
        type='task', owner=task['owner_id'],
        task=str(task_id), project=task['project'],
    )

    if task.get('pull_request_id') and not task.get('is_private'):
        comment_pull_request.delay(task_id)


@job
def comment_pull_request(task_id):
    """Comment pull request on github"""
    task = Tasks.find_one(task_id)
    project = Project.objects.get(name=task['project'])
    github = Github(
        settings.GITHUB_COMMENTER_USER, settings.GITHUB_COMMENTER_PASSWORD,
    )
    repo = github.get_repo(project.name)
    pull_request = repo.get_pull(task['pull_request_id'])
    html_comment = render_to_string(
        'tasks/pull_request_comment.html', {
            'badge': project.get_badge_url(commit=task['commit']['hash']),
            'task': task,
            'url': 'http://{}{}'.format(
                Site.objects.get_current().domain,
                reverse('tasks_detail', args=(str(task['_id']),)),
            ),
        }
    )
    pull_request.create_issue_comment(
        html2text(html_comment)
    )
