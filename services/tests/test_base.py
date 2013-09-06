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

        self.assertEqual(self.library.get('dummy'), service)

    def test_not_found(self):
        """Test service not found"""
        with self.assertRaises(ServiceDoesNotExists):
            self.library.get('dummy!!!')

    def test_has(self):
        """Test has method"""
        @self.library.register('dummy')
        def service():
            pass

        self.assertTrue(self.library.has('dummy'))
        self.assertFalse(self.library.has('dummy!!!'))
