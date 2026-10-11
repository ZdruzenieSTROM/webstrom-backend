from django.conf import settings
from django.test import SimpleTestCase, override_settings

NOINDEX_MIDDLEWARE = 'base.middleware.noindex_middleware'


class TestNoindexMiddleware(SimpleTestCase):
    '''X-Robots-Tag je len tam, kde je middleware zapnuty'''

    @override_settings(MIDDLEWARE=[NOINDEX_MIDDLEWARE, *settings.MIDDLEWARE])
    def test_enabled_marks_response_and_redirect_as_noindex(self):
        self.assertEqual(
            self.client.get('/api/neexistuje/')['X-Robots-Tag'],
            'noindex, nofollow',
        )
        # redirect na trailing slash vyraba CommonMiddleware, nie view
        redirect = self.client.get('/django-admin')
        self.assertEqual(redirect.status_code, 301)
        self.assertEqual(redirect['X-Robots-Tag'], 'noindex, nofollow')

    def test_default_settings_leave_response_indexable(self):
        self.assertNotIn('X-Robots-Tag', self.client.get('/api/neexistuje/'))
