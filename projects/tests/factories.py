import factory
from django.contrib.auth.models import User
from .. import models


class ProjectFactory(factory.DjangoModelFactory):
    """Project factory"""
    FACTORY_FOR = models.Project

    name = factory.Sequence(lambda n: 'project {}'.format(n))
    url = factory.Sequence(lambda n: 'http://test{}.com'.format(n))

    @factory.sequence
    def owner(n):
        return User.objects.create_user('user{}'.format(n))


class BranchFactory(factory.DjangoModelFactory):
    """Branch factory"""
    FACTORY_FOR = models.Branch

    name = factory.Sequence(lambda n: 'branch {}'.format(n))
    project = factory.SubFactory(ProjectFactory)


class CommitFactory(factory.DjangoModelFactory):
    """Commit factory"""
    FACTORY_FOR = models.Commit

    name = factory.Sequence(lambda n: 'commit {}'.format(n))
    branch = factory.SubFactory(BranchFactory)
