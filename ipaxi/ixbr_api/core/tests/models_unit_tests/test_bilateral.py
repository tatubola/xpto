from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import gettext as _
from model_mommy import mommy

from ...models import Bilateral, BilateralPeer, User
from ..login import DefaultLogin


class Test_Bilateral(TestCase):
    """Tests Bilateral model."""

    def setUp(self):
        DefaultLogin.__init__(self)

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    @patch('ixbr_api.core.models.create_tag_by_channel_port')
    @patch('ixbr_api.core.models.create_all_ips')
    def test_simple_history(
            self, mock_create_all_ips, mock_tag_channel_by_port,
            mock_full_clean):
        bilateral = mommy.make(Bilateral, description='old description')

        new_user = User.objects.get_or_create(name='otheruser',
                                              email='otheruser@nic.br')[0]
        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = new_user
        bilateral.description = 'new description'
        bilateral.save()
        mock.return_value = self.superuser

        self.assertEqual(bilateral.history.first().description,
                         'new description')
        self.assertEqual(bilateral.history.last().description,
                         'old description')
        self.assertEqual(bilateral.history.first().modified_by, new_user)
        self.assertEqual(bilateral.history.last().modified_by, self.superuser)

    # Tests of methods of Bilateral
    def test_bilateral_meta_verbose_name(self):
        self.assertEqual(str(Bilateral._meta.verbose_name), 'Bilateral')

    def test_bilateral_meta_verbose_name_plural(self):
        self.assertEqual(str(Bilateral._meta.verbose_name_plural),
                         'Bilaterals')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_tag_meta__str__(self, mock_full_clean, mock_signals):
        bilateral = mommy.make(Bilateral, label='bilateral label')
        self.assertEqual(
            str(bilateral),
            "[{label}: AS{asn_a}-AS{asn_b}]".format(
                label=bilateral.label,
                asn_a=bilateral.peer_a.asn.number,
                asn_b=bilateral.peer_b.asn.number))

    # Tests of model validation
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_update_label(self, mock_full_clean, mock_signals):
        bilateral = mommy.make(Bilateral, label='bilateral label')
        bilateral.label = 'new bilateral label'
        with self.assertRaisesMessage(
                ValidationError,
                'Trying to update non updatable field: '
                'Bilateral.label'):
            bilateral.clean()

    # Tests of model validation
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_update_peer_a(self, mock_full_clean, mock_signals):
        peer_a = mommy.make(BilateralPeer)
        peer_b = mommy.make(BilateralPeer)
        bilateral = mommy.make(Bilateral, peer_a=peer_a)
        bilateral.peer_a = peer_b
        with self.assertRaisesMessage(
                ValidationError,
                'Trying to update non updatable field: '
                'Bilateral.peer_a'):
            bilateral.clean()

    # Tests of model validation
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_update_peer_b(self, mock_full_clean, mock_signals):
        peer_a = mommy.make(BilateralPeer)
        peer_b = mommy.make(BilateralPeer)
        bilateral = mommy.make(Bilateral, peer_b=peer_b)
        bilateral.peer_b = peer_a
        with self.assertRaisesMessage(
                ValidationError,
                'Trying to update non updatable field: '
                'Bilateral.peer_b'):
            bilateral.clean()

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_peer_a_equals_peer_b(self, mock_full_clean, mock_signals):
        peer = mommy.make(BilateralPeer)
        bilateral = mommy.prepare(Bilateral, peer_a=peer, peer_b=peer)
        with self.assertRaisesMessage(
                ValidationError,
                _('Peer a and Peer b must be different')):
            bilateral.clean()

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_validate_label_of_vpws(self, mock_full_clean, mock_signals):
        vpws_bilateral_with_invalid_label = mommy.make(
            Bilateral, bilateral_type='VPWS', label=str(2**64))
        with self.assertRaisesMessage(
                ValidationError,
                _('VPWS Bilateral\'s label must be a 64bits number')):
            vpws_bilateral_with_invalid_label.clean()

        vpws_bilateral_with_valid_label = mommy.make(
            Bilateral, bilateral_type='VPWS', label=str(2 ** 64 - 1))
        # Clean is called to verify if object passes model validation
        vpws_bilateral_with_valid_label.clean()

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_validate_label_of_vxlan(self, mock_full_clean, mock_signals):
        vxlan_bilateral_with_invalid_label = mommy.make(
            Bilateral, bilateral_type='VXLAN', label=str(2**24))
        with self.assertRaisesMessage(
                ValidationError,
                _('VXLAN Bilateral\'s label must be a 24bits number')):
            vxlan_bilateral_with_invalid_label.clean()

        vxlan_bilateral_with_valid_label = mommy.make(
            Bilateral, bilateral_type='VXLAN', label=str(2 ** 24 - 1))
        vxlan_bilateral_with_valid_label.clean()
