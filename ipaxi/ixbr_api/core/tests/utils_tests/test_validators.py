from django.core.exceptions import ValidationError
from django.test import TestCase

from ...validators import (USUAL_MAC_ADDRESS, validate_as_number,
                           validate_ipv4_network, validate_ipv6_network,
                           validate_ipv46_network, validate_ix_code,
                           validate_ix_fullname, validate_ix_shortname,
                           validate_mac_address, validate_only_lowercase,
                           validate_pix_code, validate_url_format,)


class Test_validate_as_number(TestCase):
    def test_negative_as_number(self):
        with self.assertRaisesMessage(ValidationError,
                                      'Enter a valid AS number.'):
            validate_as_number(-1)

    def test_as_number_0(self):
        with self.assertRaisesMessage(ValidationError,
                                      'Enter a valid AS number.'):
            validate_as_number(0)

    def test_valid_16bits_as_number(self):
        valids = (7, 376, 590, 698, 1213, 1234, 1659, 1768, 1780, 1924, 2489,
                  2529, 3363, 3557, 3741, 4058, 4143, 10392, 10394, 10413,
                  10576, 10758, 10834, 10993, 11416, 11499, 11664, 12127,
                  13225, 13592, 13879, 13930, 13999, 14318, 14624, 14846,
                  15257, 15400, 15826, 16215, 16742, 17330, 17399, 19688,
                  21889, 22134, 22305, 22502, 22707, 23075, 23361, 26130,
                  26625, 27599, 29675, 35840, 48128)
        for v in valids:
            self.assertIsNone(validate_as_number(v))

    def test_invalid_16bits_as_number(self):
        invalids = (0, 64508, 64511, 65535)
        for i in invalids:
            with self.assertRaisesMessage(ValidationError,
                                          'Enter a valid AS number.'):
                    validate_as_number(i)

    def test_valid_32bits_as_number(self):
        valids = (7, 376, 590, 698, 1213, 1234, 1659, 1768, 1780, 1924, 2489,
                  2529, 3363, 3557, 3741, 4058, 4143, 10392, 10394, 10413,
                  10576, 10758, 10834, 10993, 11416, 11499, 11664, 12127,
                  13225, 13592, 13879, 13930, 13999, 14318, 14624, 14846,
                  15257, 15400, 15826, 16215, 16742, 17330, 17399, 19688,
                  21889, 22134, 22305, 22502, 22707, 23075, 23361, 26130,
                  26625, 27599, 29675, 35840, 48128, 134557, 135581, 137530,
                  196608, 198656, 199680, 204288, 205212, 206236, 263680,
                  264605, 393216, 397213, 4199999999)
        for v in valids:
            self.assertIsNone(validate_as_number(v))

    def test_invalid_32bits_as_number(self):
        invalids = (0, 64508, 4294967295, 4294967299)
        for i in invalids:
            with self.assertRaisesMessage(ValidationError,
                                          'Enter a valid AS number.'):
                validate_as_number(i)


class Test_validate_mac_address(TestCase):
    def test_valid_mac_addresses(self):
        valids = ('00:00:00:00:00:00', '01:23:45:67:89:ab', '1:2:3:4:5:6',
                  'ff:ff:ff:ff:ff:ff', '0012:fA2B:AA87', '1.2.3.4.5.6',
                  'ff-ff-ff-ff-ff-ff', '1-2-3-4-5-6', 'ff.ff.ff.ff.ff.ff',
                  '0012.fA2B.AA87', '0012-fA2B-AA87', 'aaaaaaaaaaaa',
                  'BBBBBBBBBBBB', 'abababababab', '01.02.03.04.05.06')
        for v in valids:
            self.assertIsNone(validate_mac_address(v))

    def test_invalid_mac_addresses(self):
        invalids = ('', '"', "'", 'abc1', 'XYZ', ' ', 'IJK2', '123', '.',
                    'São Paulo', 'Rio de Janeiro', '21:fA2BF:AA87',
                    '22:22:ff:ff:F0:ffF', '54:12:fc:ab:z0:ff',
                    '54:12:fc:ab:z0:ff:54:12:fc:ab:z0:ff',)
        for i in invalids:
            with self.assertRaisesMessage(ValidationError, USUAL_MAC_ADDRESS):
                validate_mac_address(i)
                raise ValueError('Did not raise an exception: "%s"' % i)


class Test_validate_only_lowercase(TestCase):
    def test_valid_lowercase(self):
        valids = ('test', 'saopaulo', 'empty')
        for v in valids:
            self.assertIsNone(validate_only_lowercase(v))

    def test_invalid_lowercase(self):
        invalids = ('', '"', "'", 'abc1', 'XYZ', ' ', 'IJK2', '123', '.',
                    'São Paulo', 'Rio de Janeiro')
        for i in invalids:
            with self.assertRaisesMessage(ValidationError,
                                          'Allowed only ASCII lowercase '
                                          'characters.'):
                validate_only_lowercase(i)
                raise ValueError('Did not raise an exception: "%s"' % i)


class Test_validate_ipv46_network(TestCase):
    """Based on stable/1.10.x/tests/forms_tests/field_tests
    /test_genericipaddressfield.py"""

    def test_generic_ipnetwork_as_generic(self):
        # The edge cases of the IPv6 validation code are not deeply tested
        # here, they are covered in the tests for django.utils.ipv6
        self.assertIsNone(validate_ipv46_network('127.0.0.1'))
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('foo')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('127.0.0.')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1.2.3.4.5')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('256.125.1.5')
        self.assertIsNone(validate_ipv46_network('fe80::223:6cff:fe8a:2e8a'))
        self.assertIsNone(validate_ipv46_network('2a02::223:6cff:fe8a:2e8a'))
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('12345:2:3:4')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1::2:3::4')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('foo::223:6cff:fe8a:2e8a')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1::2:3:4:5:6:7:8')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1:2')
        self.assertIsNone(validate_ipv46_network('127.0.0.1/32'))
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('foo/32')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('127.0.0./32')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1.2.3.4.5/32')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('256.125.1.5/32')
        self.assertIsNone(validate_ipv46_network('fe80::223:6cff:fe8a:2e8a/128'))
        self.assertIsNone(validate_ipv46_network('2a02::223:6cff:fe8a:2e8a/128'))
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('12345:2:3:4/128')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1::2:3::4/128')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('foo::223:6cff:fe8a:2e8a/128')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1::2:3:4:5:6:7:8/128')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1:2/128')
        self.assertIsNone(validate_ipv46_network('127.0.0.1/32'))
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('foo/32')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('127.0.0./32')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1.2.3.4.5/32')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('256.125.1.5/32')
        self.assertIsNone(validate_ipv46_network('fe80::223:6cff:fe8a:2e8a/128'))
        self.assertIsNone(validate_ipv46_network('2a02::223:6cff:fe8a:2e8a/128'))
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('12345:2:3:4/128')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1::2:3::4/128')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('foo::223:6cff:fe8a:2e8a/128')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1::2:3:4:5:6:7:8/128')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1:2/128')
        self.assertIsNone(validate_ipv46_network('127.0.0.1/0'))
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('foo/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('127.0.0./0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1.2.3.4.5/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('256.125.1.5/0')
        self.assertIsNone(validate_ipv46_network('fe80::223:6cff:fe8a:2e8a/0'))
        self.assertIsNone(validate_ipv46_network('2a02::223:6cff:fe8a:2e8a/0'))
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('12345:2:3:4/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1::2:3::4/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('foo::223:6cff:fe8a:2e8a/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1::2:3:4:5:6:7:8/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1:2/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('127.0.0.1/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('foo/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('127.0.0./-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1.2.3.4.5/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('256.125.1.5/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('fe80::223:6cff:fe8a:2e8a/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('2a02::223:6cff:fe8a:2e8a/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('12345:2:3:4/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1::2:3::4/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('foo::223:6cff:fe8a:2e8a/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1::2:3:4:5:6:7:8/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1:2/-1')

    def test_generic_ipnetwork_as_generic_not_required(self):
        self.assertIsNone(validate_ipv46_network('127.0.0.1'))
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('foo')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('127.0.0.')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1.2.3.4.5')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('256.125.1.5')
        self.assertIsNone(validate_ipv46_network('fe80::223:6cff:fe8a:2e8a'))
        self.assertIsNone(validate_ipv46_network('2a02::223:6cff:fe8a:2e8a'))
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('12345:2:3:4')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1::2:3::4')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('foo::223:6cff:fe8a:2e8a')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1::2:3:4:5:6:7:8')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1:2')
        self.assertIsNone(validate_ipv46_network('127.0.0.1/32'))
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('foo/32')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('127.0.0./32')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1.2.3.4.5/32')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('256.125.1.5/32')
        self.assertIsNone(validate_ipv46_network('fe80::223:6cff:fe8a:2e8a/128'))
        self.assertIsNone(validate_ipv46_network('2a02::223:6cff:fe8a:2e8a/128'))
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('12345:2:3:4/128')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1::2:3::4/128')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('foo::223:6cff:fe8a:2e8a/128')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1::2:3:4:5:6:7:8/128')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1:2/128')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('127.0.0.1/33')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('foo/33')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('127.0.0./33')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1.2.3.4.5/33')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('256.125.1.5/33')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('fe80::223:6cff:fe8a:2e8a/129')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('2a02::223:6cff:fe8a:2e8a/129')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('12345:2:3:4/129')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1::2:3::4/129')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('foo::223:6cff:fe8a:2e8a/129')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1::2:3:4:5:6:7:8/129')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1:2/129')
        self.assertIsNone(validate_ipv46_network('127.0.0.1/0'))
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('foo/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('127.0.0./0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1.2.3.4.5/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('256.125.1.5/0')
        self.assertIsNone(validate_ipv46_network('fe80::223:6cff:fe8a:2e8a/0'))
        self.assertIsNone(validate_ipv46_network('2a02::223:6cff:fe8a:2e8a/0'))
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('12345:2:3:4/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1::2:3::4/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('foo::223:6cff:fe8a:2e8a/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1::2:3:4:5:6:7:8/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1:2/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('127.0.0.1/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('foo/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('127.0.0./-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1.2.3.4.5/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('256.125.1.5/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('fe80::223:6cff:fe8a:2e8a/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('2a02::223:6cff:fe8a:2e8a/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('12345:2:3:4/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1::2:3::4/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('foo::223:6cff:fe8a:2e8a/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1::2:3:4:5:6:7:8/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 or IPv6 network.'"):
            validate_ipv46_network('1:2/-1')


class Test_validate_ipv4_network(TestCase):
    """Based on stable/1.10.x/tests/
    forms_tests/field_tests/test_genericipaddressfield.py"""

    def test_generic_ipnetwork_as_ipv4_only(self):
        self.assertIsNone(validate_ipv4_network('127.0.0.1'))
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('foo')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('127.0.0.')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('1.2.3.4.5')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('256.125.1.5')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('fe80::223:6cff:fe8a:2e8a')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('2a02::223:6cff:fe8a:2e8a')
        self.assertIsNone(validate_ipv4_network('127.0.0.1/32'))
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('foo/32')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('127.0.0./32')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('1.2.3.4.5/32')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('256.125.1.5/32')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('fe80::223:6cff:fe8a:2e8a/32')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('2a02::223:6cff:fe8a:2e8a/32')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            self.assertIsNone(validate_ipv4_network('127.0.0.1/33'))
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('foo/33')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('127.0.0./33')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('1.2.3.4.5/33')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('256.125.1.5/33')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('fe80::223:6cff:fe8a:2e8a/129')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('2a02::223:6cff:fe8a:2e8a/129')
        self.assertIsNone(validate_ipv4_network('127.0.0.1/0'))
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('foo/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('127.0.0./0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('1.2.3.4.5/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('256.125.1.5/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('fe80::223:6cff:fe8a:2e8a/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('2a02::223:6cff:fe8a:2e8a/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            self.assertIsNone(validate_ipv4_network('127.0.0.1/-1'))
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('foo/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('127.0.0./-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('1.2.3.4.5/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('256.125.1.5/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('fe80::223:6cff:fe8a:2e8a/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv4 network.'"):
            validate_ipv4_network('2a02::223:6cff:fe8a:2e8a/-1')


class Test_validate_ipv6_network(TestCase):
    """Based on stable/1.10.x/tests/
    forms_tests/field_tests/test_genericipaddressfield.py"""

    def test_generic_ipnetwork_as_ipv6_only(self):
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('127.0.0.1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('foo')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('127.0.0.')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('1.2.3.4.5')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('256.125.1.5')
        self.assertIsNone(validate_ipv6_network('fe80::223:6cff:fe8a:2e8a'))
        self.assertIsNone(validate_ipv6_network('2a02::223:6cff:fe8a:2e8a'))
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('12345:2:3:4')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('1::2:3::4')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('foo::223:6cff:fe8a:2e8a')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('1::2:3:4:5:6:7:8')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('1:2')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('127.0.0.1/32')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('foo/32')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('127.0.0./32')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('1.2.3.4.5/32')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('256.125.1.5/32')
        self.assertIsNone(validate_ipv6_network('fe80::223:6cff:fe8a:2e8a/128'))
        self.assertIsNone(validate_ipv6_network('2a02::223:6cff:fe8a:2e8a/128'))
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('12345:2:3:4/128')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('1::2:3::4/128')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('foo::223:6cff:fe8a:2e8a/128')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('1::2:3:4:5:6:7:8/128')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('1:2/128')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('127.0.0.1/33')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('foo/33')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('127.0.0./33')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('1.2.3.4.5/33')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('256.125.1.5/33')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('fe80::223:6cff:fe8a:2e8a/129')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('2a02::223:6cff:fe8a:2e8a/129')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('12345:2:3:4/129')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('1::2:3::4/129')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('foo::223:6cff:fe8a:2e8a/129')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('1::2:3:4:5:6:7:8/129')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('1:2/129')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('127.0.0.1/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('foo/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('127.0.0./0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('1.2.3.4.5/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('256.125.1.5/0')
        self.assertIsNone(validate_ipv6_network('fe80::223:6cff:fe8a:2e8a/0'))
        self.assertIsNone(validate_ipv6_network('2a02::223:6cff:fe8a:2e8a/0'))
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('12345:2:3:4/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('1::2:3::4/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('foo::223:6cff:fe8a:2e8a/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('1::2:3:4:5:6:7:8/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('1:2/0')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('127.0.0.1/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('foo/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('127.0.0./-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('1.2.3.4.5/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('256.125.1.5/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('fe80::223:6cff:fe8a:2e8a/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('2a02::223:6cff:fe8a:2e8a/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('12345:2:3:4/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('1::2:3::4/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('foo::223:6cff:fe8a:2e8a/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('1::2:3:4:5:6:7:8/-1')
        with self.assertRaisesMessage(ValidationError,
                                      "'Enter a valid IPv6 network.'"):
            validate_ipv6_network('1:2/-1')


class Test_url_format(TestCase):
    def test_not_ok_format(self):
        with self.assertRaisesMessage(ValidationError,
                                      'Enter a valid URL.'):
            validate_url_format('abxse')

    def test_ok_format(self):
        validate_url_format('http://www.teste.com')


class Test_ix_formats(TestCase):
    def test_invalid_ix_code(self):
        with self.assertRaisesMessage(ValidationError,
                                      'Allowed only two-four alphabetic '
                                      'lowercase characters'):
            validate_ix_code('sasasas')

    def test_valid_ix_code(self):
        validate_ix_code('sp')

    def test_valid_ix_shortname(self):
        validate_ix_shortname('saopaulo.sp')

    def test_invalid_ix_shortname(self):
        with self.assertRaisesMessage(ValidationError,
                                      'Allowed only two groups ' +
                                      'of 3-13 and 2-2 alphabetic' +
                                      ' lowercase characters separated by dot'):
            validate_ix_shortname('Sao Paulo - SP')

    def test_valids_ix_fullname(self):
        valids = ('Acre - AC', 'Alagoas - AL', 'Amapa - AP', 'Amazonas - AM',
                  'Bahia - BA', 'Ceara - CE', 'Distrito Federal - DF',
                  'Espirito Santo - ES', 'Goias - GO', 'Maranhao - MA',
                  'Mato Grosso - MT', 'Mato Grosso do Sul - MS',
                  'Minas Gerais - MG', 'Para - PA', 'Paraiba - PB',
                  'Parana - PR', 'Pernambuco - PE', 'Piaui - PI',
                  'Rio de Janeiro - RJ', 'Rio Grande do Sul - RS',
                  'Rio Grande do Norte - RN', 'Rondonia - RO',
                  'Roraima - RR', 'Santa Catarina - SC', 'Sao Paulo - SP',
                  'Sergipe - SE', 'Tocantins - TO', 'São Paulo - SP')
        for valid in valids:
            validate_ix_fullname(valid)


class Test_pix_formats(TestCase):
    def test_invalid_pix_code(self):
        with self.assertRaisesMessage(ValidationError,
                                      'Allowed only three-max_field_length'
                                      ' characters with first uppercase'):
            validate_pix_code('sasasas')

    def test_valid_pix_code(self):
        validate_pix_code('EQUINIX-SP2')
