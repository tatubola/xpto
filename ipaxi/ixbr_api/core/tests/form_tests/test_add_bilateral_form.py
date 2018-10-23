# # -*- coding: utf-8 -*-
# from itertools import cycle
# from unittest.mock import patch

# from django.contrib.messages import get_messages
# from django.core.urlresolvers import reverse
# from django.test import TestCase
# from model_mommy import mommy

# from ...models import (ASN, Bilateral, BilateralPeer, CustomerChannel, IX,
#                        MLPAv4, PIX, Port, Switch)
# from ..login import DefaultLogin
# from ...forms import BilateralAddForm


# class BilateralFormTestCase(TestCase):

#     def setUp(self):
#         DefaultLogin.__init__(self)

#         p = patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
#         p.start()
#         self.addCleanup(p.stop)

#         p = patch('ixbr_api.core.models.create_all_ips')
#         p.start()
#         self.addCleanup(p.stop)

#         p = patch('ixbr_api.core.models.create_tag_by_channel_port')
#         p.start()
#         self.addCleanup(p.stop)

#         self.ix = mommy.make(IX, tags_policy='ix_managed')
#         self.pix = mommy.make(PIX, ix=self.ix)
#         self.switch = mommy.make(Switch, pix=self.pix)

#         asnnumber = [2311, 44526, 62000, 62111]
#         self.asns = mommy.make(
#             ASN,
#             number=cycle(asnnumber),
#             _quantity=len(asnnumber))

#         self.customer_channels = mommy.make(
#             CustomerChannel,
#             asn=cycle(self.asns),
#             _quantity=len(asnnumber))

#         self.ports = mommy.make(
#             Port,
#             channel_port=cycle(
#                 ch.channel_port for ch in self.customer_channels),
#             switch=self.switch,
#             _quantity=len(asnnumber))

#         self.services = mommy.make(
#             MLPAv4, customer_channel=cycle(self.customer_channels))

#         self.inner = 1223
#         self.last_ticket = 12545

#     def test_form_add_bilateral_return_200_status_code_on_get(self):
#         request = self.client.get(
#             reverse('core:add_bilateral_form',
#                     args=[self.asns[0].number,
#                           self.customer_channels[0].uuid]))
#         self.assertEqual(request.status_code, 200)
#         self.assertTemplateUsed('add_bilateral_form.html')

#     def test_form_add_bilateral_type_L2_success_on_post(self):
#         response = self.client.post(
#             reverse('core:add_bilateral_form',
#                     args=[self.asns[0].number,
#                           self.customer_channels[0].uuid]),
#             {'last_ticket': self.last_ticket,
#              'asn': self.asns[1].number,
#              'bilateral_type': 'L2',
#              'pix': self.pix.uuid,
#              'switch': self.switch.uuid,
#              'customer_channel': self.customer_channels[1].uuid,
#              'tag': self.ix.tag_set.last().tag})
#         self.assertEqual(response.status_code, 302)
#         messages = [
#             m.message for m in get_messages(response.wsgi_request)]
#         self.assertIn('Bilateral created', messages)
#         self.assertEqual(Bilateral.objects.count(), 1)
#         self.assertEqual(BilateralPeer.objects.count(), 2)
#         self.assertEqual(
#             BilateralPeer.objects.first().shortname,
#             "BilateralPeer {}-{}".format(
#                 self.asns[0].number, self.asns[1].number))

#     def test_form_not_renders_with_incorrect_inputs(self):
#         form = BilateralAddForm(
#             data={
#                 'last_ticket': self.last_ticket,
#                 'asn': self.asns[1].number,
#                 'bilateral_type': 'L2',
#                 'pix': self.pix.uuid,
#                 'switch': self.switch.uuid,
#                 'customer_channel': 'not a customer channel',
#                 'tag': self.ix.tag_set.last().tag,
#             }
#         )
#         self.assertFalse(form.is_valid())

#     def test_form_add_bilateral_type_L2_with_inner_filled_ignored_success_on_post(self):
#         response = self.client.post(
#             reverse('core:add_bilateral_form',
#                     args=[self.asns[0].number,
#                           self.customer_channels[0].uuid]),
#             {'last_ticket': self.last_ticket,
#              'asn': self.asns[1].number,
#              'bilateral_type': 'L2',
#              'pix': self.pix.uuid,
#              'switch': self.switch.uuid,
#              'customer_channel': self.customer_channels[1].uuid,
#              'tag': self.ix.tag_set.last().tag,
#              'inner': self.inner})
#         self.assertEqual(response.status_code, 302)
#         messages = [
#             m.message for m in get_messages(response.wsgi_request)]
#         self.assertIn('Bilateral created', messages)
#         self.assertEqual(Bilateral.objects.count(), 1)
#         self.assertEqual(BilateralPeer.objects.count(), 2)
#         self.assertEqual(
#             BilateralPeer.objects.first().shortname,
#             "BilateralPeer {}-{}".format(
#                 self.asns[0].number, self.asns[1].number))
#         self.assertEqual(BilateralPeer.objects.first().inner, None)
#         self.assertEqual(BilateralPeer.objects.last().inner, None)

#     def test_form_add_bilateral_type_VXLAN_success_on_post(self):
#         response = self.client.post(
#             reverse('core:add_bilateral_form',
#                     args=[self.asns[0].number,
#                           self.customer_channels[0].uuid]),
#             {'last_ticket': self.last_ticket,
#              'asn': self.asns[1].number,
#              'bilateral_type': 'VXLAN',
#              'pix': self.pix.uuid,
#              'switch': self.switch.uuid,
#              'customer_channel': self.customer_channels[1].uuid,
#              'tag': self.ix.tag_set.last().tag,
#              'inner': self.inner})
#         self.assertEqual(response.status_code, 302)
#         messages = [
#             m.message for m in get_messages(response.wsgi_request)]
#         self.assertIn('Bilateral created', messages)
#         self.assertEqual(Bilateral.objects.count(), 1)
#         self.assertEqual(BilateralPeer.objects.count(), 2)
#         self.assertEqual(
#             BilateralPeer.objects.first().shortname,
#             "BilateralPeer {}-{}".format(
#                 self.asns[0].number, self.asns[1].number))
#         self.assertEqual(BilateralPeer.objects.first().inner, self.inner)
#         self.assertEqual(BilateralPeer.objects.last().inner, self.inner)

#     def test_form_add_two_bilateral_type_VXLAN_same_inner_success_on_post(self):
#         response = self.client.post(
#             reverse('core:add_bilateral_form',
#                     args=[self.asns[0].number,
#                           self.customer_channels[0].uuid]),
#             {'last_ticket': self.last_ticket,
#              'asn': self.asns[1].number,
#              'bilateral_type': 'VXLAN',
#              'pix': self.pix.uuid,
#              'switch': self.switch.uuid,
#              'customer_channel': self.customer_channels[1].uuid,
#              'tag': self.ix.tag_set.last().tag,
#              'inner': self.inner})

#         self.assertEqual(response.status_code, 302)

#         messages = [
#             m.message for m in get_messages(response.wsgi_request)]
#         self.assertIn('Bilateral created', messages)

#         self.assertEqual(Bilateral.objects.count(), 1)
#         self.assertEqual(BilateralPeer.objects.count(), 2)
#         self.assertEqual(
#             BilateralPeer.objects.first().shortname,
#             "BilateralPeer {}-{}".format(
#                 self.asns[0].number, self.asns[1].number))
#         self.assertEqual(BilateralPeer.objects.first().inner, self.inner)
#         self.assertEqual(BilateralPeer.objects.last().inner, self.inner)

#         response_second = self.client.post(
#             reverse('core:add_bilateral_form',
#                     args=[self.asns[2].number,
#                           self.customer_channels[0].uuid]),
#             {'last_ticket': self.last_ticket,
#              'asn': self.asns[3].number,
#              'bilateral_type': 'VXLAN',
#              'pix': self.pix.uuid,
#              'switch': self.switch.uuid,
#              'customer_channel': self.customer_channels[1].uuid,
#              'tag': self.ix.tag_set.filter(status='AVAILABLE').last().tag,
#              'inner': self.inner})

#         self.assertEqual(response_second.status_code, 302)

#         messages = [
#             m.message for m in get_messages(response.wsgi_request)]
#         self.assertIn('Bilateral created', messages)
#         self.assertEqual(Bilateral.objects.count(), 2)
#         self.assertEqual(BilateralPeer.objects.count(), 4)
#         self.assertEqual(
#             BilateralPeer.objects.last().shortname,
#             "BilateralPeer {}-{}".format(
#                 self.asns[2].number, self.asns[3].number))
#         self.assertEqual(BilateralPeer.objects.filter(inner=self.inner).count(), 4)