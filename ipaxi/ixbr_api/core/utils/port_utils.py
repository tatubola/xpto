from collections import OrderedDict
from re import sub


def port_sorting(port_dict, descendent=False):
    '''
    Receives an unordered dictionary with port as key.
    Port naming accepted to order:
        CISCO Port Naming -   Eg. TenGigEY/Y/Y/Y
        Extreme Port Naming - Eg. XE-Y/Y/Y

    :param port_dict: A dictionary where the port name is the key.
    :param descendent: Inform a reverse sorting.
    :return: A OrderedDict object
    '''

    clean_port_name_regex = r'([a-zA-Z]|(?:\s)|(?:-))'
    pre_process_dict = {}
    ordered = OrderedDict()

    for port_name in port_dict.keys():
        cleaned_port_name = sub(clean_port_name_regex, '', port_name)
        pre_process_dict[int(cleaned_port_name.replace('/', '0'))] = port_name

    for port_no in sorted(pre_process_dict.keys(), reverse=descendent):
        ordered[pre_process_dict[port_no]] = \
            port_dict[pre_process_dict[port_no]]

    return ordered
