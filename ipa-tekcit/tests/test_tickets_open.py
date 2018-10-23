""" This module run unit tests for the endpoint /api/tickets/"""

from unittest import (TestCase, TestSuite)
from run import app


class OpenTicketsEndPointTest(TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_tickets_endpoint_status_code(self):
        response = self.app.get("/api/tickets/open/")
        self.assertEqual(response.status_code, 200)

    def test_tickets_endpoint_content(self):
        response = self.app.get("/api/tickets/open/")
        self.assertTrue(b'aberto' in response.data)

    def test_tickets_endpoint_wrong_content(self):
        response = self.app.get("/api/tickets/open/")
        self.assertFalse(b'fechado' in response.data)

    def suite():
        suite = TestSuite()

        suite.addTest(OpenTicketsEndPointTest(
            'test_tickets_endpoint_status_code'))

        suite.addTest(OpenTicketsEndPointTest(
            'test_tickets_endpoint_content'))

        suite.addTest(OpenTicketsEndPointTest(
            'test_tickets_endpoint_wrong_content'))

        return suite