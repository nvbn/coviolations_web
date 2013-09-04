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

        self.assertEqual(self.library.get('dummy'), violation)

    def test_not_register_not_enabled(self):
        """Test not register not enabled"""
        @self.library.register('dummy!!!')
        def violation():
            pass

        with self.assertRaises(ViolationDoesNotExists):
            self.library.get('dummy!!!')

    def test_not_found(self):
        """Test violation not found"""
        with self.assertRaises(ViolationDoesNotExists):
            self.library.get('dummy!!!')
