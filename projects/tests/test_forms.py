from django.test import TestCase
from django.contrib.auth.models import User
from ..forms import RegenerateTokenForm
from . import factories


class RegenerateTokenFormCase(TestCase):
    """Regenerate token form case"""

    def setUp(self):
        self.user = User.objects.create_user('test')

    def test_valid_with_self(self):
        """Test valid with self owner"""
        project = factories.ProjectFactory(owner=self.user)
        form = RegenerateTokenForm(self.user, {
            'project': project.id,
        })
        self.assertTrue(form.is_valid())

    def test_invalid_with_other_user(self):
        """Test invalid with other user"""
        project = factories.ProjectFactory()
        form = RegenerateTokenForm(self.user, {
            'project': project.id,
        })
        self.assertFalse(form.is_valid())

    def test_regenerating(self):
        """Test regenerating"""
        project = factories.ProjectFactory(owner=self.user)
        initial_token = project.token
        form = RegenerateTokenForm(self.user, {
            'project': project.id,
        })
        self.assertTrue(form.is_valid())
        self.assertNotEqual(initial_token, form.save().token)
