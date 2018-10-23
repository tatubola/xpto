from tests import (test_ticket_api, test_tickets_close, test_tickets_id,
                   test_tickets_open)
import unittest
import xmlrunner

def suite():
    suite = unittest.TestSuite()
    suite.addTest(test_ticket_api.AllTicketsEndPointTest.suite())
    suite.addTest(test_tickets_close.ClosedTicketsEndPointTest.suite())
    suite.addTest(test_tickets_id.SpecificTicketEndPointTest.suite())
    suite.addTest(test_tickets_open.OpenTicketsEndPointTest.suite())
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite', testRunner=xmlrunner.XMLTestRunner(
        output='test-reports'))