from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from ..models import Bilateral, BilateralPeer
from .tags_use_cases import (check_inner_tag_availability,
                             get_or_create_specific_tag_without_all_service,
                             get_or_create_specific_tag_without_bilateral)


def define_bilateral_case(**kwargs):
    if 'channel_a' in kwargs:
        channel_a = kwargs.pop('channel_a')
    else:
        raise ValueError(_("Two channels must be given"))
    if 'channel_b' in kwargs:
        channel_b = kwargs.pop('channel_b')
    else:
        raise ValueError(_("Two channels must be given"))

    cix = channel_a.cix_type + channel_b.cix_type
    case = -1
    # peer_a or peer_b or neither are qinq
    if cix < 6:
        # peer_a or peer_b is qinq
        if channel_a.cix_type == 3:
            case = 1
        elif channel_b.cix_type == 3:
            case = 2
        # neither peer_a or peer_b are cix
        else:
            case = 0
    # both peer_a and peer_b are cix
    elif cix == 6:
        case = 3
    else:
        raise ValidationError(_("Inconsistent cix_type"))

    return case


def create_bilateral_not_qinq(**kwargs):
    peer_a = kwargs.pop('peer_a')
    peer_b = kwargs.pop('peer_b')
    channel_a = kwargs.pop('channel_a')
    channel_b = kwargs.pop('channel_b')
    ix = kwargs.pop('ix')
    tag = kwargs.pop('tag_a')
    ticket = kwargs.pop('ticket')
    b_type = kwargs.pop('b_type')

    tag_a = get_or_create_specific_tag_without_all_service(
        ix=ix,
        channel=channel_a,
        tag_number=tag)
    tag_b = get_or_create_specific_tag_without_all_service(
        ix=ix,
        channel=channel_b,
        tag_number=tag)

    if not tag_a or not tag_b:
        raise(ValidationError(_("This is not a valid Tag number")))

    else:
        bilateral_peer_a = BilateralPeer.objects.create(
            last_ticket=ticket,
            tag=tag_a,
            customer_channel=channel_a,
            asn=peer_a,
            mac_addresses=list(),
            shortname="b{}".format(peer_a.number),
            status='ALLOCATED')
        bilateral_peer_b = BilateralPeer.objects.create(
            last_ticket=ticket,
            tag=tag_b,
            customer_channel=channel_b,
            asn=peer_b,
            shortname="b{}".format(peer_b.number),
            mac_addresses=list(),
            status='ALLOCATED')

        bilateral = Bilateral.objects.create(
            last_ticket=ticket,
            peer_a=bilateral_peer_a,
            peer_b=bilateral_peer_b,
            bilateral_type=b_type
        )
        tag_a.status = 'PRODUCTION'
        tag_b.status = 'PRODUCTION'
        tag_a.save()
        tag_b.save()
        return bilateral


def create_bilateral_peer_a_qinq(**kwargs):

    peer_a = kwargs.pop('peer_a')
    peer_b = kwargs.pop('peer_b')
    channel_a = kwargs.pop('channel_a')
    channel_b = kwargs.pop('channel_b')
    ix = kwargs.pop('ix')
    tag = kwargs.pop('tag_b')
    tag_a = kwargs.pop('tag_a')
    ticket = kwargs.pop('ticket')
    b_type = kwargs.pop('b_type')
    inner_a = kwargs.pop('inner_a')

    tag_b = get_or_create_specific_tag_without_all_service(
        ix=ix,
        channel=channel_b,
        tag_number=tag)
    tag_a = get_or_create_specific_tag_without_bilateral(
        ix=ix,
        channel=channel_a,
        tag_number=tag_a)

    if not tag_a:
        raise(ValidationError(_("This is not a valid Tag number")))

    if inner_a:
        if not check_inner_tag_availability(inner=inner_a, tag=tag_a, ix=ix):
            raise(ValidationError(_("Invalid inner tag")))

        elif not inner_a == str(tag_b.tag):
            raise(ValidationError(
                _("Inner tag and Tag must have the same number")))

    bilateral_peer_a = BilateralPeer.objects.create(
        last_ticket=ticket,
        tag=tag_a,
        inner=inner_a,
        customer_channel=channel_a,
        asn=peer_a,
        shortname="b{}".format(peer_a.number),
        mac_addresses=list(),
        status='ALLOCATED')
    bilateral_peer_b = BilateralPeer.objects.create(
        last_ticket=ticket,
        tag=tag_b,
        customer_channel=channel_b,
        asn=peer_b,
        shortname="b{}".format(peer_b.number),
        mac_addresses=list(),
        status='ALLOCATED')

    bilateral = Bilateral.objects.create(
        last_ticket=ticket,
        peer_a=bilateral_peer_a,
        peer_b=bilateral_peer_b,
        bilateral_type=b_type
    )
    tag_a.status = 'PRODUCTION'
    tag_b.status = 'PRODUCTION'
    tag_a.save()
    tag_b.save()
    return bilateral


def create_bilateral_peer_b_qinq(**kwargs):

    peer_a = kwargs.pop('peer_a')
    peer_b = kwargs.pop('peer_b')
    channel_a = kwargs.pop('channel_a')
    channel_b = kwargs.pop('channel_b')
    ix = kwargs.pop('ix')
    tag = kwargs.pop('tag_a')
    tag_b = kwargs.pop('tag_b')
    ticket = kwargs.pop('ticket')
    b_type = kwargs.pop('b_type')
    inner_b = kwargs.pop('inner_b')

    tag_a = get_or_create_specific_tag_without_all_service(
        ix=ix,
        channel=channel_a,
        tag_number=tag)
    tag_b = get_or_create_specific_tag_without_bilateral(
        ix=ix,
        channel=channel_b,
        tag_number=tag_b)

    if not tag_b:
        raise(ValidationError(_("This is not a valid Tag number")))

    if inner_b:
        if not check_inner_tag_availability(inner=inner_b, tag=tag_b, ix=ix):
            raise(ValidationError(_("Invalid inner tag")))

        elif not inner_b == str(tag_a.tag):
            raise(ValidationError(
                _("Inner tag and Tag must have the same number")))

    bilateral_peer_a = BilateralPeer.objects.create(
        last_ticket=ticket,
        tag=tag_a,
        customer_channel=channel_a,
        asn=peer_a,
        shortname="b{}".format(peer_a.number),
        mac_addresses=list(),
        status='ALLOCATED')
    bilateral_peer_b = BilateralPeer.objects.create(
        last_ticket=ticket,
        tag=tag_b,
        inner=inner_b,
        customer_channel=channel_b,
        asn=peer_b,
        shortname="b{}".format(peer_b.number),
        mac_addresses=list(),
        status='ALLOCATED')

    bilateral = Bilateral.objects.create(
        last_ticket=ticket,
        peer_a=bilateral_peer_a,
        peer_b=bilateral_peer_b,
        bilateral_type=b_type
    )

    tag_a.status = 'PRODUCTION'
    tag_b.status = 'PRODUCTION'
    tag_a.save()
    tag_b.save()
    return bilateral


def create_bilateral_a_b_qinq(**kwargs):

    peer_a = kwargs.pop('peer_a')
    peer_b = kwargs.pop('peer_b')
    channel_a = kwargs.pop('channel_a')
    channel_b = kwargs.pop('channel_b')
    ix = kwargs.pop('ix')
    tag_a = kwargs.pop('tag_a')
    tag_b = kwargs.pop('tag_b')
    ticket = kwargs.pop('ticket')
    b_type = kwargs.pop('b_type')
    inner_b = kwargs.pop('inner_b')
    inner_a = kwargs.pop('inner_a')

    tag_a = get_or_create_specific_tag_without_bilateral(
        ix=ix,
        channel=channel_a,
        tag_number=tag_a)
    tag_b = get_or_create_specific_tag_without_bilateral(
        ix=ix,
        channel=channel_b,
        tag_number=tag_b)

    if not tag_b:
        raise(ValidationError(_("This is not a valid Tag number")))

    elif inner_b and not check_inner_tag_availability(inner=inner_b, tag=tag_b, ix=ix):
        raise(ValidationError(_("Invalid inner b tag")))
    elif inner_a and not check_inner_tag_availability(inner=inner_a, tag=tag_a, ix=ix):
        raise(ValidationError(_("Invalid inner a tag")))
    elif inner_a and inner_b and not inner_b == inner_a:
        raise(ValidationError(
            _("Inner a and b must have the same number")))

    bilateral_peer_a = BilateralPeer.objects.create(
        last_ticket=ticket,
        tag=tag_a,
        inner=inner_a,
        customer_channel=channel_a,
        asn=peer_a,
        shortname="b{}".format(peer_a.number),
        mac_addresses=list(),
        status='ALLOCATED')

    bilateral_peer_b = BilateralPeer.objects.create(
        last_ticket=ticket,
        tag=tag_b,
        inner=inner_b,
        customer_channel=channel_b,
        asn=peer_b,
        shortname="b{}".format(peer_b.number),
        mac_addresses=list(),
        status='ALLOCATED')

    bilateral = Bilateral.objects.create(
        last_ticket=ticket,
        peer_a=bilateral_peer_a,
        peer_b=bilateral_peer_b,
        bilateral_type=b_type)

    tag_a.status = 'PRODUCTION'
    tag_b.status = 'PRODUCTION'
    tag_a.save()
    tag_b.save()
    return bilateral


create_bilateral = dict([
    (0, create_bilateral_not_qinq),
    (1, create_bilateral_peer_a_qinq),
    (2, create_bilateral_peer_b_qinq),
    (3, create_bilateral_a_b_qinq)
])
