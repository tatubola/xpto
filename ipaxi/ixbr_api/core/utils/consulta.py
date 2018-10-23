import sqlite3
from functools import reduce
from re import search


class MAC(object):
    """
    This class implements a connection and a query to the sqlite that
    contains data regarding mac address vendors
    """
    def __init__(self, sqlite_file_name):
        sqlite_path = "/app/ix/oui/" + sqlite_file_name
        db = sqlite3.connect(sqlite_path)
        self.cursor = db.cursor()

    def get_vendor(self, mac_address):
        """ This method execute a query in sqlite to find the vendor of a
        ethernet card.

        :param mac_address: MAC Address to find
        :return: The vendor of a given ethernet card
        """
        mac_norm = self.__mac_normalization(mac_address)
        vendor_query = 'SELECT vendor FROM macvendors WHERE mac=\'' + mac_norm \
                       + "\'"

        res = self.cursor.execute(vendor_query).fetchall()
        if len(res) > 0:
            return res[0][0]
        else:
            return None

    @staticmethod
    def __mac_normalization(mac_address):
        """ This method receives a mac address which can have fields
        separeted by ':', '-' or '.'
        It will get first 3 fields (or first 6 characters) and return it in
        upcase.

        :param mac_address: The mac address to be normalized
        :return: A string with first characters of a mac address
        """

        regex = r"(:){1,}|(-){1,}|(\.){1,}"

        if mac_address.count(':') >= 2 or mac_address.count('-') >= 2 or \
                mac_address.count('.') >= 2:

            matches = search(regex, mac_address)

            if matches.group() == ':':
                mac_parts = mac_address.split(':')
            elif matches.group() == '-':
                mac_parts = mac_address.split('-')
            elif matches.group() == '.':
                mac_parts = mac_address.split('.')
        else:
            mac_parts = mac_address

        return reduce(lambda x, y: x + y, mac_parts).upper()[0:6]
