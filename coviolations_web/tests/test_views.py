import sure
from django.test import TestCase
from django.core.urlresolvers import reverse


class IndexViewCase(TestCase):
    """Index view case"""

    def setUp(self):
        self.url = reverse('home')

    def test_get_ok(self):
        """Test status=200"""
        response = self.client.get(self.url)
        response.status_code.should.be.equal(200)


class TestRedirectToHashView(TestCase):
    """Test redirect to hash view"""

    def test_redirect_to_hash(self):
        """Test redirect to hash"""
        response = self.client.get('/not_found-url/')
        response.status_code.should.be.equal(302)
        response['Location'].should.be.equal('/#/not_found-url/')
