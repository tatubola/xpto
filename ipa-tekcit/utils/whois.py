""" This script gets whois information about a given AS and returns it parsed
"""
# System imports
import re
from subprocess import (CalledProcessError, PIPE, run)

# Third-party imports
import json

# Local source tree imports


class WhoIsHandler(object):

    def __init__(self, asn):
        arg = str(asn)
        data = run(['whois', 'AS' + arg], stdout=PIPE)

        self.asn = asn
        self.who_is_output = data.stdout.split(b'\n')

    def who_is_to_dict(self):
        """ Process whois output and creates a dict with data

        Returns: A dict with all data collected from whois tool

        """

        who_is_dict = {}
        for line in self.who_is_output:
            try:
                decoded_line = line.decode("utf-8")
            except:
                decoded_line = line.decode("latin1")

            div = decoded_line.split(":")
            if len(div) == 2:
                div[1] = re.sub("(^\s+)", '', div[1].rstrip())
                who_is_dict[div[0]] = div[1]
            else:
                continue

        return who_is_dict

    def is_foreign(self):
        """ Check if a given AS is from BR or not

        Returns: True if AS is from outside BR or False otherwise

        """
        who_is_dict = self.who_is_to_dict()

        if "Country" in who_is_dict.keys():
            if who_is_dict['Country'] == 'BR':
                return False
            else:
                return True
        elif "country" in who_is_dict.keys():
            if who_is_dict['country'] == 'BR':
                return False
            else:
                return True
        else:
            return True
