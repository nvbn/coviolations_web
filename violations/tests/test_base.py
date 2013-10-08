import sure
from django.test import TestCase
from ..base import ViolationsLibrary
from ..exceptions import ViolationDoesNotExists


class ViolationsLibraryCase(TestCase):
    """Violations library case"""

    def setUp(self):
        self.library = ViolationsLibrary()

    def test_register(self):
        """Test register"""
        @self.library.register('dummy')
        def violation():
            pass

        self.library.get('dummy').should.be.equal(violation)

    def test_not_found(self):
        """Test violation not found"""
        self.library.get.when.called_with('dummy!!!')\
            .should.throw(ViolationDoesNotExists)

    def test_has(self):
        """Test has method"""
        @self.library.register('dummy')
        def violation():
            pass

        self.library.has('dummy').should.be.true
        self.library.has('dummy!!!').should.be.false
