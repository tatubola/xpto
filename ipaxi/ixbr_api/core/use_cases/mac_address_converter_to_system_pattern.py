import re

from ..utils.regex import Regex

regex = Regex()


class MACAddressConverterToSystemPattern(object):
    def __init__(self, mac_to_convert):
        self._MAC_PATTERN_1 = regex._MAC_PATTERN_1
        self._MAC_PATTERN_2 = regex._MAC_PATTERN_2
        self._MAC_PATTERN_3 = regex._MAC_PATTERN_3
        self.mac_to_convert = mac_to_convert.lower()

    def mac_address_converter_treatment(self, pattern):
        if pattern == self._MAC_PATTERN_1:
            candidates = re.findall('\w+', self.mac_to_convert)
            for i in range(0, len(candidates)):
                if len(candidates[i]) == 1:
                    candidates[i] = '0{0}'.format(candidates[i])
            raw_mac_address = ''.join(candidates)
        else:
            raw_mac_address = re.sub(r'\W+', '', self.mac_to_convert)

        return re.sub("(.{2})", "\\1:", raw_mac_address)[:-1]

    def mac_address_converter(self):
        if not isinstance(self.mac_to_convert, str):
            raise TypeError("'{0}' is not a str".format(self.mac_to_convert))

        if re.findall(self._MAC_PATTERN_1, self.mac_to_convert):
            return self.mac_address_converter_treatment(self._MAC_PATTERN_1)
        elif re.findall(self._MAC_PATTERN_2, self.mac_to_convert):
            return self.mac_address_converter_treatment(self._MAC_PATTERN_2)
        elif re.findall(self._MAC_PATTERN_3, self.mac_to_convert):
            return self.mac_address_converter_treatment(self._MAC_PATTERN_3)
