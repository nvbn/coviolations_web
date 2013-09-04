import factory
from django.conf import settings
from projects.tests.factories import CommitFactory
from .. import models


class TaskFactory(factory.DjangoModelFactory):
    """Task factory"""
    FACTORY_FOR = models.Task

    commit = factory.SubFactory(CommitFactory)


class ViolationFactory(factory.DjangoModelFactory):
    """Violation factory"""
    FACTORY_FOR = models.Violation
    raw_data = factory.Sequence(lambda n: 'raw {}'.format(n))

    @factory.sequence
    def violation(n):
        return settings.VIOLATIONS[n % len(settings.VIOLATIONS)]
