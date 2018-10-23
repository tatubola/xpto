
from ..models import (get_free_ipv4_by_ix, get_free_ipv6_by_ix)
import itertools


def get_free_ips_by_ix(option, ix):
    ips = {}
    ipv6 = None
    ipv4 = None
    if option == 'only_v4':
        ipv4 = get_free_ipv4_by_ix(ix=ix)[0]

    if option == 'only_v6':
        ipv6 = get_free_ipv6_by_ix(ix=ix)[0]

    elif option == 'v4_and_v6':
        free_ipv4 = get_free_ipv4_by_ix(ix=ix)
        free_ipv6 = get_free_ipv6_by_ix(ix=ix)

        ips_combination = itertools.product(free_ipv4, free_ipv6)
        ipv4, ipv6 = next((
            ips for ips in ips_combination
            if ips[0].last_group() == ips[1].last_group()), (None, None))

        if ipv4 is None:
            ipv4 = free_ipv4[0]
            ipv6 = free_ipv6[0]

    ips['ipv4'] = ipv4
    ips['ipv6'] = ipv6

    return ips
