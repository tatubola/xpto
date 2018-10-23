from django.http.request import HttpRequest
from django.test import TestCase

from ....users.models import User
from ...utils.globals import get_current_user
from ...utils.middlewares import SaveCurrentUser


class SaveCurrentUserTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            email='superuser@ix.br',
            password='V&ryS@f3Pwd',
            name='Super User')

    def test_base(self):
        """
        Test that SaveCurentUser stores user passed with the request
        """
        request = HttpRequest()
        request.user = self.user

        SaveCurrentUser(lambda x: x)(request)

        self.assertEqual(get_current_user(), self.user)
