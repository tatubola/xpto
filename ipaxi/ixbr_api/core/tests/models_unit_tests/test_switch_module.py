from unittest.mock import patch
from model_mommy import mommy

from django.core.exceptions import ValidationError
from django.test import TestCase

from ...models import (SwitchModule, User)


class Test_SwitchModule(TestCase):
    """Tests SwitchModule model."""
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def setUp(self, mock_full_clean):

        new_user = User.objects.get_or_create(
            name='otheruser', email='otheruser@nic.br')[0]
        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = new_user

        self.module = mommy.make(
            SwitchModule,
            model='ABCDE',
            vendor='EXTREME')
        self.module_2 = mommy.make(
            SwitchModule,
            model='JKL',
            vendor='EXTREME')
        self.module_3 = mommy.make(
            SwitchModule,
            model='FGH',
            vendor='EXTREME')

    def test__str__(self):
        self.assertEqual(str(self.module), '[module-%s-%s ports]' % (
            self.module.model,
            self.module.port_quantity))

    def test_meta_verbose_name(self):
        self.assertEqual(
            str(SwitchModule._meta.verbose_name), 'SwitchModule')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(
            str(SwitchModule._meta.verbose_name_plural), 'SwitchModules')

    def test_meta_order_by(self):
        self.assertEqual(SwitchModule.objects.all().ordered, True)

        self.assertEqual(
            str(SwitchModule.objects.all()[0]), str(self.module))
        self.assertEqual(
            str(SwitchModule.objects.all()[1]), str(self.module_3))
        self.assertEqual(
            str(SwitchModule.objects.all()[2]), str(self.module_2))

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_simple_history(self, mock_full_clean):
        
        self.assertEqual(self.module,
                         self.module.history.most_recent())
        self.module.description = 'my description'
        self.module.save()
      
        self.assertEqual(
            self.module.history.most_recent().description,
            'my description')

        self.assertEqual(self.module.history.count(), 2)