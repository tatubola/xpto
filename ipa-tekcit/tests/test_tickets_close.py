""" This module run unit tests for the endpoint /api/tickets/closed"""

from unittest import (TestCase, TestSuite)
from run import app


class ClosedTicketsEndPointTest(TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_tickets_endpoint_status_code(self):
        response = self.app.get("/api/tickets/closed/")
        self.assertEqual(response.status_code, 200)

    def test_tickets_endpoint_content(self):
        response = self.app.get("/api/tickets/closed/")
        self.assertTrue(b'fechado' in response.data)

    def test_tickets_endpoint_wrong_content(self):
        response = self.app.get("/api/tickets/closed/")
        self.assertFalse(b'aberto' in response.data)

    def suite():
        suite = TestSuite()

        suite.addTest(ClosedTicketsEndPointTest(
            'test_tickets_endpoint_status_code'))

        suite.addTest(ClosedTicketsEndPointTest(
            'test_tickets_endpoint_content'))

        suite.addTest(ClosedTicketsEndPointTest(
            'test_tickets_endpoint_wrong_content'))

        return suite
