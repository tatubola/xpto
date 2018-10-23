from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy

from ..login import DefaultLogin
from ...models import SwitchModel, SwitchPortRange

# from ..makefaketestdata import MakeFakeTestData


class Test_SwitchPortRange(TestCase):
    """Tests SwitchPortRange model."""

    def setUp(self):
        DefaultLogin.__init__(self)

        self.extreme = mommy.make(
            SwitchModel,
            model='ASR9003',
            vendor='CISCO',
        )
        self.extreme_port_range = mommy.make(
            SwitchPortRange,
            switch_model=self.extreme,
            name_format='TenGigE0/0/1/{0}',
            capacity=1000,
            connector_type='SFP+',
            begin=1, end=48,
        )

    def test__str__(self):
        self.assertEqual(str(self.extreme_port_range), '[ASR9003: 1-48]')

    def test_meta_verbose_name(self):
        self.assertEqual(
            str(SwitchPortRange._meta.verbose_name), 'SwitchPortRange')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(
            str(SwitchPortRange._meta.verbose_name_plural), 'SwitchPortRanges')

    def test_simple_history(self):
        # is the last extreme_port_range in the historical table?
        self.assertEqual(self.extreme_port_range,
                         self.extreme_port_range.history.most_recent())
        self.extreme_port_range.description = 'my description'
        self.extreme_port_range.save()
        # is the last extreme_port_range in the historical table?
        self.assertEqual(
            self.extreme_port_range.history.most_recent().description,
            'my description')
        # is the modified_by data field actually working?
        self.assertEqual(
            self.extreme_port_range.history.most_recent().modified_by,
            self.superuser)
        # is there two instances of extreme_port_range in the historical table?

        self.assertEqual(self.extreme_port_range.history.count(), 2)

    def test_update_capacity(self):
        self.extreme_port_range.capacity = 10000
        with self.assertRaisesMessage(
            ValidationError,
                'Trying to update non updatable field: '
                'SwitchPortRange.capacity'):
            self.extreme_port_range.save()

    def test_update_connector_type(self):
        self.extreme_port_range.connector_type = 'QSFP28'
        with self.assertRaisesMessage(
            ValidationError,
                'Trying to update non updatable field: '
                'SwitchPortRange.connector_type'
        ):
            self.extreme_port_range.save()

    def test_update_name_format(self):
        self.extreme_port_range.name_format = 'TenGigE1/2/3/{0}'
        with self.assertRaisesMessage(
            ValidationError,
                'Trying to update non updatable field: '
                'SwitchPortRange.name_format'
        ):
            self.extreme_port_range.save()

    def test_update_begin(self):
        self.extreme_port_range.begin = 2
        with self.assertRaisesMessage(
            ValidationError,
                'Trying to update non updatable field: '
                'SwitchPortRange.begin'
        ):
            self.extreme_port_range.save()

    def test_update_end(self):
        self.extreme_port_range.end = 25
        with self.assertRaisesMessage(
            ValidationError,
                'Trying to update non updatable field: '
                'SwitchPortRange.end'):
            self.extreme_port_range.save()

    def test_update_switch_model(self):
        self.extreme_test = mommy.make(
            SwitchModel,
            model='X460-48t',
            vendor="EXTREME"
        )
        self.extreme_port_range.switch_model = self.extreme_test
        with self.assertRaisesMessage(
            ValidationError,
                'Trying to update non updatable field: '
                'SwitchPortRange.switch_model'):
            self.extreme_port_range.save()

    def test_begin_le_end(self):
        with self.assertRaisesMessage(
            ValidationError,
                'begin field must be less or equal than end field'):
            self.port_range_test = mommy.make(
                SwitchPortRange,
                switch_model=self.extreme,
                name_format='TenGigE0/0/6/{0}',
                begin=12, end=6,
            )

    def test_name_format_fail(self):
        with self.assertRaisesMessage(
            ValidationError,
                'there is more than one { or } on name_format'):
            self.port_range_test = mommy.make(
                SwitchPortRange,
                switch_model=self.extreme,
                name_format='TenGigE0/0/6/{{0}',
                begin=1, end=24,
            )
        with self.assertRaisesMessage(
            ValidationError,
                'there is more than one { or } on name_format'):
            self.port_range_test = mommy.make(
                SwitchPortRange,
                switch_model=self.extreme,
                name_format='TenGigE0/0/6/{0}}',
                begin=1, end=24,
            )
        with self.assertRaisesMessage(
            ValidationError,
                'there is more than one { or } on name_format'):
            self.port_range_test = mommy.make(
                SwitchPortRange,
                switch_model=self.extreme,
                name_format='TenGigE0/0/6/{{0}}',
                begin=1, end=24,
            )

    def test_conflict_ranges(self):
        self.port_range_test_1 = mommy.make(
            SwitchPortRange,
            switch_model=self.extreme,
            name_format='{0}',
            begin=1, end=48,
        )

        with self.assertRaisesMessage(
            ValidationError,
            'This interval of range conflits with another existent'
        ):
            self.port_range_test_2 = mommy.make(
                SwitchPortRange,
                switch_model=self.extreme,
                name_format='{0}',
                begin=12, end=56,
            )

        with self.assertRaisesMessage(
            ValidationError,
            'This interval of range conflits with another existent'
        ):
            self.port_range_test_2 = mommy.make(
                SwitchPortRange,
                switch_model=self.extreme,
                name_format='{0}',
                begin=6, end=28,
            )
            self.port_range_test_2.save()

        with self.assertRaisesMessage(
            ValidationError,
            'This interval of range conflits with another existent'
        ):
            self.port_range_test_2 = mommy.make(
                SwitchPortRange,
                switch_model=self.extreme,
                name_format='{0}',
                begin=48, end=56,
            )

        with self.assertRaisesMessage(
            ValidationError,
            'This interval of range conflits with another existent'
        ):
            self.port_range_test_2 = mommy.make(
                SwitchPortRange,
                switch_model=self.extreme,
                name_format='{0}',
                begin=49, end=56,
            )
            self.port_range_test_2 = mommy.make(
                SwitchPortRange,
                switch_model=self.extreme,
                name_format='{0}',
                begin=50, end=52,
            )

    def test_raise_message_with_not_valid_capacity_choice(self):
        with self.assertRaisesMessage(
            ValidationError,
            'Value 73 is not a valid choice.'
        ):
                mommy.make(
                    SwitchPortRange,
                    capacity='73',
                    name_format='TenGigE0/0/6/{0}'
                )
