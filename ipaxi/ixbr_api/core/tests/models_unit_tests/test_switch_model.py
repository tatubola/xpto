from django.core.exceptions import ValidationError
from django.test import TestCase

from ...models import SwitchModel
from ..makefaketestdata import MakeFakeTestData


class Test_SwitchModel(TestCase):
    """Tests SwitchModel model."""

    def setUp(self):
        MakeFakeTestData.__init__(self)

    def test__str__(self):
        self.assertEqual(
            str(SwitchModel.objects.all()[0]), str(self.extreme))
        self.assertEqual(
            str(SwitchModel.objects.all()[1]), str(self.cisco_sp_1))
        self.assertEqual(
            str(SwitchModel.objects.all()[2]), str(self.cisco_sp_2))

    def test_meta_verbose_name(self):
        self.assertEqual(
            str(SwitchModel._meta.verbose_name), 'SwitchModel')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(
            str(SwitchModel._meta.verbose_name_plural), 'SwitchModels')

    def test_meta_order_by(self):
        self.assertEqual(SwitchModel.objects.all().ordered, True)

    def test_simple_history(self):
        history_count = self.cisco_sp_2.history.count()

        # is the last cisco_sp_2 in the historical table?
        self.assertEqual(self.cisco_sp_2,
                         self.cisco_sp_2.history.most_recent())
        self.cisco_sp_2.description = 'my description'
        self.cisco_sp_2.save()
        # is the last cisco_sp_2 in the historical table?
        self.assertEqual(
            self.cisco_sp_2.history.most_recent().description,
            'my description')
        # is the modified_by data field actually working?
        self.assertEqual(
            self.cisco_sp_2.history.most_recent().modified_by, self.superuser)
        # is there two instances of cisco_sp_2 in the historical table?

        self.assertEqual(self.cisco_sp_2.history.count(), history_count + 1)

    def test_update_model(self):
        self.cisco_sp_2.model = 'ASR9999'
        with self.assertRaisesMessage(
            ValidationError,
                'Trying to update non updatable field: SwitchModel.model'):
                self.cisco_sp_2.save()

    def test_model_vendor(self):
        with self.assertRaisesMessage(ValidationError,
                                      'SwitchModel.model format not compatible with SwitchModel.vendor.'):
            self.model_test = SwitchModel.objects.create(
                model='X480t',
                vendor='CISCO',
                last_ticket='2121')
            self.extreme_test.save()
