from test_plus.test import TestCase

from ..admin import MyUserChangeForm, MyUserCreationForm
from ..models import User


class TestMyUserCreationForm(TestCase):

    def test_is_valid_success(self):
        # Instantiate the form with a new email
        form = MyUserCreationForm({
            'email': 'alamode@example.com',
            'password1': '7jefB#f@Cc7YJB]2v',
            'password2': '7jefB#f@Cc7YJB]2v',
        })
        # Run is_valid() to trigger the validation
        valid = form.is_valid()
        self.assertTrue(valid)

    def test_is_valid_false(self):
        self.user = User.objects.create_user('alamode@example.com', password='123456')
        # Instantiate the form with the same email as self.user
        form = MyUserCreationForm({
            'email': self.user.email,
            'password1': 'notalamodespassword',
            'password2': 'notalamodespassword',
        })
        # Run is_valid() to trigger the validation, which is going to fail
        # because the email is already taken
        valid = form.is_valid()
        self.assertFalse(valid)

        # The form.errors dict should contain a single error called 'email'
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('email' in form.errors)
