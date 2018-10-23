""" This module run unit tests for the endpoint /api/tickets/"""

from unittest import (TestCase, TestSuite)
from run import app


class AllTicketsEndPointTest(TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_tickets_endpoint_status_code(self):
        response = self.app.get("/api/tickets/")
        self.assertEqual(response.status_code, 200)

    def test_tickets_endpoint_content(self):
        response = self.app.get("/api/tickets/")
        self.assertTrue(b'assunto' in response.data)

    def suite():
        suite = TestSuite()
        suite.addTest(AllTicketsEndPointTest(
                                         'test_tickets_endpoint_status_code'))
        suite.addTest(AllTicketsEndPointTest('test_tickets_endpoint_content'))
        return suite
