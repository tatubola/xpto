from django.core.urlresolvers import resolve, reverse
from test_plus.test import TestCase

from ..models import User


class TestUserURLs(TestCase):
    """Test URL patterns for users app."""

    def setUp(self):
        self.user = self.make_user()

    def make_user(self, email='testuser@example.com', password='password', perms=None):
        """
        Build a user with email testuser@example.com and password of
        'password' for testing purposes.
        """
        test_user = User.objects.create_user(
            email,
            password,
        )

        if perms:
            _filter = Q()
            for perm in perms:
                if '.' not in perm:
                    raise ImproperlyConfigured(
                        'The permission in the perms argument needs to be either '
                        'app_label.codename or app_label.* (e.g. accounts.change_user or accounts.*)'
                    )

                app_label, codename = perm.split('.')
                if codename == '*':
                    _filter = _filter | Q(content_type__app_label=app_label)
                else:
                    _filter = _filter | Q(content_type__app_label=app_label, codename=codename)

            test_user.user_permissions.add(*list(Permission.objects.filter(_filter)))

        return test_user

    def test_list_reverse(self):
        """users:list should reverse to /users/."""
        self.assertEqual(reverse('users:list'), '/users/')

    def test_list_resolve(self):
        """/users/ should resolve to users:list."""
        self.assertEqual(resolve('/users/').view_name, 'users:list')

    def test_redirect_reverse(self):
        """users:redirect should reverse to /users/~redirect/."""
        self.assertEqual(reverse('users:redirect'), '/users/~redirect/')

    def test_redirect_resolve(self):
        """/users/~redirect/ should resolve to users:redirect."""
        self.assertEqual(
            resolve('/users/~redirect/').view_name,
            'users:redirect'
        )

    def test_detail_reverse(self):
        """users:detail should reverse to /users/testuser/."""
        self.assertEqual(
            reverse('users:detail', kwargs={'email': 'testuser@example.com'}),
            '/users/testuser@example.com/'
        )

    def test_detail_resolve(self):
        """/users/testuser/ should resolve to users:detail."""
        self.assertEqual(resolve('/users/testuser/').view_name, 'users:detail')

    def test_update_reverse(self):
        """users:update should reverse to /users/~update/."""
        self.assertEqual(reverse('users:update'), '/users/~update/')

    def test_update_resolve(self):
        """/users/~update/ should resolve to users:update."""
        self.assertEqual(
            resolve('/users/~update/').view_name,
            'users:update'
        )
