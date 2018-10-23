from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import gettext as _
from model_mommy import mommy

from ...models import (IX, BilateralPeer, ChannelPort, MLPAv4,
                       MLPAv6, Monitorv4, Port, Tag, User,)
from ..login import DefaultLogin


class Test_Tag(TestCase):
    """Tests Tag model."""

    def setUp(self):
        '''
        This method creates an user and logs into the system
        '''
        DefaultLogin.__init__(self)

        p = patch(
            'ixbr_api.core.models.Switch.full_clean')
        self.addCleanup(p.stop)
        p.start()

    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_simple_history(self, mock_full_clean, mock_create_all_ips):
        tag = mommy.make(Tag, description='old description')

        new_user = User.objects.get_or_create(name='otheruser',
                                              email='otheruser@nic.br')[0]
        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = new_user
        tag.description = 'new description'
        tag.save()
        mock.return_value = self.superuser

        self.assertEqual(tag.history.first().description, 'new description')
        self.assertEqual(tag.history.last().description, 'old description')
        self.assertEqual(tag.history.first().modified_by, new_user)
        self.assertEqual(tag.history.last().modified_by, self.superuser)

    # Test of fields validation
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_validate_tag_number(self, mock_full_clean, mock_signals):
        with self.assertRaisesMessage(ValidationError,
                                      "Ensure this value is greater than or "
                                      "equal to 0."):
            ix = mommy.make(IX)
            tag = mommy.prepare(Tag, tag=-1, modified_by=self.superuser, ix=ix)
            tag.clean_fields()

            tag = mommy.prepare(Tag, tag=4096, modified_by=self.superuser,
                                ix=ix)
            tag.clean_fields()

    # Test of field uniqueness
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_field_uniqueness(self, mock_full_clean, mock_signals):
        ix = mommy.make(IX)
        tag_domain = mommy.make(ChannelPort)
        tag_number = 1
        mommy.make(Tag, ix=ix, tag_domain=tag_domain, tag=tag_number)
        tag2 = mommy.prepare(Tag, ix=ix, tag_domain=tag_domain, tag=tag_number)

        with self.assertRaisesMessage(ValidationError,
                                      "Tag with this Tag, Ix and Tag domain "
                                      "already exists."):
            tag2.validate_unique()

        tag2 = mommy.prepare(Tag, ix=ix, tag_domain=tag_domain,
                             tag=tag_number + 1)

        # Validate unique is called to verify that all uniqueness constraints
        # are satisfied
        tag2.validate_unique()
        tag2.save()

    # Tests of methods of Tag
    def test_Tag_meta_verbose_name(self):
        self.assertEqual(str(Tag._meta.verbose_name), 'Tag')

    def test_Tag_meta_verbose_name_plural(self):
        self.assertEqual(str(Tag._meta.verbose_name_plural), 'Tags')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_tag_meta__str__(self, mock_full_clean, mock_signals):
        ix = mommy.make(IX)
        tag_domain = mommy.make(ChannelPort)
        tag = mommy.make(Tag, tag=10, ix=ix, tag_domain=tag_domain)
        self.assertEqual(
            str(tag),
            "[{ix}-{tag}:{tag_domain}]".format(ix=str(ix),
                                               tag=tag.tag,
                                               tag_domain=str(tag_domain)))

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ordering(self, mock_full_clean, mock_signals):
        ix2 = mommy.make(IX, code='cc')
        ix0 = mommy.make(IX, code='aa')
        ix1 = mommy.make(IX, code='bb')

        tag4 = mommy.make(Tag, ix=ix2, tag=0)
        tag1 = mommy.make(Tag, ix=ix0, tag=1)
        tag3 = mommy.make(Tag, ix=ix1, tag=3)
        tag2 = mommy.make(Tag, ix=ix1, tag=0)
        tag0 = mommy.make(Tag, ix=ix0, tag=0)

        tags = Tag.objects.all()
        self.assertEqual(tags[0], tag0)
        self.assertEqual(tags[1], tag1)
        self.assertEqual(tags[2], tag2)
        self.assertEqual(tags[3], tag3)
        self.assertEqual(tags[4], tag4)

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_update_status(self, mock_full_clean, mock_signals):
        tag = mommy.make(Tag, status='AVAILABLE')
        with self.assertRaisesMessage(ValueError,
                                      _("Can't update to the same status")):
            tag.update_status('AVAILABLE')
        tag.update_status('PRODUCTION')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_block_update_tag_number(self, mock_full_clean, mock_signals):
        tag = mommy.make(Tag, tag=1)
        tag.tag = 2

        with self.assertRaisesMessage(ValidationError,
                                      "Trying to update non updatable field: "
                                      "Tag.tag"):
            tag.block_update_fields('tag')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_block_update_ix(self, mock_full_clean, mock_signals):
        ix0 = mommy.make(IX, code='sp')
        ix1 = mommy.make(IX, code='rj')

        tag = mommy.make(Tag, ix=ix0)
        tag.ix = ix1

        with self.assertRaisesMessage(ValidationError,
                                      "Trying to update non updatable field: "
                                      "Tag.ix"):
            tag.block_update_fields('ix_id')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_validate_ix_tag_domain(self, mock_full_clean, mock_signals):
        ix = mommy.make(IX, code='sp')
        other_ix = mommy.make(IX, code='rj')

        tag_domain = mommy.make(ChannelPort)
        mommy.make(Port, switch__pix__ix=ix, channel_port=tag_domain,
                   _quantity=10)
        port_in_wrong_ix = mommy.make(Port, switch__pix__ix=other_ix,
                                      channel_port=tag_domain)

        tag = mommy.prepare(Tag, ix=ix, tag_domain=tag_domain)
        with self.assertRaisesMessage(ValidationError,
                                      _("tag_domain.ix and ix must be the "
                                        "same")):
            tag.validate_ix_tag_domain()

        port_in_wrong_ix.delete()
        tag.validate_ix_tag_domain()

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_validate_tag_status(self, mock_full_clean, mock_signals):
        other_tag = mommy.make(Tag)
        tag = mommy.make(Tag)
        mlpav4 = mommy.make(MLPAv4, tag=tag)
        mommy.make(MLPAv6, tag=other_tag)
        mommy.make(Monitorv4, tag=other_tag)
        mommy.make(BilateralPeer, tag=other_tag)

        tag.status = 'AVAILABLE'
        with self.assertRaisesMessage(ValidationError,
                                      _("An used Tag can not be "
                                        "AVAILABLE")):
            tag.validate_tag_status()

        mlpav4.tag = other_tag
        mlpav4.save()
        tag.validate_tag_status()
