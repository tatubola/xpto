# -*- coding: utf-8 -*-
from itertools import cycle
from unittest.mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy
from model_mommy.recipe import seq

from ...forms import GenericMLPANewChannelForm
from ...models import (IX, PIX, ASN, ContactsMap, SwitchModel, Switch,
                       ChannelPort, Port, CustomerChannel, IPv4Address,
                       IPv6Address, Tag)
from ..login import DefaultLogin


class GenericMLPANewFormTestCase(TestCase):
    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
        p.start()
        self.addCleanup(p.stop)

        p = patch('ixbr_api.core.models.create_all_ips')
        p.start()
        self.addCleanup(p.stop)

        p = patch(
            'ixbr_api.core.models.Switch.full_clean')
        self.addCleanup(p.stop)
        p.start()

        ixs = ['sp', 'jpa']
        management_prefix = ['192.168.21.0/26', '192.168.22.0/26']
        ipv4_prefixs = ['187.16.193.0/24', '187.16.199.0/24']
        ipv6_prefixs = ['2001:12f8:0:16::/64', '2001:12f8:0:22::/64']
        self.ixs = mommy.make(
            IX,
            code=cycle(ixs),
            management_prefix=cycle(management_prefix),
            ipv4_prefix=cycle(ipv4_prefixs),
            ipv6_prefix=cycle(ipv6_prefixs),
            _quantity=len(ixs))

        self.pixs = mommy.make(
            PIX,
            ix=cycle(self.ixs),
            _quantity=len(ixs))

        self.asn = mommy.make(
            ASN,
            number=20121)

        self.contacstmap = mommy.make(
            ContactsMap,
            asn=self.asn,
            ix=self.ixs[0])

        models = ['[X460-48t]', '[X670-72x]']

        self.switch_models = mommy.make(
            SwitchModel,
            model=cycle(models),
            vendor='EXTREME',
            _quantity=len(models))

        management_ips = ['192.168.21.1', '192.168.22.1']
        self.switchs = mommy.make(
            Switch,
            pix=cycle(self.pixs),
            model=cycle(self.switch_models),
            management_ip=cycle(management_ips),
            _quantity=len(models))

        self.channel_port = mommy.make(
            ChannelPort,
            create_tags=False)

        self.ports = mommy.make(
            Port,
            switch=cycle(self.switchs),
            name=seq('1'),
            channel_port=self.channel_port,
            _quantity=len(self.switchs))

        self.customer_channel = mommy.make(
            CustomerChannel,
            asn=self.asn,
            name='ct-1',
            channel_port=self.channel_port)

        ipv4s = ['187.16.193.22', '187.16.199.9']
        self.ipv4_not_found = '187.16.192.22'

        self.ipv4s = mommy.make(
            IPv4Address,
            address=cycle(ipv4s),
            ix=cycle(self.ixs),
            _quantity=len(ipv4s))

        ipv6s = ['2001:12f8:0:16::22', '2001:12f8:0:22::9']
        self.ipv6_not_found = '2001:12f8:0:17::22'
        self.ipv6s = mommy.make(
            IPv6Address,
            address=cycle(ipv6s),
            ix=cycle(self.ixs),
            _quantity=len(ipv6s))

        tags = [2, 3]
        self.tags = mommy.make(
            Tag,
            tag=cycle(tags),
            status='AVAILABLE',
            _quantity=len(tags))

    def message_ip_not_found(type_service):
        message = ("{} not found").format(type_service)

        return message

    def message_ips_another_ix(ix):
        message = ("IPs don't belong to IX {} network").format(ix)

        return message

    def message_ip_another_ix(ip_object, type_service, ip_prefix, ix):
        message = ("{} doesn't belong to {} network: {}").format(
            ip_object.address, type_service, ip_prefix)

        return message

    def test_when_status_code_200_and_context(self):
        request = self.client.get(
            reverse('core:generic_new_mlpa_add_form',
                    args=[self.asn.number, self.ixs[0].code]))

        self.assertEqual(200, request.status_code)
        self.assertTemplateUsed('forms/generic_mlpa_new_channel.html')

        self.assertEqual(request.context['asn'], str(self.asn.number))
        self.assertEqual(request.context['code'], self.ixs[0].code)

    def test_add_ipv4_and_ipv6_success(self):
        request = self.client.post(
            reverse('core:generic_new_mlpa_add_form',
                    args=[self.asn.number,
                          self.ixs[0].code]),
            {'last_ticket': 1234,
             'pix': self.pixs[0].uuid,
             'switch': self.switchs[0].uuid,
             'customer_channel': self.customer_channel.uuid,
             'service_option': 'v4_and_v6',
             'mlpav4_address': self.ipv4s[0].address,
             'tag_v4': self.tags[0].tag,
             'inner_v4': 1,
             'mlpav6_address': self.ipv6s[0].address,
             'tag_v6': self.tags[1].tag,
             'inner_v6': 2,
             'asn': self.asn.number,
             'code': self.ixs[0].code})

        self.assertTemplateUsed('forms/modal_feedback_service.html')

        message = request.context['message']
        self.assertEqual(message, 'success')

    def test_add_only_ipv4_success(self):
        request = self.client.post(
            reverse('core:generic_new_mlpa_add_form',
                    args=[self.asn.number,
                          self.ixs[0].code]),
            {'last_ticket': 1234,
             'pix': self.pixs[0].uuid,
             'switch': self.switchs[0].uuid,
             'customer_channel': self.customer_channel.uuid,
             'service_option': 'only_v4',
             'mlpav4_address': self.ipv4s[0].address,
             'tag_v4': self.tags[0].tag,
             'inner_v4': 1,
             'asn': self.asn.number,
             'code': self.ixs[0].code})

        self.assertTemplateUsed('forms/modal_feedback_service.html')

        message = request.context['message']
        self.assertEqual(message, 'success')

    def test_add_only_ipv6_success(self):
        request = self.client.post(
            reverse('core:generic_new_mlpa_add_form',
                    args=[self.asn.number,
                          self.ixs[0].code]),
            {'last_ticket': 1234,
             'pix': self.pixs[0].uuid,
             'switch': self.switchs[0].uuid,
             'customer_channel': self.customer_channel.uuid,
             'service_option': 'only_v6',
             'mlpav6_address': self.ipv6s[0].address,
             'tag_v6': self.tags[0].tag,
             'inner_v6': 1,
             'asn': self.asn.number,
             'code': self.ixs[0].code})

        self.assertTemplateUsed('forms/modal_feedback_service.html')

        message = request.context['message']
        self.assertEqual(message, 'success')

    def test_add_ipv4_from_another_ix(self):
        request = self.client.post(
            reverse('core:generic_new_mlpa_add_form',
                    args=[self.asn.number,
                          self.ixs[0].code]),
            {'last_ticket': 1234,
             'pix': self.pixs[0].uuid,
             'switch': self.switchs[0].uuid,
             'customer_channel': self.customer_channel.uuid,
             'service_option': 'only_v4',
             'mlpav4_address': self.ipv4s[1].address,
             'tag_v4': self.tags[0].tag,
             'inner_v4': 1,
             'asn': self.asn.number,
             'code': self.ixs[0].code})

        self.assertTemplateUsed('forms/modal_feedback_service.html')

        message = request.context['message']
        self.assertEqual(
            message,
            GenericMLPANewFormTestCase.message_ip_another_ix(
                self.ipv4s[1], 'IPv4', self.ixs[0].ipv4_prefix,
                self.ixs[0].code))

    def test_add_ipv6_from_another_ix(self):
        request = self.client.post(
            reverse('core:generic_new_mlpa_add_form',
                    args=[self.asn.number,
                          self.ixs[0].code]),
            {'last_ticket': 1234,
             'pix': self.pixs[0].uuid,
             'switch': self.switchs[0].uuid,
             'customer_channel': self.customer_channel.uuid,
             'service_option': 'only_v6',
             'mlpav6_address': self.ipv6s[1].address,
             'tag_v6': self.tags[0].tag,
             'inner_v6': 1,
             'asn': self.asn.number,
             'code': self.ixs[0].code})

        self.assertTemplateUsed('forms/modal_feedback_service.html')

        message = request.context['message']
        self.assertEqual(
            message,
            GenericMLPANewFormTestCase.message_ip_another_ix(
                self.ipv6s[1], 'IPv6', self.ixs[0].ipv6_prefix,
                self.ixs[0].code))

    def test_add_ipv4_and_ipv6_from_another_ix(self):
        request = self.client.post(
            reverse('core:generic_new_mlpa_add_form',
                    args=[self.asn.number,
                          self.ixs[0].code]),
            {'last_ticket': 1234,
             'pix': self.pixs[0].uuid,
             'switch': self.switchs[0].uuid,
             'customer_channel': self.customer_channel.uuid,
             'service_option': 'v4_and_v6',
             'mlpav4_address': self.ipv4s[1].address,
             'tag_v4': self.tags[0].tag,
             'inner_v4': 1,
             'mlpav6_address': self.ipv6s[1].address,
             'tag_v6': self.tags[1].tag,
             'inner_v6': 2,
             'asn': self.asn.number,
             'code': self.ixs[0].code})

        self.assertTemplateUsed('forms/modal_feedback_service.html')

        message = request.context['message']
        self.assertEqual(
            message, GenericMLPANewFormTestCase.message_ips_another_ix(
                self.ixs[0].code))

    def test_ipv4_not_found(self):
        request = self.client.post(
            reverse('core:generic_new_mlpa_add_form',
                    args=[self.asn.number,
                          self.ixs[0].code]),
            {'last_ticket': 1234,
             'pix': self.pixs[0].uuid,
             'switch': self.switchs[0].uuid,
             'customer_channel': self.customer_channel.uuid,
             'service_option': 'only_v4',
             'mlpav4_address': self.ipv4_not_found,
             'tag_v4': self.tags[0].tag,
             'inner_v4': 1,
             'asn': self.asn.number,
             'code': self.ixs[0].code})

        self.assertTemplateUsed('forms/modal_feedback_service.html')

        message = request.context['message']
        self.assertEqual(
            message, GenericMLPANewFormTestCase.message_ip_not_found(
                'IPv4'))

    def test_ipv6_not_found(self):
        request = self.client.post(
            reverse('core:generic_new_mlpa_add_form',
                    args=[self.asn.number,
                          self.ixs[0].code]),
            {'last_ticket': 1234,
             'pix': self.pixs[0].uuid,
             'switch': self.switchs[0].uuid,
             'customer_channel': self.customer_channel.uuid,
             'service_option': 'only_v6',
             'mlpav6_address': self.ipv6_not_found,
             'tag_v6': self.tags[0].tag,
             'inner_v6': 1,
             'asn': self.asn.number,
             'code': self.ixs[0].code})

        self.assertTemplateUsed('forms/modal_feedback_service.html')

        message = request.context['message']
        self.assertEqual(
            message, GenericMLPANewFormTestCase.message_ip_not_found(
                'IPv6'))

    def test_ipv4_and_ipv6_not_found(self):
        request = self.client.post(
            reverse('core:generic_new_mlpa_add_form',
                    args=[self.asn.number,
                          self.ixs[0].code]),
            {'last_ticket': 1234,
             'pix': self.pixs[0].uuid,
             'switch': self.switchs[0].uuid,
             'customer_channel': self.customer_channel.uuid,
             'service_option': 'v4_and_v6',
             'mlpav4_address': self.ipv4_not_found,
             'tag_v4': self.tags[0].tag,
             'inner_v4': 1,
             'mlpav6_address': self.ipv6_not_found,
             'tag_v6': self.tags[1].tag,
             'inner_v6': 2,
             'asn': self.asn.number,
             'code': self.ixs[0].code})

        self.assertTemplateUsed('forms/modal_feedback_service.html')

        message = request.context['message']
        self.assertEqual(
            message, GenericMLPANewFormTestCase.message_ip_not_found(
                'IPs'))

    def test_generic_mlpa_new_channel_form_fail(self):
        form = GenericMLPANewChannelForm(
            data={
                'last_ticket': 1234,
                'pix': self.pixs[0].uuid,
                'switch': self.switchs[0].uuid,
                'customer_channel': '',
                'service_option': 'only_v4',
                'mlpav4_address': self.ipv4_not_found,
                'tag_v4': self.tags[0].tag,
                'inner_v4': 1,
                'asn': self.asn.number,
                'code': self.ixs[0].code
            }
        )
        self.assertFalse(form.is_valid())
