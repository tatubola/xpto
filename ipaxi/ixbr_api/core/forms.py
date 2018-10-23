from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext as _

from .models import (ASN, IX, PIX, Bilateral, Contact, CustomerChannel,
                     IPv4Address, IPv6Address, Organization,
                     PhysicalInterface, Port, Switch, SwitchModel,
                     SwitchPortRange, Tag,)
from .utils import port_utils
from .utils.constants import (MAX_TAG_NUMBER, MIN_TAG_NUMBER,
                              SWITCH_MODEL_CHANNEL_PREFIX, PORT_TYPES,
                              VENDORS, CAPACITIES_MAX, CONNECTOR_TYPES)
from .validators import validate_mac_address


def _raw_value(form, fieldname):
    field = form.fields[fieldname]
    prefix = form.add_prefix(fieldname)
    return field.widget.value_from_datadict(form.data, form.files, prefix)


class ASNForm(forms.ModelForm):

    class Meta:
        model = ASN
        fields = ('number',)


class AddMACServiceForm(forms.Form):
    required_css_class = 'required'
    last_ticket = forms.IntegerField(
        label='Ticket',
        widget=forms.TextInput(
            attrs={'type': 'number', 'min': 1, 'max': 2147483647,
                   'class': 'form-control'}
        )
    )
    address = forms.CharField(validators=[validate_mac_address],
                              widget=forms.TextInput(attrs={'class':
                                                            'form-control'}))
    copy_mac = forms.BooleanField(required=False)
    copy_mac.initial = True

    description = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control'}),
        required=False)


class EditMLPAv4Form(forms.Form):
    required_css_class = 'required'
    mlpav4_address = forms.ModelChoiceField(
        queryset=IPv4Address.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}))


class EditMLPAv6Form(forms.Form):
    required_css_class = 'required'
    mlpav6_address = forms.ModelChoiceField(
        queryset=IPv6Address.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}))


class PhoneForm(forms.Form):
    required_css_class = 'required'
    categories = (('Landline', 'Landline'),
                  ('Mobile', 'Mobile'),
                  ('Business', 'Business'),)
    last_ticket = forms.CharField(
        label='Ticket',
        max_length=20,
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'type': 'number', 'min': 1, 'max': 2147483647}
        )
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '1111-1111'}))
    category = forms.ChoiceField(
        required=False,
        widget=forms.Select(
            attrs={'class': 'form-control'}), choices=categories)


class AddCustomerChannelForm(forms.Form):

    def __init__(self, *args, **kwargs):
        switch_list = kwargs.pop('switchs', None)
        super(AddCustomerChannelForm, self).__init__(*args, **kwargs)
        port_list = {}
        if switch_list:
            self.fields['switch'] = forms.ChoiceField(
                choices=switch_list,
                widget=forms.Select(attrs={'class': 'form-control'})
            )

            if len(switch_list) > 0:
                self.fields['switch'].initial = switch_list[0]

            switch_id = self.fields['switch'].initial[0] \
                or self.initial.get('switch')[0] \
                or _raw_value(self, 'switch')[0]
            if switch_id:
                port_set = Port.objects.filter(switch=switch_id,
                                               status='AVAILABLE')
                for port in port_set:
                    port_list[str(port.name)] = str(port.uuid)
                ordered_ports = port_utils.port_sorting(port_list)
                port_choices = ()
                for key in ordered_ports:
                    port_choices += (
                        (ordered_ports[key], key),
                    )
                self.fields['ports'] = forms.ChoiceField(
                    choices=port_choices,
                    widget=forms.SelectMultiple(
                        attrs={'class': 'form-control'})
                )

                channel_name_prefix = SWITCH_MODEL_CHANNEL_PREFIX[
                    Switch.objects.get(
                        pk=switch_id).model.vendor]
                self.fields['channel_name'] = forms.CharField(
                    max_length=200,
                    initial=channel_name_prefix,
                    widget=forms.TextInput(attrs={'class': 'form-control'}),)

    required_css_class = 'required'
    pix_uuid = forms.CharField(widget=forms.HiddenInput(), required=False)
    asn = forms.CharField(widget=forms.HiddenInput(), required=False)

    ticket = forms.IntegerField(
        label='Ticket',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number', 'min': 1,
                   'max': 2147483647}
        )
    )
    pix = forms.ModelChoiceField(
        queryset=PIX.objects.all(),
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    switch = forms.ModelChoiceField(
        queryset=Switch.objects.all(),
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    channel_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    cix_type = forms.ChoiceField(
        choices=CustomerChannel.CIX_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    # TODO: need more informations on model of Translation Channel to continue
    # translation_channel = forms.ChoiceField(choices='')
    ports = forms.ModelMultipleChoiceField(
        queryset=Port.objects.filter(status='AVAILABLE'),
        widget=forms.SelectMultiple(
            attrs={'class': 'form-control'}
        ),
    )


class EditContactForm(forms.Form):
    required_css_class = 'required'

    last_ticket = forms.IntegerField(
        label='Ticket',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number', 'min': 1,
                   'max': 2147483647}
        )
    )
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Name'}))
    email = forms.EmailField(
        max_length=200,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder':
                   'exemple@exemple.com', 'type': 'email'}))


class AddContactForm(forms.Form):
    required_css_class = 'required'

    last_ticket = forms.IntegerField(
        label='Ticket',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number', 'min': 1,
                   'max': 2147483647}
        )
    )
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Name'}))
    email = forms.EmailField(
        max_length=200,
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': 'exemple@exemple.nic',
                   'type': 'email'}))
    TYPES = (('noc', 'NOC'),
             ('adm', 'ADM'),
             ('peer', 'PEER'),
             ('com', 'COM'),)
    # types = forms.ChoiceField(choices=TYPES, widget=forms.RadioSelect())
    noc = forms.BooleanField(required=False)
    adm = forms.BooleanField(required=False)
    peer = forms.BooleanField(required=False)
    com = forms.BooleanField(required=False)


class EditContactsMapForm(forms.Form):
    required_css_class = 'required'

    last_ticket = forms.CharField(
        label='Ticket',
        max_length=20,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number', 'min': 1,
                   'max': 2147483647}
        )
    )
    noc_contact = forms.ModelChoiceField(
        queryset=Contact.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}))
    adm_contact = forms.ModelChoiceField(
        queryset=Contact.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}))
    peer_contact = forms.ModelChoiceField(
        queryset=Contact.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}))
    com_contact = forms.ModelChoiceField(
        queryset=Contact.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}))


class MigrateSwitchForm(forms.Form):
    required_css_class = 'required'

    last_ticket = forms.CharField(
        label='Ticket',
        max_length=20,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number', 'min': 1,
                   'max': 2147483647}
        )
    )

    switch = forms.ModelChoiceField(
        queryset=Switch.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}))

    new_model = forms.ModelChoiceField(
        queryset=SwitchModel.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}))

    description = forms.CharField(
        label='Description',
        max_length=80,
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'rows': '3'}
        )
    )


class EditDescriptionForm(forms.Form):
    required_css_class = 'required'

    description = forms.CharField(
        label='Description',
        max_length=80,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'rows': '3'}
        )
    )


class EditOrganizationForm(forms.Form):
    required_css_class = 'required'

    name = forms.CharField(max_length=200, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Name'}))
    shortname = forms.CharField(max_length=200, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Shortname'}))
    url = forms.CharField(max_length=200, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'www.example.com.br',
               'type': "url"}))
    address = forms.CharField(max_length=200, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'Street example, 11000'}))


class EditServiceStatusForm(forms.Form):
    required_css_class = 'required'
    statuses = (('ALLOCATED', 'Allocated for customer but not in use'),
                ('INTERNAL', 'Internal servers in production'),
                ('PRODUCTION', 'Customer in production'),
                ('QUARANTINE', 'Customer in test/quarantine'), )
    status = forms.ChoiceField(
        required=False, widget=forms.Select(
            attrs={'class': 'form-control'}), choices=statuses)


class EditServiceTagForm(forms.Form):
    tag = forms.IntegerField(
        label='Tag',
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number',
                   'min': 0, 'max': 4095}
        )
    )


class EditServicePrefixLimitForm(forms.Form):
    required_css_class = 'required'
    prefix_limit = forms.IntegerField(
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Prefix Limit'}),
        validators=[MinValueValidator(0)])


class AddASContactForm(forms.Form):

    default_attr = {'class': 'form-control new-as-input'}

    # These fields will be used to create a ContactsMap Obj
    ticket = forms.IntegerField(
        label='Ticket',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control new-as-input', 'type': 'number',
                   'min': 1, 'max': 2147483647}
        )
    )
    asn = forms.CharField(required=False, widget=forms.HiddenInput())

    ix = forms.ModelChoiceField(
        queryset=IX.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}))

    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False)

    org_name = forms.CharField(widget=forms.HiddenInput(), required=False)

    org_shortname = forms.CharField(widget=forms.HiddenInput(), required=False)

    org_cnpj = forms.CharField(widget=forms.HiddenInput(), required=False)

    org_url = forms.URLField(widget=forms.HiddenInput(), required=False)

    org_addr = forms.CharField(widget=forms.HiddenInput(), required=False)

    contact_name_noc = forms.CharField(
        label='NOC Name',
        widget=forms.TextInput(attrs=default_attr))

    contact_email_noc = forms.EmailField(
        label='NOC Email',
        widget=forms.TextInput(
            attrs={'class': 'form-control new-as-input', 'type': 'email'}))

    contact_phone_noc = forms.CharField(
        label='NOC Phone',
        widget=forms.TextInput(attrs=default_attr))

    contact_name_adm = forms.CharField(
        label='ADM Name',
        widget=forms.TextInput(attrs=default_attr))
    contact_email_adm = forms.EmailField(
        label='ADM Email',
        widget=forms.TextInput(
            attrs={'class': 'form-control new-as-input', 'type': 'email'}))
    contact_phone_adm = forms.CharField(
        label='ADM Phone',
        widget=forms.TextInput(attrs=default_attr))

    contact_name_peer = forms.CharField(
        label='PEER Name',
        widget=forms.TextInput(attrs=default_attr))
    contact_email_peer = forms.EmailField(
        label='PEER Email',
        widget=forms.TextInput(
            attrs={'class': 'form-control new-as-input', 'type': 'email'}))
    contact_phone_peer = forms.CharField(
        label='PEER Phone',
        widget=forms.TextInput(attrs=default_attr))

    contact_name_com = forms.CharField(
        label='Commercial Name',
        widget=forms.TextInput(attrs=default_attr))
    contact_email_com = forms.EmailField(
        label='Commercial Email',
        widget=forms.TextInput(
            attrs={'class': 'form-control new-as-input', 'type': 'email'}))
    contact_phone_com = forms.CharField(
        label='Commercial Phone',
        widget=forms.TextInput(attrs=default_attr))

    contact_name_org = forms.CharField(
        label='Organization Name',
        widget=forms.TextInput(attrs=default_attr),
        required=False)
    contact_email_org = forms.EmailField(
        label='Organization Email',
        widget=forms.TextInput(
            attrs={'class': 'form-control new-as-input', 'type': 'email'}),
        required=False)
    contact_phone_org = forms.CharField(
        label='Organization Phone',
        widget=forms.TextInput(attrs=default_attr),
        required=False)


class GenericMLPAUsedChannelForm(forms.Form):
    required_css_class = 'required'

    MLPA_CATEGORIES = (('', ('-----')),
                       ('only_v4', _("Only IPv4")),
                       ('only_v6', _("Only IPv6")),
                       ('v4_and_v6', _("IPv4 and IPv6")))

    last_ticket = forms.IntegerField(
        label='Ticket',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number', 'min': 1,
                   'max': 2147483647}
        )
    )

    service_option = forms.ChoiceField(
        choices=MLPA_CATEGORIES, required=True, widget=forms.Select(
            attrs={'class': 'form-control',
                    'onchange' : "update_mlpa_form_by_service_option(false)",}))

    mlpav4_address = forms.CharField(
        required=False, widget=forms.TextInput(
            attrs={'class': 'form-control mlpav4'})
    )
    tag_v4 = forms.IntegerField(
        validators=[MinValueValidator(MIN_TAG_NUMBER),
                    MaxValueValidator(MAX_TAG_NUMBER)],
        required=False, widget=forms.TextInput(
            attrs={'class': 'form-control keyup-tag', 'type': 'number',
                   'min': MIN_TAG_NUMBER, 'max':  MAX_TAG_NUMBER,
                   'required': 'required'})
    )
    inner_v4 = forms.IntegerField(
        validators=[MinValueValidator(MIN_TAG_NUMBER),
                    MaxValueValidator(MAX_TAG_NUMBER)],
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'type': 'number',
                   'min': MIN_TAG_NUMBER,
                   'max': MAX_TAG_NUMBER})
    )

    mlpav6_address = forms.CharField(
        required=False, widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tag_v6 = forms.IntegerField(
        validators=[MinValueValidator(MIN_TAG_NUMBER),
                    MaxValueValidator(MAX_TAG_NUMBER)],
        required=False, widget=forms.TextInput(
            attrs={'class': 'form-control keyup-tag', 'type': 'number',
                   'min': MIN_TAG_NUMBER, 'max': MAX_TAG_NUMBER,
                   'required': 'required'}
        )
    )
    inner_v6 = forms.IntegerField(
        validators=[MinValueValidator(MIN_TAG_NUMBER),
                    MaxValueValidator(MAX_TAG_NUMBER)],
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number', 'min': 0,
                   'max': MAX_TAG_NUMBER})
    )

    asn = forms.IntegerField(required=False, widget=forms.HiddenInput())
    code = forms.CharField(required=False, widget=forms.HiddenInput())
    channel = forms.CharField(required=False, widget=forms.HiddenInput())


class AddPortChannel(forms.Form):
    required_css_class = 'required'
    ports = forms.ModelMultipleChoiceField(
        queryset=Port.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}))


class CreatePortPhysicalInterfaceForm(forms.Form):
    required_css_class = 'required'
    last_ticket = forms.IntegerField(
        label='Ticket',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number', 'min': 1,
                   'max': 2147483647}
        ),
    )
    connector_type = forms.ChoiceField(
        choices=CONNECTOR_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    port_type = forms.ChoiceField(
        choices=PORT_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    serial_number = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'maxlength': 255})
    )


class EditCixTypeForm(forms.Form):
    required_css_class = 'required'
    cix_type = forms.ChoiceField(
        choices=CustomerChannel.CIX_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'}))


class EditPortPhysicalInterfaceForm(forms.Form):
    required_css_class = 'required'
    physical_interface = forms.ModelChoiceField(
        queryset=PhysicalInterface.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}))


class AddIXtoASNForm(forms.Form):
    required_css_class = 'required'
    ticket = forms.IntegerField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Ticket',
                   'type': 'number', 'min': 1, 'max': 2147483647}
        )
    )
    ix = forms.ModelChoiceField(
        queryset=IX.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}))


class GenericMLPANewChannelForm(forms.Form):
    required_css_class = 'required'

    MLPA_CATEGORIES = (('', ('-----')),
                       ('only_v4', _("Only IPv4")),
                       ('only_v6', _("Only IPv6")),
                       ('v4_and_v6', _("IPv4 and IPv6")))

    last_ticket = forms.IntegerField(
        label='Ticket',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number', 'min': 1,
                   'max': 2147483647}
        )
    )

    pix = forms.ModelChoiceField(
        queryset=PIX.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': "update_switch_by_pix_bilateral_form(\"mlpa\", \"#id_pix\", \"#id_switch\")"}))

    switch = forms.ModelChoiceField(
        queryset=Switch.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange' : "update_channels_by_switch_asn_mpla_form()" }))

    customer_channel = forms.ModelChoiceField(
        queryset=CustomerChannel.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}))

    service_option = forms.ChoiceField(
        choices=MLPA_CATEGORIES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': "update_mlpa_form_by_service_option(true)",}))

    mlpav4_address = forms.CharField(
        required=False, widget=forms.TextInput(
            attrs={'class': 'form-control mlpav4'})
    )
    tag_v4 = forms.IntegerField(
        validators=[MinValueValidator(MIN_TAG_NUMBER),
                    MaxValueValidator(MAX_TAG_NUMBER)],
        required=False,
        widget=forms.TextInput(
            attrs={'class': ' form-control keyup-tag', 'type': 'number',
                   'min': MIN_TAG_NUMBER, 'max': MAX_TAG_NUMBER})
    )
    inner_v4 = forms.IntegerField(
        validators=[MinValueValidator(MIN_TAG_NUMBER),
                    MaxValueValidator(MAX_TAG_NUMBER)],
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'type': 'number',
                   'min': MIN_TAG_NUMBER,
                   'max': MAX_TAG_NUMBER})
    )

    mlpav6_address = forms.CharField(
        required=False, widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tag_v6 = forms.IntegerField(
        validators=[MinValueValidator(MIN_TAG_NUMBER),
                    MaxValueValidator(MAX_TAG_NUMBER)],
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control keyup-tag',
                                      'type': 'number',
                                      'min': MIN_TAG_NUMBER,
                                      'max': MAX_TAG_NUMBER})
    )
    inner_v6 = forms.IntegerField(
        validators=[MinValueValidator(MIN_TAG_NUMBER),
                    MaxValueValidator(MAX_TAG_NUMBER)],
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'type': 'number',
                   'min': MIN_TAG_NUMBER,
                   'max': MAX_TAG_NUMBER})
    )
    asn = forms.IntegerField(required=False, widget=forms.HiddenInput())
    code = forms.CharField(required=False, widget=forms.HiddenInput())

class AddBilateralNewChannelForm(forms.Form):
    required_css_class = 'required'

    last_ticket = forms.IntegerField(
        label='Ticket',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number',
                   'min': 1, 'max': 2147483647}))

    ix = forms.CharField(widget=forms.HiddenInput())
    origin_asn = forms.CharField(widget=forms.HiddenInput())

    asn = forms.IntegerField(
        label='ASN Connection',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number',
                   'min': 1, 'max': 2147483647}))

    bilateral_type = forms.ChoiceField(
        choices=Bilateral.BILATERAL_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'}),)

    origin_pix = forms.ModelChoiceField(
        label = 'Origin pix',
        queryset=PIX.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': "update_switch_by_pix_bilateral_form(\"bilateral\", \"#id_origin_pix\", \"#id_origin_switch\")",}))

    origin_switch = forms.ModelChoiceField(
        label = 'Origin switch',
        queryset=Switch.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': "update_channels_by_switch_asn_bilateral_form(true)",}))

    origin_channel = forms.ModelChoiceField(
        label = 'Origin channel',
        queryset=CustomerChannel.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',}))

    mac_search = forms.CharField(
        label = 'Search Channel by MAC',
        required=False,
        widget=forms.TextInput(
            attrs={
            'class': 'form-control',
            'onchange':"search_channel_by_mac()",}))

    pix = forms.ModelChoiceField(
        label = 'Peer pix',
        queryset=PIX.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': "update_switch_by_pix_bilateral_form(\"bilateral\", \"#id_pix\", \"#id_switch\")",}))

    switch = forms.ModelChoiceField(
        label = 'Peer switch',
        queryset=Switch.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': "update_channels_by_switch_asn_bilateral_form(false)",}))

    customer_channel = forms.ModelChoiceField(
        label = 'Peer channel',
        queryset=CustomerChannel.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': "update_tags_by_bilateral_type()",}))

    tag_a = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    tag_b = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    inner_a = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}))

    inner_b = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}))


class AddBilateralForm(forms.Form):
    required_css_class = 'required'

    last_ticket = forms.IntegerField(
        label='Ticket',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number',
                   'min': 1, 'max': 2147483647}))

    asn = forms.IntegerField(
        label='ASN Connection',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number',
                   'min': 1, 'max': 2147483647}))

    bilateral_type = forms.ChoiceField(
        choices=Bilateral.BILATERAL_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'}),)

    pix = forms.ModelChoiceField(
        queryset=PIX.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': "update_switch_by_pix_bilateral_form(\"bilateral\", \"#id_pix\", \"#id_switch\")",}))

    switch = forms.ModelChoiceField(
        queryset=Switch.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': "update_channels_by_switch_asn_bilateral_form(false)",}))

    origin_channel = forms.CharField(widget=forms.HiddenInput())

    ix = forms.CharField(widget=forms.HiddenInput())

    customer_channel = forms.ModelChoiceField(
        label = 'Peer channel',
        queryset=CustomerChannel.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': "update_tags_by_bilateral_type()",}))

    tag_a = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    tag_b = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    inner_a = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}))

    inner_b = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}))


class EditConfiguredCapacityPort(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Port
        fields = ['last_ticket', 'configured_capacity']
        widgets = {
            'last_ticket': forms.TextInput(
                attrs={'class': 'form-control', 'type': 'number', 'min': 1,
                       'max': 2147483647}),
            'configured_capacity': forms.Select(
                attrs={'class': 'form-control'}),
        }


class EditDioPortForm(forms.Form):

    required_css_class = 'required'
    last_ticket = forms.IntegerField(
        label='Ticket',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number',
                   'min': 1, 'max': 2147483647})
    )

    ix_position = forms.CharField(
        label='IX Position',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'min': 1})
    )

    dc_position = forms.CharField(
        label='DC Position',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'min': 10})
    )

    switch = forms.ModelChoiceField(
        queryset=Switch.objects.all(),
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    ports = forms.ModelChoiceField(
        queryset=Port.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class AddDIOToPIXForm(forms.Form):
    required_css_class = 'required'

    last_ticket = forms.IntegerField(
        label='Ticket',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number',
                   'min': 1, 'max': 2147483647})
    )

    dio_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control', 'pattern': '.{10,255}',
                'title': 'Must contain at least ten characters'
            })
    )
    number_of_ports = forms.IntegerField(
        label='Number of ports',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number',
                   'min': 1})
    )

    datacenter_position = forms.CharField(
        label='Datacenter position',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'})
    )

    ix_position = forms.CharField(
        label='IX position pattern',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control'})
    )


class ReserveIPResourceForm(forms.Form):
    required_css_class = 'required'
    IPv4 = forms.ModelMultipleChoiceField(
        queryset=IPv4Address.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    IPv6 = forms.ModelMultipleChoiceField(
        queryset=IPv6Address.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}))


class ReleaseIPResourceForm(forms.Form):
    required_css_class = 'required'
    IPv4 = forms.ModelMultipleChoiceField(
        queryset=IPv4Address.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    IPv6 = forms.ModelMultipleChoiceField(
        queryset=IPv6Address.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}))


class ReservePortResourceForm(forms.Form):
    required_css_class = 'required'
    ports_to_reserve = forms.ModelMultipleChoiceField(
        queryset=Port.objects.all(),
        widget=forms.SelectMultiple(
            attrs={'class': 'form-control'}
        ),
    )


class ReleasePortResourceForm(forms.Form):
    required_css_class = 'required'
    ports_to_release = forms.ModelMultipleChoiceField(
        queryset=Port.objects.all(),
        widget=forms.SelectMultiple(
            attrs={'class': 'form-control'}
        ),
    )


class AllocateTagStatusForm(forms.Form):
    required_css_class = 'required'
    tag_to_allocate = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}))


class DeallocateTagStatusForm(forms.Form):
    required_css_class = 'required'
    tag_to_deallocate = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}))


class ReserveTagResourceForm(forms.Form):
    required_css_class = 'required'
    tag_to_reserve = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}))


class ReleaseTagResourceForm(forms.Form):
    required_css_class = 'required'
    tag_to_release = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}))


class AddSwitchModuleForm(forms.Form):
    required_css_class = 'required'

    last_ticket = forms.IntegerField(
        label='Ticket',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number',
                   'min': 1, 'max': 2147483647})
    )

    capacity = forms.ChoiceField(
        required=True,
        widget=forms.Select(
        attrs={'class': 'form-control'}),
        choices=CAPACITIES_MAX)

    connector_type = forms.ChoiceField(
        required=True,
        widget=forms.Select(
            attrs={'class': 'form-control'}),
        choices=CONNECTOR_TYPES)

    name_format = forms.CharField(
        label='Ports name format',
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control',
            'placeholder':'For example {0}',})
    )
    begin = forms.IntegerField(
        label='First Port',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number',
                   'min': 1, 'max': 9999})
    )
    end = forms.IntegerField(
        label='Last Port',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number',
                   'min': 1, 'max': 9999})
    )
    model = forms.CharField(
        label='Module Model',
        required=True,
        widget=forms.TextInput(
        attrs={'class': 'form-control'})
    )
    vendor = forms.ChoiceField(
        required=True,
        widget=forms.Select(
        attrs={'class': 'form-control'}), choices=VENDORS)

class CreateSwitchForm(forms.Form):
    required_css_class = 'required'

    last_ticket = forms.CharField(
        label='Ticket',
        max_length=20,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number', 'min': 1,
                   'max': 2147483647}
        )
    )

    mgmt_ip = forms.CharField(
        label="Management IP",
        required=True, widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )

    model = forms.ModelChoiceField(
        label="Switch Model",
        queryset=SwitchModel.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    is_pe = forms.BooleanField(
        label="IS PE",
        required=False
    )

    translation = forms.BooleanField(
        label="Translation",
        required=False
    )

    create_ports = forms.BooleanField(
        label="Create Ports",
        required=False
    )


class CreateOrganizationForm(forms.Form):
    required_css_class = 'required'

    last_ticket = forms.CharField(
        label='Ticket',
        max_length=20,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number', 'min': 1,
                   'max': 2147483647}
        )
    )
    name = forms.CharField(
        label='Owner',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    shortname = forms.CharField(
        label='Short Name',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    cnpj = forms.CharField(
        label='CNPJ',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False)

    url = forms.URLField(
        label='URL',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'url'}))

    country_code = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False)

    state = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False)

    city = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False)

    address = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False)

    zip_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False)

    description = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control'}), required=False)


class CreatePixForm(forms.Form):
    required_css_class = 'required'

    last_ticket = forms.CharField(
        label='Ticket',
        max_length=20,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number', 'min': 1,
                   'max': 2147483647}
        )
    )

    description = forms.CharField(widget=forms.Textarea(
        attrs={'class':'form-control'}),required=False)

    code = forms.CharField(
        label='PIX Code', widget=forms.TextInput(
            attrs={'class':'form-control'})
    )


class CreateSwitchModelForm(forms.Form):
    required_css_class = 'required'

    last_ticket = forms.CharField(
        label='Ticket',
        max_length=20,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number', 'min': 1,
                   'max': 2147483647}
        )
    )

    description = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control'}), required=False)

    model = forms.CharField(
        label="Model", widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )

    vendor = forms.ChoiceField(
        required=True,
        label="Switch Vendor",
        choices=VENDORS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # SwitchPortRange

    capacity = forms.ChoiceField(
        label='Capacity',
        required=True,
        widget=forms.Select(
            attrs={'class': 'form-control'}),
        choices=CAPACITIES_MAX)

    connector_type = forms.ChoiceField(
        label='Connector type',
        required=True,
        widget=forms.Select(
            attrs={'class': 'form-control'}), choices=CONNECTOR_TYPES)

    name_format = forms.CharField(
        label="Name format",
        max_length=255,
        required=True, widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )

    begin = forms.CharField(
        label='Begin',
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number', 'min': 0}
        )
    )

    end = forms.CharField(
        label='End',
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number', 'min': 0}
        )
    )

    # SwitchPortRange for extra ports (ex. uplink)

    extra_ports = forms.BooleanField(
        label="Extra Ports (Not Module Ports)",
        required=False
    )

    capacity_extra = forms.ChoiceField(
        label='Capacity [Extra Ports]',
        required=False,
        widget=forms.Select(
            attrs={'class': 'form-control'}),
        choices=CAPACITIES_MAX)

    connector_type_extra = forms.ChoiceField(
        label='Connector type [Extra Ports]',
        required=False,
        widget=forms.Select(
            attrs={'class': 'form-control'}), choices=CONNECTOR_TYPES)

    begin_extra = forms.CharField(
        label='Begin [Extra Ports]',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number', 'min': 0}
        )
    )

    end_extra = forms.CharField(
        label='End [Extra Ports]',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number', 'min': 0}
        )
    )

    def clean(self):
        if not self.cleaned_data['extra_ports']:
            self.cleaned_data['begin_extra'] = 0
            self.cleaned_data['end_extra'] = 0
        return super(CreateSwitchModelForm, self).clean()


class CreateUplinkCoreChannelModelForm(forms.Form):

    required_css_class = 'required'

    last_ticket = forms.CharField(
        label='Ticket',
        required=True,
        max_length=20,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number', 'min': 1,
                   'max': 2147483647}
        )
    )

    CHANNEL_TYPES = (('UPLINK', "UPLINK"), ('CORE', "CORE"), )
    channel_type = forms.ChoiceField(choices=CHANNEL_TYPES)

    channel_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    channel_ports = forms.ModelMultipleChoiceField(
        queryset=Port.objects.filter(status='AVAILABLE'),
        widget=forms.SelectMultiple(
            attrs={'class': 'form-control'}),
        required=False,
    )

    destination_ports = forms.ModelMultipleChoiceField(
        queryset=Port.objects.filter(status='AVAILABLE'),
        widget=forms.SelectMultiple(
            attrs={'class': 'form-control'}
        ),
    )
    destination_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    create_tags = forms.BooleanField(required=False)


class CreateIXForm(forms.Form):

    required_css_class = 'required'

    last_ticket = forms.CharField(
        label='Ticket',
        required=True,
        max_length=20,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'number', 'min': 1,
                   'max': 2147483647}
        )
    )

    code = forms.CharField(
        label='Code',
        required=True,
        min_length=2,
        max_length=4,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )

    shortname = forms.CharField(
        label='Reverse DNS',
        required=True,
        max_length=16,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )

    fullname = forms.CharField(
        label='Fullname',
        required=True,
        max_length=48,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )

    ipv4_prefix = forms.CharField(
        label='IPv4 Prefix',
        required=True,
        max_length=18,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )

    ipv6_prefix = forms.CharField(
        label='IPv6 Prefix',
        required=True,
        max_length=43,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )

    management_prefix = forms.CharField(
        label='Management Prefix',
        required=True,
        max_length=18,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )

    create_ips = forms.BooleanField(
        label="Create IPs",
        required=False,
    )

    tags_policies = (('ix_managed', "IX_managed"),
                     ('distributed', "Distributed"),)

    tags_policy = forms.ChoiceField(
        required=True,
        widget=forms.Select(
            attrs={'class': 'form-control'}), choices=tags_policies)
