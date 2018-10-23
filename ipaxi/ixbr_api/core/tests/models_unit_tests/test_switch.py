from django.core.exceptions import ValidationError
from django.test import TestCase

from ...models import (Switch, SwitchModel, SwitchPortRange,)
from ..makefaketestdata import MakeFakeTestData


class Test_Switch(TestCase):
    """Tests Switch model."""

    def setUp(self):
        MakeFakeTestData.__init__(self)

    def test__str__(self):
        self.assertEqual(str(self.cisco_sp_araguaia), '[%s: %s]' % (
            self.cisco_sp_araguaia.pix, self.cisco_sp_araguaia.management_ip))

    def test_meta_verbose_name(self):
        self.assertEqual(
            str(Switch._meta.verbose_name), 'Switch')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(
            str(Switch._meta.verbose_name_plural), 'Switches')

    def test_meta_order_by(self):
        self.assertEqual(Switch.objects.all().ordered, True)

        self.assertEqual(
            str(Switch.objects.all()[0]), str(self.extreme_pix_kapotnhinore))
        self.assertEqual(
            str(Switch.objects.all()[1]), str(self.cisco_sp_araguaia))
        self.assertEqual(
            str(Switch.objects.all()[2]), str(self.cisco_sp_kadiweu))

    def test_simple_history(self):
        # is the last extreme_pix_kapotnhinore in the historical table?
        self.assertEqual(self.extreme_pix_kapotnhinore,
                         self.extreme_pix_kapotnhinore.history.most_recent())
        self.extreme_pix_kapotnhinore.description = 'my description'
        self.extreme_pix_kapotnhinore.save()
        # is the last extreme_pix_kapotnhinore in the historical table?
        self.assertEqual(
            self.extreme_pix_kapotnhinore.history.most_recent().description,
            'my description')
        # is the modified_by data field actually working?
        self.assertEqual(
            self.extreme_pix_kapotnhinore.history.most_recent().modified_by,
            self.superuser)
        # is there two instances of extreme_pix_kapotnhinore in the
        # historical table?

        self.assertEqual(self.extreme_pix_kapotnhinore.history.count(), 2)

    def test_update_pix(self):
        self.cisco_sp_araguaia.pix = self.kadiweu
        with self.assertRaisesMessage(
                ValidationError,
                'Trying to update non updatable field: Switch.pix'):
            self.cisco_sp_araguaia.save()

    def test_update_translation(self):
        if self.cisco_sp_araguaia.translation:
            self.cisco_sp_araguaia.translation = False
        else:
            self.cisco_sp_araguaia.translation = True

        self.cisco_sp_araguaia.save()

    def test_managment_ip(self):
        self.cisco_switch_model_test = SwitchModel.objects.create(
            model='ASR9432',
            vendor='CISCO',
            last_ticket='23123')
        self.cisco_port_range_test = SwitchPortRange.objects.create(
            switch_model=self.cisco_sp_2,
            name_format='TenGigE0/0/3/{0}',
            capacity=1000,
            connector_type='SFP+',
            begin=1, end=27,
            last_ticket='3453')

        with self.assertRaisesMessage(
            ValidationError,
                "192.168.1.1 doesn't belong to network "
                "management IX: " + self.sp.management_prefix):
            self.cisco_switch_test = Switch.objects.create(
                pix=self.araguaia,
                model=self.cisco_switch_model_test,
                management_ip='192.168.1.1',
                last_ticket='453',
                translation=False,
                create_ports=False)
            self.cisco_switch_test.save()

    '''TODO: Fix this test
    def test_create_ports(self):
        self.cisco_switch_model_test = SwitchModel.objects.create(
            model='ASR9432',
            vendor='CISCO',
            translation=False,
            last_ticket='23123')
        self.cisco_port_range_test = SwitchPortRange.objects.create(
            switch_model=self.cisco_switch_model_test,
            name_format='TenGigE0/0/4/{0}',
            capacity=1000,
            connector_type='SFP+',
            begin=1, end=27,
            last_ticket='64656')
        self.cisco_sp_switch_test = Switch.objects.create(
            pix=self.araguaia,
            model=self.cisco_switch_model_test,
            management_ip='192.168.5.252',
            last_ticket='313',
            create_ports=True)

        list_ports = list(
            Port.objects.filter(switch=self.cisco_sp_switch_test).order_by())
        self.assertEqual(len(list_ports), self.cisco_port_range_test.end)
        if len(list_ports) >= self.cisco_port_range_test.end:
            self.assertEqual(
                list_ports[0].name, self.
                cisco_port_range_test.name_format.format(
                    self.cisco_port_range_test.end))
            self.assertEqual(
                list_ports[-1].name, self.
                cisco_port_range_test.name_format.format(
                    self.cisco_port_range_test.begin))
            self.assertEqual(
                list_ports[0].last_ticket,
                self.cisco_sp_switch_test.last_ticket)
            self.assertEqual(
                list_ports[0].modified_by,
                self.cisco_sp_switch_test.modified_by)
        else:
            self.assertEqual(
                list_ports[0].name, self.
                cisco_port_range_test.name_format.format(
                    self.cisco_port_range_test.begin))
            self.assertEqual(
                list_ports[-1].name, self.
                cisco_port_range_test.name_format.format(
                    self.cisco_port_range_test.end))
            self.assertEqual(
                list_ports[0].last_ticket,
                self.cisco_sp_switch_test.last_ticket)
            self.assertEqual(
                list_ports[0].modified_by,
                self.cisco_sp_switch_test.modified_by)
    '''

    def test_create_one_aditional_port(self):
        """Testing creating one additional port, calling the method once,
        asserting if count is correct and the number of the last port.
        The qty variable is for each iteration of the method, it's not for total
        ports created.
        """
        qty = 1
        last_ticket = 1223
        self.assertEqual(self.cisco_sp_kadiweu.port_set.count(), 4)
        self.assertEqual(
            self.cisco_sp_kadiweu.port_set.latest('modified').name,
            "TenGigE0/0/0/4")

        self.cisco_sp_kadiweu.create_additional_ports(qty, last_ticket)
        self.assertEqual(self.cisco_sp_kadiweu.port_set.count(), 4+qty)
        self.assertEqual(
            self.cisco_sp_kadiweu.port_set.latest('modified').name,
            self.cisco_sp_kadiweu.model.switchportrange_set.first(
            ).name_format.format(
                self.cisco_sp_kadiweu.model.switchportrange_set.first(
                ).end+qty))

    def test_create_two_aditional_ports(self):
        """Testing creating two additional port, calling the method once,
        asserting if count is correct and the number of the last port.
        The qty variable is for each iteration of the method, it's not for total
        ports created.
        """
        qty = 2
        last_ticket = 1223
        self.assertEqual(self.cisco_sp_kadiweu.port_set.count(), 4)
        self.assertEqual(
            self.cisco_sp_kadiweu.port_set.latest('modified').name,
            "TenGigE0/0/0/4")

        self.cisco_sp_kadiweu.create_additional_ports(qty, last_ticket)
        self.assertEqual(self.cisco_sp_kadiweu.port_set.count(), 4+qty)
        self.assertEqual(
            self.cisco_sp_kadiweu.port_set.latest('modified').name,
            self.cisco_sp_kadiweu.model.switchportrange_set.first(
            ).name_format.format(
                self.cisco_sp_kadiweu.model.switchportrange_set.first(
                ).end+qty))

    def test_create_one_aditional_port_then_create_another_one(self):
        """Testing creating two additional port, calling the method twice,
        asserting on each call if count is correct and the number of the last
        port.
        The qty variable is for each iteration of the method, it's not for total
        ports created.
        """
        qty = 1
        last_ticket = 1223
        self.assertEqual(self.cisco_sp_kadiweu.port_set.count(), 4)
        self.assertEqual(
            self.cisco_sp_kadiweu.port_set.latest('modified').name,
            "TenGigE0/0/0/4")

        self.cisco_sp_kadiweu.create_additional_ports(qty, last_ticket)
        self.assertEqual(self.cisco_sp_kadiweu.port_set.count(), 4+qty)
        self.assertEqual(
            self.cisco_sp_kadiweu.port_set.latest('modified').name,
            self.cisco_sp_kadiweu.model.switchportrange_set.first(
            ).name_format.format(
                self.cisco_sp_kadiweu.model.switchportrange_set.first(
                ).end+qty))

        self.cisco_sp_kadiweu.create_additional_ports(qty, last_ticket)
        self.assertEqual(self.cisco_sp_kadiweu.port_set.count(), 4+qty+qty)
        self.assertEqual(
            self.cisco_sp_kadiweu.port_set.latest('modified').name,
            self.cisco_sp_kadiweu.model.switchportrange_set.first(
            ).name_format.format(
                self.cisco_sp_kadiweu.model.switchportrange_set.first(
                ).end+qty+qty))

    def test_get_unavailable_ports(self):
        """Test if get_unavailable_ports returns all ports that are not available.
        """
        self.assertEqual(set(self.cisco_sp_kadiweu.get_unavailable_ports()),
                         set([self.port_sp_kadiweu_2, self.port_sp_kadiweu_1,
                              self.port_sp_kadiweu_3, self.port_sp_kadiweu_4]))
