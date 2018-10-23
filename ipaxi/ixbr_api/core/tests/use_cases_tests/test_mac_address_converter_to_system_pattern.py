from django.test import TestCase

from ...use_cases.mac_address_converter_to_system_pattern import (
    MACAddressConverterToSystemPattern,)


class MACAddressConverterToSystemPatternTestCase(TestCase):
    def setUp(self):
        self.conversor = MACAddressConverterToSystemPattern

    def test_mac_address_converter_success(self):
        to_convert = ('00:00:00:00:00:00', '01:23:45:67:89:ab', '1:2:3:4:5:6',
                      'ff:ff:ff:ff:ff:ff', '0012:fA2B:AA87', '1.2.3.4.5.6',
                      'ff-ff-ff-ff-ff-ff', '1-2-3-4-5-6', 'ff.ff.ff.ff.ff.ff',
                      '0012.fA2B.AA87', '0012-fA2B-AA87', 'aaaaaaaaaaaa',
                      'BBBBBBBBBBBB', 'abababababab', '01.02.03.04.05.06')
        converted = ('00:00:00:00:00:00', '01:23:45:67:89:ab',
                     '01:02:03:04:05:06', 'ff:ff:ff:ff:ff:ff',
                     '00:12:fa:2b:aa:87', '01:02:03:04:05:06',
                     'ff:ff:ff:ff:ff:ff', '01:02:03:04:05:06',
                     'ff:ff:ff:ff:ff:ff', '00:12:fa:2b:aa:87',
                     '00:12:fa:2b:aa:87', 'aa:aa:aa:aa:aa:aa',
                     'bb:bb:bb:bb:bb:bb', 'ab:ab:ab:ab:ab:ab',
                     '01:02:03:04:05:06')
        for index, value in enumerate(to_convert):
            self.assertEqual(
                self.conversor(value).mac_address_converter(),
                converted[index])
