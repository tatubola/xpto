from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test.client import Client
from model_mommy import mommy

import ixbr_api.core.use_cases.create_dio_ports_use_case as create_dio_ports_use_case

from ...models import DIO, PIX, DIOPort
from ..login import DefaultLogin


class CreateDIOPortsTest(TestCase):

    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch(
            'ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
        p.start()
        self.addCleanup(p.stop)

    def test_create_dio_ports_successfully(self):
        ix_position_pattern = "abcdefghijk{0}{1}{2}"
        datacenter_position_pattern = "abcdefghijk/{0}{1}{2}"
        number_of_ports = 6
        dio = mommy.make(DIO)
        last_ticket = 50
        create_dio_ports_use_case.create_dio_ports(ix_position_pattern,
                                                   datacenter_position_pattern,
                                                   number_of_ports,
                                                   dio,
                                                   last_ticket,
                                                   self.superuser)

        dio_ports = DIOPort.objects.all().order_by('datacenter_position')
        self.assertEqual(dio_ports[0].datacenter_position, "abcdefghijk/123")
        self.assertEqual(dio_ports[0].ix_position, "abcdefghijk123")
        self.assertEqual(dio_ports[0].dio, dio)

        self.assertEqual(dio_ports[1].datacenter_position, "abcdefghijk/456")
        self.assertEqual(dio_ports[1].ix_position, "abcdefghijk456")
        self.assertEqual(dio_ports[1].dio, dio)

    def test_create_dio_ports_with_number_of_ports_not_divisible(self):
        ix_position_pattern = "{0}abcdefghijk{1}{2}"
        datacenter_position_pattern = "{0}abc{1}def{2}ghijk"
        number_of_ports = 7
        dio = mommy.make(DIO)
        last_ticket = 50
        with self.assertRaisesRegexp(
            ValidationError,
                create_dio_ports_use_case.ERROR_NUMBER_OF_PORTS_NOT_DIVISIBLE):
                create_dio_ports_use_case.create_dio_ports(
                    ix_position_pattern,
                    datacenter_position_pattern,
                    number_of_ports,
                    dio,
                    last_ticket,
                    self.superuser)

    def test_create_dio_ports_with_patterns_with_different_number_of_groups(self):
        ix_position_pattern = "{0}abcdefghijk{1}{2}"
        datacenter_position_pattern = "{0}abc{1}def{2}gh{3}ijk"
        number_of_ports = 12
        dio = mommy.make(DIO)
        last_ticket = 50
        with self.assertRaisesRegexp(
            ValidationError,
            (create_dio_ports_use_case
             .ERROR_PATTERNS_WITH_DIFFERENT_NUMBER_OF_GROUPS)):
                create_dio_ports_use_case.create_dio_ports(
                    ix_position_pattern,
                    datacenter_position_pattern,
                    number_of_ports,
                    dio,
                    last_ticket,
                    self.superuser)

    def test_create_dio_ports_with_empty_dc_position(self):
        datacenter_position_pattern = "{0}abcdefghijk{2}{1}"
        ix_position_pattern = ""
        number_of_ports = 6
        dio = mommy.make(DIO)
        last_ticket = 50

        create_dio_ports_use_case.create_dio_ports(ix_position_pattern,
                                                   datacenter_position_pattern,
                                                   number_of_ports,
                                                   dio,
                                                   last_ticket,
                                                   self.superuser)

        dio_ports = list(DIOPort.objects.order_by('ix_position'))
        self.assertEqual(dio_ports[0].datacenter_position, "1abcdefghijk32")
        self.assertEqual(dio_ports[0].ix_position, "")
        self.assertEqual(dio_ports[0].dio, dio)

        self.assertEqual(dio_ports[1].datacenter_position, "4abcdefghijk65")
        self.assertEqual(dio_ports[1].ix_position, "")
        self.assertEqual(dio_ports[1].dio, dio)
