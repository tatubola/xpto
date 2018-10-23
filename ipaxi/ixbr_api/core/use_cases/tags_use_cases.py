from django.db.models import Q
from django.utils.translation import gettext as _

from ..models import (IX, BilateralPeer, MLPAv4, MLPAv6, Monitorv4, Tag,
                      create_tag_by_channel_port)
from ..utils.constants import MAX_TAG_NUMBER, MIN_TAG_NUMBER
from .network_use_cases import get_pe_channel_by_channel


def get_free_tags(**kwargs):
    """ gets the free TAGs to be used in a given channel

    Args:
        ix: kwarg -> the owner IX
        channel: kwargs -> Origin Channel

    Returns:
        Queryset<Tag>: Queryset conataining free Tags

    This funciton is dependent of the following functions:
        get_pe_channel_by_channel
    """
    ix = kwargs.pop('ix')
    channel = kwargs.pop('channel')

    if type(ix) is str:
        try:
            ix = IX.objects.get(pk=ix)
        except Exception:
            raise ValueError(_("IX doesn't exist"))

    if ix.tags_policy == 'ix_managed':
        free_tags = Tag.objects.filter(
            ix=ix,
            status='AVAILABLE').order_by('tag')

    else:
        pe_channel = get_pe_channel_by_channel(channel=channel, ix=ix)
        tag_domain = pe_channel.channel_port if pe_channel else None
        free_tags = Tag.objects.filter(
            ix=ix,
            tag_domain=tag_domain,
            status='AVAILABLE').order_by('tag')

        if channel.channel_port.tags_type == 'Direct-Bundle-Ether':
            if len(free_tags) <= 1 and pe_channel:
                if(Tag.objects.filter(tag_domain=tag_domain).count() <=
                        MAX_TAG_NUMBER - MIN_TAG_NUMBER):
                    create_tag_by_channel_port(tag_domain, False, 2)
                    free_tags = get_free_tags(ix=ix, channel=channel)

    return free_tags


def instantiate_tag(**kwargs):
    """ create a tag instance

    Args:
        ix: kwarg -> the owner IX
        channel: kwargs -> Origin Channel
        tag_number: kwargs:Integer -> the tag.tag to be created

    Returns:
        Tag: tag instance

    This funciton is dependent of the following functions:
        get_pe_by_channel
    """

    channel = kwargs.pop('channel')
    tag_number = kwargs.pop('tag_number')
    ix = kwargs.pop('ix')
    if type(ix) == str:
        ix = IX.objects.get(pk=ix)

    if not ix.tags_policy == 'ix_managed':
        pe_channel = get_pe_channel_by_channel(channel=channel, ix=ix)
        tag_domain = pe_channel.channel_port if pe_channel else None
        tag = Tag.objects.filter(
            ix=ix,
            tag_domain=tag_domain).order_by('tag').filter(tag=tag_number)
        if not tag:
            if tag_number == 0 or tag_number == 1:
                status = 'ALLOCATED'
            else:
                status = 'AVAILABLE'
            tag = Tag.objects.create(
                tag=tag_number, last_ticket=channel.last_ticket,
                modified_by=channel.modified_by, ix=ix,
                tag_domain=tag_domain, status=status)
            tag.save()
            return tag
        else:
            return None


def get_tag_without_bilateral(**kwargs):
    """ gets all the free TAGs in a given Channel, that their tag attribute
    don't be the same to other TAG used by a Bilateral in the given IX.

    Args:
        ix: kwarg -> the owner IX
        channel: kwargs -> Origin Channel

    Returns:
        Queryset<Tag>: Queryset conataining free Tags

    This funciton is dependent of the following functions:
        get_free_tags
    """
    ix = kwargs.pop('ix')
    channel = kwargs.pop('channel')

    channel_available_tags = get_free_tags(ix=ix, channel=channel)
    bilateral_used_tags = Tag.objects.filter(
        Q(bilateralpeer__in=list(BilateralPeer.objects.all()))
        | Q(reserved=True),
        ix=ix,
    )

    free_tags = channel_available_tags.exclude(
        tag__in=bilateral_used_tags.values_list('tag', flat=True))

    return free_tags


def get_tag_without_all_service(**kwargs):
    """ gets all the free TAGs in a given Channel, that their tag attribute
    don't be the same to other TAG in the given IX. If there's no an instance
    of free TAG, then, this instantiate it

    Args:
        ix: kwarg -> the owner IX
        channel: kwargs -> Origin Channel

    Returns:
        Queryset<Tag>: Queryset conataining free Tags

    This funciton is dependent of the following functions:
        get_free_tags, instantiate_tag
    """
    ix = kwargs.pop('ix')
    channel = kwargs.pop('channel')
    all_tags = set(range(1, 4097))

    channel_available_tags = get_free_tags(ix=ix, channel=channel)
    all_ix_used_tags = Tag.objects.filter(
        Q(status='PRODUCTION') | Q(reserved=True),
        ix=ix
    )

    free_tags = channel_available_tags.exclude(
        tag__in=all_ix_used_tags.values_list('tag', flat=True))

    if(not free_tags and len(all_ix_used_tags) <=
            MAX_TAG_NUMBER - MIN_TAG_NUMBER):
        tags_to_create = all_tags - \
            set(all_ix_used_tags.values_list('tag', flat=True))
        tag = list(tags_to_create)[0]
        free_tags = instantiate_tag(channel=channel, ix=ix, tag_number=tag)
        free_tags = Tag.objects.filter(pk=free_tags.pk)

    return free_tags


def get_or_create_specific_tag_without_all_service(**kwargs):
    """ Test the tag for validity, create if not exist and
        return it

    Args:
        ix: kwarg -> the owner IX
        channel: kwargs -> Origin Channel
        tag_number

    Returns:
        Tag: Tag object

    This funciton is dependent of the following functions:
        get_free_tags, instantiate_tag, get_tag_without_all_services
    """
    ix = kwargs.pop('ix')
    channel = kwargs.pop('channel')
    tag_number = kwargs.pop('tag_number')

    if ix.tags_policy == 'ix_managed':
        used_tags = Tag.objects.filter(
            ix=ix).exclude(status='AVAILABLE').order_by('tag')

    else:
        pe_channel = get_pe_channel_by_channel(channel=channel, ix=ix)
        tag_domain = pe_channel.channel_port if pe_channel else None
        used_tags = Tag.objects.filter(
            ix=ix,
            tag_domain=tag_domain).exclude(
            status='AVAILABLE').order_by('tag')

    if used_tags.filter(tag=tag_number):
        return 0
    else:
        free_tags = get_tag_without_all_service(
            ix=ix, channel=channel)
        if free_tags.filter(tag=tag_number):
            return free_tags.get(tag=tag_number)
        else:
            tag = instantiate_tag(
                channel=channel, ix=ix, tag_number=tag_number)
            return tag


def get_or_create_specific_tag_without_bilateral(**kwargs):
    """ Test the tag for validity, create if not exist and 
        return it

    Args:
        ix: kwarg -> the owner IX
        channel: kwargs -> Origin Channel
        tag_number

    Returns:
        Tag: Tag object

    This funciton is dependent of the following functions:
        get_free_tags, instantiate_tag, get_tag_without_all_services
    """
    ix = kwargs.pop('ix')
    channel = kwargs.pop('channel')
    tag_number = kwargs.pop('tag_number')

    if ix.tags_policy == 'ix_managed':
        used_tags = Tag.objects.filter(
            ix=ix).exclude(status='AVAILABLE').order_by('tag')

    else:
        pe_channel = get_pe_channel_by_channel(channel=channel, ix=ix)
        tag_domain = pe_channel.channel_port if pe_channel else None
        used_tags = Tag.objects.filter(
            ix=ix,
            tag_domain=tag_domain).exclude(
            status='AVAILABLE').order_by('tag')

    if used_tags.filter(tag=tag_number):
        return 0
    else:
        free_tags = get_tag_without_bilateral(
            ix=ix, channel=channel)
        if free_tags.filter(tag=tag_number):
            return free_tags.get(tag=tag_number)
        else:
            tag = instantiate_tag(
                channel=channel, ix=ix, tag_number=tag_number)
            return tag


def check_inner_tag_availability(**kwargs):
    """ Check if a given inner tag is available in a
        given outer tag

    Args:
        inner: int
        tag: Tag object

    Returns:
        Bool: True if inner available
              False if inner unavailable
    """

    inner = kwargs.pop('inner')
    tag = kwargs.pop('tag')
    used_inners = [item.inner for item in [
        *MLPAv4.objects.filter(tag=tag),
        *MLPAv6.objects.filter(tag=tag),
        *BilateralPeer.objects.filter(tag=tag),
        *Monitorv4.objects.filter(tag=tag)]]
    check_inner = inner in used_inners
    if check_inner:
        return False
    else:
        return True


def get_available_inner_tag(**kwargs):
    """ Get an available inner tag in a
        given outer tag

    Args:
        tag: Tag object

    Returns:
        Int: the inner tag number
    """

    tag = kwargs.pop('tag')
    used_inners = [item.inner for item in [
        *MLPAv4.objects.filter(tag=tag),
        *MLPAv6.objects.filter(tag=tag),
        *BilateralPeer.objects.filter(tag=tag),
        *Monitorv4.objects.filter(tag=tag)]]
    for i in range(1, 4097):
        if i not in used_inners:
            return i
