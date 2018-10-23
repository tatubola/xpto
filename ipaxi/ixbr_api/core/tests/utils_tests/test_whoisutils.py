from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase

from ...utils.whoisutils import INEXISTENT_ASN, get_whois, parse_whois


class Test_whoisutils(TestCase):

    def test_get_whois_success(self):
        self.assertIsNotNone(get_whois(62000))

    def test_get_whois_failure_with_string(self):
        with self.assertRaisesMessage(ValidationError, INEXISTENT_ASN):
            get_whois("62000")

    @patch('ixbr_api.core.utils.whoisutils.get_whois')
    def test_parse_whois_success(self, mock_get_whois):
        mock_get_whois.return_value = b'% Information related to \'AS61952 - AS62463\'\n\nas-block:       AS61952 - AS62463\ndescr:          RIPE NCC ASN block\nremarks:        These AS Numbers are assigned to network operators in the RIPE NCC service region.\nmnt-by:         RIPE-NCC-HM-MNT\ncreated:        2013-06-13T15:34:28Z\nlast-modified:  2014-02-24T13:15:18Z\nsource:         RIPE\n\n% This query was served by the RIPE Database Query Service version 1.90 (BLAARKOP)\n\n\n'
        something_to_test_now = parse_whois(get_whois(62000))
        self.assertIsInstance(something_to_test_now, list)
        self.assertIsInstance(something_to_test_now[0], tuple)

    def test_parse_whois_failure_with_not_valid_whois_content(self):
        with self.assertRaisesMessage(ValidationError, INEXISTENT_ASN):
            parse_whois(None)

    def test_parse_whois_failure_with_blank_whois_content(self):
        with self.assertRaisesMessage(ValidationError, INEXISTENT_ASN):
            parse_whois(b'')
