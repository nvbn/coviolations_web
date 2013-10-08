import sure
from django.test import TestCase
from ..base import ServicesLibrary
from ..exceptions import ServiceDoesNotExists


class ServicesLibraryCase(TestCase):
    """Services library case"""

    def setUp(self):
        self.library = ServicesLibrary()

    def test_register(self):
        """Test register"""
        @self.library.register('dummy')
        def service():
            pass

        self.library.get('dummy').should.be.equal(service)

    def test_not_found(self):
        """Test service not found"""
        self.library.get.when.called_with('dummy!!!')\
            .should.throw(ServiceDoesNotExists)

    def test_has(self):
        """Test has method"""
        @self.library.register('dummy')
        def service():
            pass

        self.library.has('dummy').should.be.true
        self.library.has('dummy!!!').should.be.false
