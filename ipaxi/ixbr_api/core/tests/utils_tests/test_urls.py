from django.core.urlresolvers import resolve
from django.test import TestCase


class HomeViewTestCase(TestCase):

    def test_root_url_uses_home(self):
        """
        Test that the root of 'core' app resolves to the Home view
        """
        root = resolve('/core/')
        self.assertEqual(root.func.__name__, 'HomeView')

    def test_home_url(self):
        """
        Test that the URL for Home resolves to the correct view function
        """
        root = resolve('/core/home/')
        self.assertEqual(root.func.__name__, 'HomeView')


class ASURLsTestCase(TestCase):
    def test_search_as_url(self):
        """
        Test that the URL for AS search resolves to the correct view function
        """
        as_search = resolve('/core/as/search/')

        self.assertEqual(as_search.func.__name__, 'ASSearchView')

    def test_as_detail_url(self):
        """
        Test that the URL for the AS Detail page resolves to the correct view
        function
        """
        as_detail = resolve('/core/as/57976/')

        self.assertEqual(as_detail.func.__name__, 'ASDetailView')
        self.assertEqual(int(as_detail.kwargs['asn']), 57976)

    def test_as_whois_url(self):
        """
        Test the correctitude of the AS Whois info page
        """
        as_whois = resolve('/core/as/57976/whois/')

        self.assertEqual(as_whois.func.__name__, 'ASWhoisView')
        self.assertEqual(int(as_whois.kwargs['asn']), 57976)


class IXURLsTestCase(TestCase):
    def test_ix_detail_url(self):
        """
        Test that the URL for IX detail resolves to the corret ciew function
        """
        ix_detail = resolve("/core/ix/sp/")

        self.assertEqual(ix_detail.func.__name__, 'IXDetailView')
        self.assertEqual(ix_detail.kwargs['code'], 'sp')

    def test_ix_as_detail_url(self):
        """
        Test that the information page for an AS in an IX resolves correctly
        """
        ix_as_detail = resolve("/core/ix/sp/57976/")

        self.assertEqual(ix_as_detail.func.__name__, 'ASIXDetailView')
        self.assertEqual(ix_as_detail.kwargs['code'], 'sp')
        self.assertEqual(int(ix_as_detail.kwargs['asn']), 57976)

    def test_ix_stats_url(self):
        """
        Test that the URL for IXStats resolves to the correct view function
        """
        ix_stats = resolve("/core/ix/sp/57976/stats/")

        self.assertEqual(ix_stats.func.__name__, 'IXStatsView')
        self.assertEqual(ix_stats.kwargs['code'], 'sp')
        self.assertEqual(int(ix_stats.kwargs['asn']), 57976)
