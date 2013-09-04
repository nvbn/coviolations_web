from django.test import TestCase
from django.core.urlresolvers import reverse


class IndexViewCase(TestCase):
    """Index view case"""

    def setUp(self):
        self.url = reverse('home')

    def test_get_ok(self):
        """Test status=200"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
