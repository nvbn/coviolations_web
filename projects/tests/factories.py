import factory
from django.contrib.auth.models import User
from accounts.tests.factories import UserFactory
from .. import models


class OrganizationFactory(factory.DjangoModelFactory):
    """Organization factory"""
    FACTORY_FOR = models.Organization

    name = factory.Sequence(lambda n: 'organization {}'.format(n))

    @factory.post_generation
    def users(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for user in extracted:
                self.users.add(user)
        else:
            self.users = UserFactory.create_batch(10)


class ProjectFactory(factory.DjangoModelFactory):
    """Project factory"""
    FACTORY_FOR = models.Project

    name = factory.Sequence(lambda n: 'project {}'.format(n))
    url = factory.Sequence(lambda n: 'http://test{}.com'.format(n))
    organization = factory.SubFactory(OrganizationFactory)

    @factory.sequence
    def owner(n):
        return User.objects.create_user('user{}'.format(n))
