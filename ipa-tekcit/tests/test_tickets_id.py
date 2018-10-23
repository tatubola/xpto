""" This module run unit tests for the endpoint /api/tickets/<ticket_ID>"""

from unittest import (TestCase, TestSuite)
from run import app


class SpecificTicketEndPointTest(TestCase):

    def setUp(self):
        self.ticket_to_test = "27639"
        self.app = app.test_client()

    def test_tickets_endpoint_status_code(self):
        response = self.app.get("/api/tickets/" + self.ticket_to_test)
        self.assertEqual(response.status_code, 200)

    def test_tickets_endpoint_content(self):
        response = self.app.get("/api/tickets/" + self.ticket_to_test)
        self.assertTrue(b'ticket_info' in response.data)

    def suite():
        suite = TestSuite()

        suite.addTest(SpecificTicketEndPointTest(
            'test_tickets_endpoint_status_code'))

        suite.addTest(SpecificTicketEndPointTest(
            'test_tickets_endpoint_content'))

        return suite
