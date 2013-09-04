from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User


class ManageProjectViewCase(TestCase):
    """Manage project view case"""

    def setUp(self):
        self.url = reverse('projects_manage')

    def test_authorised_ok(self):
        """Test status=200"""
        User.objects.create_user('test', 'test@test.test', 'test')
        self.client.login(
            username='test',
            password='test',
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
