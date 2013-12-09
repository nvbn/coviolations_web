import factory
from projects.tests.factories import ProjectFactory
from ..models import NodeTask


class NodeTaskFactory(factory.DjangoModelFactory):
    """NodeTask factory"""
    FACTORY_FOR = NodeTask

    project = factory.SubFactory(ProjectFactory)
    revision = factory.Sequence('rev_{}'.format)
