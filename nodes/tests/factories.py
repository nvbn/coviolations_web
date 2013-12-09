import factory
from projects.tests.factories import ProjectFactory
from .. import models


class NodeTaskFactory(factory.DjangoModelFactory):
    """NodeTask factory"""
    FACTORY_FOR = models.NodeTask

    project = factory.SubFactory(ProjectFactory)
    revision = factory.Sequence('rev_{}'.format)


class ProjectKeysFactory(factory.DjangoModelFactory):
    """Project keys factory"""
    FACTORY_FOR = models.ProjectKeys

    project = factory.SubFactory(ProjectFactory)
