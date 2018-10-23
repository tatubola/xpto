from test_plus.test import TestCase

from ..models import User


class TestUser(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuser@example.com', password='123456',
                                             name='Joe Tester')

    def test__str__(self):
        self.assertEqual(
            self.user.__str__(),
            'testuser@example.com'  # This is the default email for self.make_user()
        )

    def test_get_full_name(self):
        self.assertEqual(
            self.user.get_full_name(),
            'Joe Tester'
        )

    def test_get_short_name(self):
        self.assertEqual(
            self.user.get_short_name(),
            'Joe Tester'
        )

    def test_get_absolute_url(self):
        self.assertEqual(
            self.user.get_absolute_url(),
            '/users/testuser@example.com/'
        )


class TestSuperUser(TestCase):

    def test_createsuperuser_should_fail(self):
        with self.assertRaisesRegexp(ValueError, 'The given email must be set'):
            self.user = User.objects.create_superuser(email='', password='123456')
