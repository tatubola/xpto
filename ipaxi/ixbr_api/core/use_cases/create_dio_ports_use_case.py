import re
from itertools import zip_longest

from django.core.exceptions import ValidationError

from ..models import DIOPort

PATTERN = r"\{(\d+)\}"
ERROR_NUMBER_OF_PORTS_NOT_DIVISIBLE = "The total number of ports must \
                                       be divisible by the number of ports \
                                       assined to each DIO"
ERROR_PATTERNS_WITH_DIFFERENT_NUMBER_OF_GROUPS = "IX Position and Datacenter \
                                                 position patterns must have \
                                                 the same number of groups"
ERROR_PATTERN_DONT_MATCH = "Datacenter position do not have any group"


def create_dio_ports(ix_position_pattern, dc_position_pattern,
                     number_of_ports, dio, last_ticket, user):
    """ Method to create range of DIO Ports according to IX position and datacenter position patterns

    Args:
        ix_position_pattern: string -> A pattern that represents the IX
                                       Position for each group of ports
        dc_position_pattern: string -> A pattern that represents the
                                               datacenter Position for each
                                               group of ports
        number_of_ports: Integer -> number of ports
        dio: DIO -> The DIO whose ports are being created
        last_ticket -> The last ticket
        user -> User logged in the system
    Returns:
        None
    """
    pattern = re.compile(PATTERN)

    number_of_matches_ix_position = len(pattern.findall(ix_position_pattern))
    number_of_matches_dc_position = len(pattern.findall(dc_position_pattern))

    if number_of_matches_dc_position == 0:
        raise ValidationError(ERROR_PATTERN_DONT_MATCH)

    if number_of_matches_ix_position != 0 and number_of_matches_ix_position != number_of_matches_dc_position:
        raise ValidationError(ERROR_PATTERNS_WITH_DIFFERENT_NUMBER_OF_GROUPS)

    number_of_matches = number_of_matches_dc_position
    if number_of_ports % number_of_matches != 0:
        raise ValidationError(ERROR_NUMBER_OF_PORTS_NOT_DIVISIBLE)

    matches_ix_position = pattern.findall(ix_position_pattern)
    matches_dc_position = pattern.findall(dc_position_pattern)

    for i in range(number_of_ports // number_of_matches):
        dc_position, ix_position = dc_position_pattern, ix_position_pattern
        offset = i * number_of_matches + 1

        for match_ix_position, match_dc_position in zip_longest(matches_ix_position, matches_dc_position):
            dc_position = pattern.sub(str(int(match_dc_position) + offset), dc_position, 1)
            if(match_ix_position):
                ix_position = pattern.sub(str(int(match_ix_position) + offset), ix_position, 1)

        new_dio_port = DIOPort.objects.create(
            dio=dio,
            ix_position=ix_position,
            datacenter_position=dc_position,
            last_ticket=last_ticket,
            modified_by=user)
