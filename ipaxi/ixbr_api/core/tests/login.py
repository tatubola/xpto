from unittest.mock import patch

from ixbr_api.users.models import User


class DefaultLogin(object):

    def __init__(self):
        '''
        Note that a Test Class will merge this __init__ class in these
        setUp that is method of django.test.TestCase, which already
        globalize the __init__ of the test class:

        Examples:
            from ..login import DefaultLogin
            class TagListViewTestBasics(TestCase):
                def setUp(self):
                    DefaultLogin.__init__(self)
        '''
        self.superuser = User.objects.create_superuser(
            email='demi@ix.br',
            password='D3M1+h3G0dOf1n+3rn3+1s0n',
            name='Demi the God of Internetson')
        patcher = patch('ixbr_api.core.models.get_current_user')
        self.addCleanup(patcher.stop)

        self.get_user_mock = patcher.start()
        self.get_user_mock.return_value = self.superuser

        # Log into application
        self.login = self.client.login(
            email='demi@ix.br',
            password='D3M1+h3G0dOf1n+3rn3+1s0n')
