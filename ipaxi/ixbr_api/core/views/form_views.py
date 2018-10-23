from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.generic import View
from django.views.generic.edit import FormView

from ixbr_api.core.use_cases import (
    create_dio_ports_use_case as create_dio_ports_use_case,)

from ..forms import (AddASContactForm, AddBilateralForm,
                     AddBilateralNewChannelForm, AddContactForm,
                     AddCustomerChannelForm, AddDIOToPIXForm, AddIXtoASNForm,
                     AddMACServiceForm, AddPortChannel, AddSwitchModuleForm,
                     AllocateTagStatusForm, CreateIXForm,
                     CreateOrganizationForm, CreatePixForm,
                     CreatePortPhysicalInterfaceForm, CreateSwitchForm,
                     CreateSwitchModelForm, CreateUplinkCoreChannelModelForm,
                     DeallocateTagStatusForm, EditCixTypeForm,
                     EditConfiguredCapacityPort, EditContactForm,
                     EditContactsMapForm, EditDescriptionForm, EditDioPortForm,
                     EditMLPAv4Form, EditMLPAv6Form, EditOrganizationForm,
                     EditPortPhysicalInterfaceForm, EditServicePrefixLimitForm,
                     EditServiceStatusForm, EditServiceTagForm,
                     GenericMLPANewChannelForm, GenericMLPAUsedChannelForm,
                     MigrateSwitchForm, PhoneForm, ReleaseIPResourceForm,
                     ReleasePortResourceForm, ReleaseTagResourceForm,
                     ReserveIPResourceForm, ReservePortResourceForm,
                     ReserveTagResourceForm,)
from ..models import (ASN, DIO, IX, PIX, BilateralPeer, ChannelPort,
                      Contact, ContactsMap, CustomerChannel, DIOPort,
                      DownlinkChannel, IPv4Address, IPv6Address, MACAddress,
                      MLPAv4, MLPAv6, Monitorv4, Organization, Phone,
                      PhysicalInterface, Port, Service, Switch, SwitchModel,
                      SwitchPortRange, Tag, create_tag_by_channel_port,)
from ..use_cases.bilateral_use_case import (create_bilateral,
                                            define_bilateral_case,)
from ..use_cases.channels_use_cases import create_uplink_core_channel_use_case
from ..use_cases.mac_address_converter_to_system_pattern import (
    MACAddressConverterToSystemPattern,)
from ..use_cases.migrate_switch import migrate_switch
from ..use_cases.switch_module_use_cases import (
    create_switch_module_with_ports_use_case,)
from ..use_cases.tags_use_cases import (get_free_tags,
                                        get_tag_without_all_service,
                                        get_tag_without_bilateral,
                                        instantiate_tag,)
from ..utils import port_utils
from ..utils.constants import CAPACITIES_CONF, SWITCH_MODEL_CHANNEL_PREFIX
from ..utils.consulta import MAC
from ..utils.last_ticket_update import updatelastticket
from ..utils.logger import ixapilog
from ..utils.mixins import AjaxableResponseMixin, LogsMixin
from ..validators import validate_cnpj


class AddASContactFormView(LoginRequiredMixin, FormView):
    """Creates a new AS instance in the system.

     In order to add a new AS, several data is required (i.e. contacts,
     IX and organization). These data are collected from the ticket system
     and used create the new AS instance.
     This class is used by:
      - ixbr_api/core/urls.py (directly)
      - ixbr_api/templates/as/as_add.html (as url)
      - ix-api/ixbr_api/templates/forms/add_as_contact_form.html (as url)
    """

    template_name = 'forms/add_as_contact_form.html'
    form_class = AddASContactForm
    initial = {}
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, asn):
        form = self.form_class()
        self.context = {
            'form': form,
            'asn': asn,
        }
        form.fields['asn'].widget.attrs['value'] = asn
        return render(request, self.template_name, self.context)

    @staticmethod
    def __add_contact(contact_dict):
        """Creates a contact instance to be used in Contactsmap.

        Args:
            contact_dict: the contact dict with contact data

        Returns: a contact object to be used in a Contactsmap instance.

        """

        cur_contact = Contact()
        cur_contact.name = contact_dict['name']
        cur_contact.email = contact_dict['email']
        cur_contact.last_ticket = contact_dict['ticket']
        cur_contact.modified_by_id = contact_dict['user_id']
        cur_contact.save()

        if contact_dict['phone'] is not None:
            cur_phone = Phone()
            cur_phone.number = contact_dict['phone']
            cur_phone.last_ticket = contact_dict['ticket']
            cur_phone.contact = cur_contact
            cur_phone.save()

        return cur_contact

    @ixapilog
    def form_valid(self, form):
        user = self.request.user
        form_data = form.cleaned_data
        cur_ticket = int(form_data['ticket'])

        try:
            with transaction.atomic():

                # Get the IX
                cur_ix = form_data['ix']

                # Organization Info
                cur_organization = form_data['organization']

                # Administrative Contact
                contact_dict = {
                    'name': form_data['contact_name_adm'],
                    'email': form_data['contact_email_adm'],
                    'phone': form_data['contact_phone_adm'],
                    'ticket': cur_ticket,
                    'user_id': user.id
                }

                if not cur_organization:
                    contact_map = ContactsMap.objects.filter(
                        organization__name=form_data['org_name'].upper(),
                        ix=cur_ix)
                    if not contact_map:
                        cur_organization = Organization.objects.create(
                            name=form_data['org_name'].upper(),
                            last_ticket=cur_ticket,
                            shortname=form_data['org_shortname'],
                            cnpj=form_data['org_cnpj'],
                            url=form_data['org_url'],
                            address=form_data['org_addr']
                        )

                cur_adm_contact = self.__add_contact(contact_dict)

                # NOC Contact
                contact_dict['name'] = form_data['contact_name_noc']
                contact_dict['email'] = form_data['contact_email_noc']
                cur_noc_contact = self.__add_contact(contact_dict)

                # Commercial Contact
                contact_dict['name'] = form_data['contact_name_com']
                contact_dict['email'] = form_data['contact_email_com']
                cur_com_contact = self.__add_contact(contact_dict)

                # Peer Contact
                contact_dict['name'] = form_data['contact_name_peer']
                contact_dict['email'] = form_data['contact_email_peer']
                cur_peer_contact = self.__add_contact(contact_dict)

                # Organization Contact
                contact_dict['name'] = form_data['contact_name_org']
                contact_dict['email'] = form_data['contact_email_org']
                cur_org_contact = self.__add_contact(contact_dict)

                # ASN
                cur_asn = ASN()
                cur_asn.number = form_data['asn']
                cur_asn.modified_by_id = user.id
                cur_asn.last_ticket = cur_ticket
                cur_asn.save()

                # Contact Map
                cur_contactsmap = ContactsMap()
                cur_contactsmap.organization = cur_organization
                cur_contactsmap.ix = cur_ix
                cur_contactsmap.asn = cur_asn
                cur_contactsmap.noc_contact = cur_noc_contact
                cur_contactsmap.adm_contact = cur_adm_contact
                cur_contactsmap.org_contact = cur_org_contact
                cur_contactsmap.peer_contact = cur_peer_contact
                cur_contactsmap.com_contact = cur_com_contact
                cur_contactsmap.modified_by_id = user.id
                cur_contactsmap.last_ticket = cur_ticket
                # FIXME
                cur_contactsmap.peering_url = "http://abc.com"
                cur_contactsmap.save()

                messages.success(self.request, "AS Registered")
                return redirect(self.request.META.get('PATH_INFO'))

        except ValidationError as e:
            messages.error(self.request, str(e))
            return redirect(self.request.META.get('PATH_INFO'))

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return redirect(self.request.META.get('PATH_INFO'))


class MACDeleteView(LoginRequiredMixin, View):
    """Delete a MAC
    Attributes:
        mac (str): MAC Address.
        service (str): UUID of service.
        ma (<class 'django.db.models.query.QuerySet'>): Get a MAC speciefied.
        data (dic): Dictionary that return the result
            to be printed.
    returns:

        If the MAC was deleted successfully, it will return the following
        dictionary
        {
        'result' : 'Your MAC was deleted successfully'
        }

        Otherwise, it will return the following dictionary:
        {
        'result' : 'error'
        }
    """

    @ixapilog
    def get(self, request, *args, **kwargs):
        try:
            mac_uuid = request.GET.get("mac")
            service_uuid = request.GET.get("service")

            mac = MACAddress.objects.get_or_none(pk=mac_uuid)
            service = Service.get_objects_filter('uuid', service_uuid).pop()

            service.mac_addresses.remove(mac)

            if not mac.is_in_any_service():
                mac.delete()
            data = {'result': 'Your MAC was deleted successfully'}
        except:
            data = {'result': 'error'}

        return JsonResponse(data)


class EditMLPAv4FormView(LoginRequiredMixin, LogsMixin, FormView):

    """This class has, as main objective, to change the IPv4 address of an
       MLPAv4 service

    Attributes:
        context (dic): It is a dictionary of information to be printed on the
            screen
        form_class (Instance of forms.EditMLPAv4Form): Instance of the
            EditMLPAv4Form class, this class contains all form information
        http_method_names (list): List containing the request types
        initial (dict): Boot Dictionary, if you need to start a field with a
            value
        template_name (str): Name of the template used for this form
        mlpav4 (<class 'django.db.models.query.QuerySet'>): Get a MLPAv4 by
            the primary key passed by parameter
    Returns:
        If the IPv4 address was changed successfully, it will return a
            successful message, else it will return a
        message with the error that occurred
    """

    template_name = 'forms/edit_mlpav4_form.html'
    form_class = EditMLPAv4Form
    initial = {}
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, service, code):
        form = self.form_class()
        used_v4_addresses = IPv4Address.objects.filter(
            Q(address__in=MLPAv4.objects.all().values_list(
                'mlpav4_address', flat=True)) |
            Q(address__in=Monitorv4.objects.all().values_list(
                'monitor_address', flat=True)), ix=code).distinct()
        V4_QUERY = IPv4Address.objects.filter(ix=code).exclude(
            pk__in=used_v4_addresses.values_list('pk', flat=True))
        form.fields['mlpav4_address'].queryset = V4_QUERY
        self.context = {
            'form': form,
            'service': service,
            'code': code}
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            with transaction.atomic():

                mlpav4 = MLPAv4.objects.get(pk=self.kwargs['service'])
                mlpav4_address = form.cleaned_data['mlpav4_address']
                mlpav4.mlpav4_address = mlpav4_address
                mlpav4.save()

                messages.success(self.request, "MLPAv4 saved")
                return redirect(self.request.META.get('PATH_INFO'))

        except ValidationError as e:
            messages.error(self.request, str(e))
            return redirect(self.request.META.get('PATH_INFO'))


class EditMLPAv6FormView(LoginRequiredMixin, LogsMixin, FormView):
    """This class has, as main objective, to change the IPv6 address of an
        MLPAv6 service

    Attributes:
        context (dic): It is a dictionary of information to be printed on the
            screen
        form_class (Instance of forms.EditMLPAv6Form): Instance of the
            EditMLPAv6Form class, this class contains all form information
        http_method_names (list): List containing the request types
        initial (dict): Boot Dictionary, if you need to start a field with a
            value
        template_name (str): Name of the template used for this form
        mlpav6 (<class 'django.db.models.query.QuerySet'>): Get a MLPAv6 by
            the primary key passed by parameter
    Returns:
        If the IPv6 address was changed successfully, it will return a
            successful message, else it will return a message with the error
            that occurred
    """
    template_name = 'forms/edit_mlpav6_form.html'
    form_class = EditMLPAv6Form
    initial = {}
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, service, code):
        form = self.form_class()
        used_v6_addresses = IPv6Address.objects.filter(
            Q(address__in=MLPAv6.objects.all().values_list(
                'mlpav6_address', flat=True))).distinct()
        V6_QUERY = IPv6Address.objects.filter(ix=code).exclude(
            pk__in=used_v6_addresses.values_list('pk', flat=True))
        form.fields['mlpav6_address'].queryset = V6_QUERY
        self.context = {
            'form': form,
            'service': service,
            'code': code}
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            with transaction.atomic():
                mlpav6_address = form.cleaned_data['mlpav6_address']

                mlpav6 = MLPAv6.objects.get(pk=self.kwargs['service'])
                mlpav6.mlpav6_address = mlpav6_address
                mlpav6.save()

                messages.success(self.request, "MLPAv6 saved")
                return redirect(self.request.META.get('PATH_INFO'))

        except ValidationError as e:
            messages.error(self.request, str(e))
            return redirect(self.request.META.get('PATH_INFO'))


class AddMACServiceFormView(LoginRequiredMixin, LogsMixin, FormView):
    """To add a mac to a service

    Attributes:
        form_class (<class 'ixbr_api.core.forms.AddMACServiceForm'>):
        Class that contains the form to add a mac to a service.
        http_method_names (list): Requisition methods
        context (dic): Dictionary that return a set of informations
            to be printed.
        address (str): Get the Mac Address.
        last_ticket (int): Get the last_ticket.
        description (str): Get the description of a MAC Address.
        template_name (str): forms/add_mac_service_form.html
    returns:
        If the request method is a get, will return a dict context with
        the fields of form. If method requisition is different of get,
        return success message case the mac was successfully added or
        error message case mac was not added
    """

    template_name = 'forms/add_mac_service_form.html'
    form_class = AddMACServiceForm
    initial = {}
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, service):
        service_object = Service.get_objects_filter('pk', service)[0]
        form = self.form_class()
        related_service = None
        if type(service_object) == MLPAv4:
            related_service = service_object.get_related_service()
            form.fields['copy_mac'].label = "Copy MAC to MLPAv6"
        elif type(service_object) == MLPAv6:
            related_service = service_object.get_related_service()
            form.fields['copy_mac'].label = "Copy MAC to MLPAv4"

        if not related_service:
            form.fields.pop('copy_mac')

        self.context = {
            'form': form,
            'service': service}
        return render(request, self.template_name, self.context)

    @updatelastticket
    @ixapilog
    def form_valid(self, form):
        service = Service.get_objects_filter(
            'pk', self.kwargs['service'])[0]
        copy_mac = form.cleaned_data['copy_mac']
        address = form.cleaned_data['address']
        description = form.cleaned_data['description']
        last_ticket = form.cleaned_data['last_ticket']
        user = self.request.user
        service_mac = list()

        address = MACAddressConverterToSystemPattern(address). \
            mac_address_converter()

        ''' Validation if accept uppercase letters
        PS: Change core.validator.py regex
        ADDRESS_REGEX = re.compile(Regex().mac.upper())
        if ADDRESS_REGEX.match(address):
            address = address.lower()'''

        def add_mac_service(address, service):
            vendor = MAC('macvendors1.db').get_vendor(address)

            if vendor is None:
                raise ValidationError("Vendor not Found")
            mac = MACAddress.objects.get_or_none(address=address)
            if not mac:
                mac = MACAddress.objects.create(address=address,
                                                description=description,
                                                last_ticket=last_ticket)
                self.makeLog([mac.__class__], mac.__dict__)
            else:
                service_mac = mac.get_service_of_mac()
                if service_mac and service_mac.asn.number != service.asn.number:
                    raise ValidationError("MAC is allocated in another asn")

            service.mac_addresses.add(mac.address)
            service.user = user
            service.last_ticket = last_ticket

            if len(service.mac_addresses.all()) == 2:
                messages.warning(self.request, "Warn: Two Mac Addresses " +
                                 "are Allowed only during migrations")
            service.save()

        try:
            with transaction.atomic():
                add_mac_service(address, service)
                if copy_mac:
                    related_service = service.get_related_service()
                    add_mac_service(address, related_service)

            messages.success(self.request, "MAC registered")
            return redirect(self.request.META.get('PATH_INFO'))
        except ValidationError as e:
            messages.error(self.request, str(e.messages[0]))
            return redirect(self.request.META.get('PATH_INFO'))
        except ValueError as e:
            messages.error(self.request, str(e))
            return redirect(self.request.META.get('PATH_INFO'))

    def form_invalid(self, form):
        context = {
            'form': form,
            'service': self.kwargs['service']}
        messages.error(self.request, form.errors)
        return render(self.request, self.template_name, context)


class AddDIOToPIXFormView(LoginRequiredMixin, LogsMixin, FormView):
    """Add a DIO to a PIX

    Attributes:
        form_class (<class 'ixbr_api.core.forms.AddDIOToPIXForm'>):
        Class that contains the form that adds a new DIO.
        http_method_names (list): Requisition methods
        context (dict): Dictionary that return a set of informations
            to be printed.
        template_name (str): forms/add_dio_form.html
    returns:
        If the request method is a get, will return a dict context with
        the fields of form. If method requisition is different of get,
        return success message case the DIO was successfully added or
        error message case DIO was not added
    """
    template_name = 'forms/add_dio_form.html'
    form_class = AddDIOToPIXForm
    initial = {}
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, pix):
        pix = PIX.objects.get(uuid=pix)
        self.context = {
            'form': self.form_class(),
            'pix': pix}
        return render(request, self.template_name, self.context)

    @updatelastticket
    @ixapilog
    def form_valid(self, form):
        user = self.request.user
        try:
            with transaction.atomic():
                pix = PIX.objects.get(pk=self.kwargs['pix'])
                last_ticket = form.cleaned_data['last_ticket']
                dio_name = form.cleaned_data['dio_name']
                number_of_ports = form.cleaned_data['number_of_ports']
                ix_position_pattern = form.cleaned_data['ix_position']
                datacenter_position_pattern = form.cleaned_data[
                    'datacenter_position']

                new_dio = DIO.objects.create(pix=pix,
                                             name=dio_name,
                                             last_ticket=last_ticket,
                                             modified_by=user)

                create_dio_ports_use_case.create_dio_ports(
                    ix_position_pattern,
                    datacenter_position_pattern,
                    number_of_ports,
                    new_dio,
                    last_ticket,
                    user)

                messages.success(self.request, "DIO saved")
                return redirect(self.request.META.get('PATH_INFO'))

        except ValidationError as e:
            context = {
                'form': form,
                'pix': PIX.objects.get(pk=self.kwargs['pix'])
            }
            messages.error(self.request, str(e.messages[0]))
            return render(self.request, self.template_name, context)


class GenericMLPAUsedChannelFormView(AjaxableResponseMixin,
                                     LoginRequiredMixin,
                                     LogsMixin,
                                     FormView):
    template_name = 'forms/generic_mlpa_used_channel.html'
    form_class = GenericMLPAUsedChannelForm
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, asn, channel, code):
        customer_channel = CustomerChannel.objects.get(pk=channel)

        form = self.form_class()
        form.fields['asn'].widget.attrs['value'] = asn
        form.fields['channel'].widget.attrs['value'] = channel
        form.fields['code'].widget.attrs['value'] = code
        self.context = {
            'form': form,
            'channel': channel,
            'code': code,
            'asn': asn,
            'customer_channel': customer_channel
        }

        return render(request, self.template_name, self.context)

    @updatelastticket
    @ixapilog
    def form_valid(self, form):
        return GenericMLPANewChannelFormView.form_valid(self, form)


class EditPhoneFormView(LoginRequiredMixin, LogsMixin, FormView):
    """This class has, as main objective, to edit a phone

    Attributes:
        context (dic): Dictionary with information to be printed on the screen
            form_class (Instance of forms.PhoneForm): Instance of the PhoneForm
            class, this class contains all form information
        http_method_names (list): List containing the request types
        initial (dict): Boot Dictionary, if you need to start a field with a
        value template_name (str): Name of the template used for this form
        old_phone (<class 'django.db.models.query.QuerySet'>): Get a Phone
            by the primary key passed by parameter
        new_phone (object): New object of the models.Phone class, with all
            modifications
    Returns:
        If the old phone was successfully removed and the new one successfully
            added, it will return a successful message,
            else a message with the error occurred
    """

    template_name = 'forms/edit_phone_form.html'
    form_class = PhoneForm
    initial = {}
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, phone):
        form = self.form_class()
        old_phone = get_object_or_404(Phone, pk=phone)
        form.fields['phone'].widget.attrs['value'] = old_phone.number
        form.fields['category'].initial = old_phone.category
        form.fields['last_ticket'].widget.attrs['value'] = old_phone. \
            last_ticket
        form.fields['last_ticket'].widget.attrs['readonly'] = True
        self.context = {
            'form': form,
            'phone': phone
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        user = self.request.user
        old_phone = Phone.objects.get(pk=self.kwargs['phone'])
        try:
            with transaction.atomic():
                number = form.cleaned_data['phone']
                category = form.cleaned_data['category']
                last_ticket = form.cleaned_data['last_ticket']
                new_phone = Phone.objects.create(
                    last_ticket=last_ticket,
                    number=number,
                    category=category,
                    modified_by=user,
                    contact=old_phone.contact)
                new_phone.save()
                old_phone.delete()

                self.context = {
                    'phone': new_phone.pk,
                    'messenger': 'success'
                }
                messages.success(self.request, "Phone saved")
                return HttpResponse(render_to_string(
                    'forms/modal_feedback.html', self.context))
        except ValidationError as e:
            self.context = {
                'phone': old_phone.pk,
                'messenger': str(e.messages[0])
            }
            messages.error(self.request, str(e.messages[0]))
            return HttpResponse(render_to_string(
                'forms/modal_feedback.html', self.context))


class AddPhoneFormView(LoginRequiredMixin, LogsMixin, FormView):
    """This class has, as main objective, to add a new phone

    Attributes:
        context (dict): Dictionary with information to be printed on the screen
        form_class (Instance of forms.PhoneForm): Instance of the PhoneForm
            class, this class contains all form information
        http_method_names (list): List containing the request types
        template_name (str): Name of the template used for this form
        phone (object): New object of the models. Phone class, with all
            the data of a phone
        number (int): Phone number entered by user in form
        category (str): Category selected by the user in the form
        last_ticket (int): Last ticket entered by the user in the form
        contact (<class 'django.db.models.query.QuerySet'>): Get a Contact by
            the primary key passed by parameter

    Returns:
        A successful message if the phone has been added or an error message
        otherwise.
    """
    template_name = 'forms/add_phone_form.html'
    form_class = PhoneForm
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, contact):
        self.context = {
            'form': self.form_class(),
            'contact': contact
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            with transaction.atomic():
                number = form.cleaned_data['phone']
                category = form.cleaned_data['category']
                last_ticket = form.cleaned_data['last_ticket']
                contact = Contact.objects.get(pk=self.kwargs['contact'])

                phone = Phone.objects.create(
                    number=number,
                    category=category,
                    contact=contact,
                    last_ticket=last_ticket)
                phone.save()

                messages.success(self.request, "Phone saved")
                return redirect(self.request.META.get('PATH_INFO'))
        except ValidationError as e:
            messages.error(self.request, str(e))
            return redirect(self.request.META.get('PATH_INFO'))


class DeletePhoneView(LoginRequiredMixin, View):

    """This class has, as main objective, to delete a phone

    Attributes:
        phone (str): Primary key of the phone you want to delete, passed by
            kwargs
        phone_object (<class 'django.db.models.query.QuerySet'>): Get a
            Contact by the primary key passed by the GET method
        data (dic): Dictionary with information to be printed on the screen
    Returns:
        If the phone has been deleted successfully, it will return a
            successful message,
        else it will return a message with the error occurred
    """

    def get(self, request, *args, **kwargs):
        phone = kwargs["phone"]
        try:
            with transaction.atomic():
                phone_object = Phone.objects.get(pk=phone)
                phone_object.delete()

                data = {'result': 'Phone was deleted successfully'}
        except ValidationError:
            data = {'result': 'error'}

        return JsonResponse(data)


class AddCustomerChannelFormView(AjaxableResponseMixin,
                                 LoginRequiredMixin,
                                 LogsMixin,
                                 FormView):
    """This class has, as main objective, to add a new channel

    Attributes:
        context (dict): Dictionary with information to be printed on the screen
        form_class (Instance of forms.AddCustomerChannelForm): Instance of the
            AddCustomerChannelForm class, this class contains all form information
        http_method_names (list): List containing the request types
        initial (dict): Boot Dictionary, if you need to start a field with a
            value
        template_name (str): Name of the template used for this form
        phone_object (object): New object of the models.Phone class, with all
            the data of a phone
        number (int): Phone number entered by user in form
        category (str): Category selected by the user in the form
        last_ticket (int): Last ticket entered by the user in the form
        contact (<class 'django.db.models.query.QuerySet'>): Get a Contact by
            the primary key passed by parameter
    Returns:
        If the new channel has been added successfully, it will return a
            successful message,
        else it will return a message with the error occurred
    """
    template_name = 'forms/add_customer_channel_form.html'
    form_class = AddCustomerChannelForm
    initial = {}
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, asn, pix):
        pix_object = get_object_or_404(PIX, pk=pix)

        switch_set = pix_object.switch_set.filter(pix=pix_object)

        switch_list = ()
        for switch in switch_set:
            switch_list += (
                (switch.pk, switch.management_ip),
            )

        form = self.form_class(switchs=switch_list)

        form.fields['pix'].widget.choices.queryset = PIX.objects.filter(pk=pix)
        form.fields['pix'].widget.attrs['readonly'] = True

        form.fields['pix_uuid'].widget.attrs['value'] = pix
        form.fields['asn'].widget.attrs['value'] = asn

        self.context = {
            'form': form,
            'asn': asn,
            'pix': pix,
            'switch': switch_list,
        }

        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            with transaction.atomic():
                pix = self.request.POST.get('pix', False) or \
                    self.request.POST.get('pix_uuid', False)
                switch = self.request.POST.get('switch', False)
                channel_name = "ct-{0}".format(
                    self.request.POST.get('channel_name', False))
                as_number = self.request.POST.get('asn', False)
                cix_type = self.request.POST.get('cix_type', False)
                ports = self.request.POST.getlist('ports')
                ticket = int(self.request.POST.get('ticket', False))
                # TODO: need more informations on model of Translation Channel
                # to continue
                # translation_channel = \
                #   self.request.POST['translation_channel']

                ix_object = IX.objects.get(pix__pk=pix)
                asn = ASN.objects.get(pk=as_number)
                switch_object = get_object_or_404(Switch, pk=switch)

                is_lag = False
                if len(ports) > 1:
                    is_lag = True

                if(ix_object.tags_policy == 'ix_managed' or
                        not switch_object.is_pe):
                    tags_type = 'Indirect-Bundle-Ether'
                else:
                    tags_type = 'Direct-Bundle-Ether'

                channel_port = ChannelPort.objects.create(
                    tags_type=tags_type,
                    last_ticket=ticket,
                    create_tags=False,
                )
                for p in ports:
                    p_object = get_object_or_404(Port, pk=p)
                    channel_port.port_set.add(p_object)
                    p_object.status = 'UNAVAILABLE'
                    p_object.save()

                if tags_type == 'Direct-Bundle-Ether' and switch_object.is_pe:
                    create_tag_by_channel_port(channel_port, True, 3)

                customer_channel = CustomerChannel.objects.create(
                    cix_type=cix_type, asn=asn, name=channel_name,
                    is_lag=is_lag, channel_port=channel_port,
                    last_ticket=ticket, is_mclag=False
                )

                for port in channel_port.port_set.all():
                    port.status = 'CUSTOMER'
                    port.save()

                customer_channel.channel_port.save()

                context = {'message': 'success'}
                return HttpResponse(
                    render_to_string('forms/modal_feedback_service.html',
                                     context))

        except ValidationError as e:
            if type(e.messages) == list:
                context = {'message': str(e)}
            else:
                context = {'message': dict(e)}
            return HttpResponse(
                render_to_string('forms/modal_feedback_service.html',
                                 context))


class AddPixToAsnFormView(AjaxableResponseMixin,
                          LoginRequiredMixin,
                          LogsMixin,
                          FormView):
    """This class has, as main objective, to add a new channel

    Attributes:
        context (dict): Dictionary with information to be printed on the screen
        form_class (Instance of forms.AddCustomerChannelForm): Instance of the
            AddCustomerChannelForm class, this class contains all form information
        http_method_names (list): List containing the request types
        initial (dict): Boot Dictionary, if you need to start a field with a
            value
        template_name (str): Name of the template used for this form
        phone_object (object): New object of the models.Phone class, with all
            the data of a phone
        number (int): Phone number entered by user in form
        category (str): Category selected by the user in the form
        last_ticket (int): Last ticket entered by the user in the form
        contact (<class 'django.db.models.query.QuerySet'>): Get a Contact by
            the primary key passed by parameter
    Returns:
        If the new channel has been added successfully, it will return a
            successful message,
        else it will return a message with the error occurred
    """

    template_name = 'forms/add_customer_channel_form.html'
    form_class = AddCustomerChannelForm
    initial = {}
    http_method_names = ['get', 'post']

    def get(self, request, ix, asn):
        switch_set = Switch.objects.filter(pix__ix=ix)

        switch_list = ()
        for switch in switch_set:
            switch_list += (
                (switch.pk, switch.management_ip),
            )

        form = self.form_class(switchs=switch_list)

        form.fields['asn'].widget.attrs['value'] = asn
        form.fields['pix'].queryset = PIX.objects.filter(ix=ix)

        form.fields['switch'].queryset = Switch.objects.filter(
            pix=PIX.objects.filter(ix=ix).first())
        switch_initial = form.fields['switch'].queryset.first()
        form.fields['switch'].initial = switch_initial
        form.fields['ports'].queryset = Port.objects.filter(
            switch=switch_initial, status='AVAILABLE')

        self.context = {
            'form': form,
            'asn': asn,
            'ix': ix,
        }

        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        return AddCustomerChannelFormView.form_valid(self, form)


class EditContactFormView(LoginRequiredMixin, LogsMixin, FormView):

    """This class has, as main objective, to edit a contact

    Attributes:
        context (dic): Dictionary with information to be printed on the screen
        form_class (Instance of forms.EditContactForm): Instance of the
            EditContactForm class, this class contains all form information
        http_method_names (list): List containing the request types
        initial (dict): Boot Dictionary, if you need to start a field with a
            value
        template_name (str): Name of the template used for this form
        name (str): New contact name entered by the user in the form
        email (str): New contact email entered by the user in the form
        last_ticket (int): New contact last ticket entered by the user in the
            form
        contact_object (<class 'django.db.models.query.QuerySet'>): Get a
            Contact by the primary key passed by parameter
        new_contact (object): New object of the models.Contact class, with all
            modifications
        contacsmap_object (<class 'django.db.models.query.QuerySet'>): Get a
            ContactsMap by the primary key passed by parameter
        type_contact (str): The contact type, passed by parameter
    Returns:
        If the old contact was deleted successfully and the new contact with
            the modifications was successfully added, it will return a success
            message, else it will return a message with the error occurred
    """

    template_name = 'forms/edit_contact_form.html'
    form_class = EditContactForm
    initial = {}
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, contact, contactsmap, type_contact):
        form = self.form_class()
        contact_object = get_object_or_404(Contact, pk=contact)
        form.fields['name'].widget.attrs['value'] = contact_object.name
        form.fields['email'].widget.attrs['value'] = contact_object.email
        form.fields['last_ticket'].widget.attrs['value'] = \
            contact_object.last_ticket

        self.context = {
            'form': form,
            'contact': contact,
            'contactsmap': contactsmap,
            'type_contact': type_contact
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        user = self.request.user
        try:
            with transaction.atomic():
                name = form.cleaned_data['name']
                email = form.cleaned_data['email']
                last_ticket = form.cleaned_data['last_ticket']
                contact_object = Contact.objects.get(pk=self.kwargs['contact'])

                new_contact = Contact.objects.create(
                    name=name, email=email, last_ticket=last_ticket,
                    modified_by=user)
                new_contact.save()
                contacsmap_object = ContactsMap.objects.get(
                    pk=self.kwargs['contactsmap'])
                if self.kwargs['type_contact'] == 'noc':
                    contacsmap_object.noc_contact = new_contact
                    if contacsmap_object.adm_contact.pk == contact_object.pk:
                        contacsmap_object.adm_contact = new_contact

                    if contacsmap_object.com_contact.pk == contact_object.pk:
                        contacsmap_object.com_contact = new_contact

                    if contacsmap_object.peer_contact.pk == contact_object.pk:
                        contacsmap_object.peer_contact = new_contact

                elif self.kwargs['type_contact'] == 'adm':
                    contacsmap_object.adm_contact = new_contact
                    if contacsmap_object.noc_contact.pk == contact_object.pk:
                        contacsmap_object.noc_contact = new_contact

                    if contacsmap_object.com_contact.pk == contact_object.pk:
                        contacsmap_object.com_contact = new_contact

                    if contacsmap_object.peer_contact.pk == contact_object.pk:
                        contacsmap_object.peer_contact = new_contact

                elif self.kwargs['type_contact'] == 'per':
                    contacsmap_object.peer_contact = new_contact
                    if contacsmap_object.noc_contact.pk == contact_object.pk:
                        contacsmap_object.noc_contact = new_contact

                    if contacsmap_object.com_contact.pk == contact_object.pk:
                        contacsmap_object.com_contact = new_contact

                    if contacsmap_object.adm_contact.pk == contact_object.pk:
                        contacsmap_object.adm_contact = new_contact

                elif self.kwargs['type_contact'] == 'com':
                    contacsmap_object.com_contact = new_contact
                    if contacsmap_object.noc_contact.pk == contact_object.pk:
                        contacsmap_object.noc_contact = new_contact

                    if contacsmap_object.adm_contact.pk == contact_object.pk:
                        contacsmap_object.adm_contact = new_contact

                    if contacsmap_object.peer_contact.pk == contact_object.pk:
                        contacsmap_object.peer_contact = new_contact

                phones = Phone.objects.filter(contact=contact_object)
                for phone in phones:
                    new_phone = Phone.objects.create(
                        number=phone.number, category=phone.category,
                        modified_by=user, contact=new_contact,
                        last_ticket=phone.last_ticket)
                    new_phone.save()
                for phone in phones:
                    phone.delete()

                contacsmap_object.save()

                self.context = {
                    'contact': new_contact.pk,
                    'contactsmap': contacsmap_object.pk,
                    'type_contact': self.kwargs['type_contact'],
                    'messenger': 'success'
                }

                messages.success(self.request, "Contact saved")

                return HttpResponse(
                    render_to_string('forms/modal_feedback.html',
                                     self.context))

        except ValidationError as e:
            self.context = {
                'contact': new_contact.pk,
                'contactsmap': contacsmap_object.pk,
                'type_contact': self.kwargs['type_contact'],
                'messenger': str(e.messages[0])
            }
            messages.error(self.request, str(e.messages[0]))
            return HttpResponse(
                render_to_string('forms/modal_feedback.html',
                                 self.context))


class EditContactsMapFormView(LoginRequiredMixin, LogsMixin, FormView):

    """This class has, as main objective, to edit a contactsmap

    Attributes:
        context (dic): Dictionary with information to be printed on the screen
        form_class (Instance of forms.EditContactForm): ContactsMapEditForm
        http_method_names (list): List containing the request types
        initial (dict): Boot Dictionary, if you need to start a field with a
            value
        template_name (str): Name of the template used for this form
        contactsmap_object (<class 'django.db.models.query.QuerySet'>): Get a
            ContactsMap by the primary key passed by paramete
        contacts (<class 'django.db.models.query.QuerySet'>): Get all contacts
            from an ix and asn passed by parameter
        noc_contact (Relationship with the contact): Relationship with the
            contact, noc contact is a type of contact
        adm_contact (Relationship with the contact): Relationship with the
            contact, adm contact is a type of contact
        peer_contact (Relationship with the contact): Relationship with the
            contact, peer contact is a type of contact
        com_contact (Relationship with the contact): Relationship with the
            contact, com contact is a type of contact
    Returns:
        If the contactsmap has been edited successfully, it will return a
            successful message,
        else it will return a message with the error occurred
    """

    template_name = 'forms/edit_contacts_map_form.html'
    form_class = EditContactsMapForm
    initial = {}
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, contactsmap, ix, asn):
        form = self.form_class()
        contactsmap_object = get_object_or_404(ContactsMap, pk=contactsmap)
        contacts = Contact.objects.filter(
            Q(pk__in=ContactsMap.objects.filter(ix=ix, asn=asn).values_list(
                'noc_contact', flat=True)) |
            Q(pk__in=ContactsMap.objects.filter(ix=ix, asn=asn).values_list(
                'adm_contact', flat=True)) |
            Q(pk__in=ContactsMap.objects.filter(ix=ix, asn=asn).values_list(
                'peer_contact', flat=True)) |
            Q(pk__in=ContactsMap.objects.filter(ix=ix, asn=asn).values_list(
                'com_contact', flat=True)))
        form.fields['noc_contact'].queryset = contacts
        form.fields['adm_contact'].queryset = contacts
        form.fields['peer_contact'].queryset = contacts
        form.fields['com_contact'].queryset = contacts

        form.fields['noc_contact'].initial = contactsmap_object.noc_contact
        form.fields['adm_contact'].initial = contactsmap_object.adm_contact
        form.fields['peer_contact'].initial = contactsmap_object.peer_contact
        form.fields['com_contact'].initial = contactsmap_object.com_contact
        form.fields['last_ticket'].widget.attrs['value'] = \
            contactsmap_object.last_ticket
        form.fields['last_ticket'].widget.attrs['readonly'] = True

        self.context = {
            'form': form,
            'contactsmap': contactsmap,
            'ix': ix,
            'asn': asn
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            with transaction.atomic():
                contactsmap_object = get_object_or_404(
                    ContactsMap,
                    pk=self.kwargs['contactsmap'])
                noc_contact = form.cleaned_data['noc_contact']
                adm_contact = form.cleaned_data['adm_contact']
                peer_contact = form.cleaned_data['peer_contact']
                com_contact = form.cleaned_data['com_contact']

                contactsmap_object.noc_contact = noc_contact
                contactsmap_object.adm_contact = adm_contact
                contactsmap_object.peer_contact = peer_contact
                contactsmap_object.com_contact = com_contact
                contactsmap_object.save()

                messages.success(self.request, "Contactsmap saved")
                return redirect(self.request.META.get('PATH_INFO'))
        except ValidationError as e:
            messages.error(self.request, str(e.messages[0]))
            return redirect(self.request.META.get('PATH_INFO'))


class EditOrganizationFormView(LoginRequiredMixin, LogsMixin, FormView):

    """This class has, as main objective, redenrize and submit
    the form to edit an organization.

    Attributes:
        context (dict): Dictionary with all information
            to be printed on the screen
        form_class (Instance of forms.EditOrganizationForm): EditOrganizationForm
        http_method_names (list): List containing the request types
        initial (dict): Boot Dictionary, if you need to start a field
            with a value
        template_name (str): Name of the template used for this form
        organization_object (<class 'django.db.models.query.QuerySet'>): Get a
            Organization by the primary key passed by paramete
        name (str): Name of the organization, this data comes from the
            form when it is submitted
        shortname (str): Shortname of organization, this data comes from the
            form when it is submitted
        url (str): URL of organization, this data comes from the form when
            it is submitted
        address (str): Address of organization, this data comes from the for
            when it is submitted

    Returns:
        If the organization has been edited successfully,
        it will return a successful message, else it will return
        a message with the error occurred.

    """

    template_name = 'forms/edit_organization_form.html'
    form_class = EditOrganizationForm
    initial = {}
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, organization):
        form = self.form_class()
        organization_object = get_object_or_404(Organization, pk=organization)
        form.fields['name'].widget.attrs['value'] = organization_object.name
        form.fields['shortname'].widget.attrs['value'] = \
            organization_object.shortname
        form.fields['url'].widget.attrs['value'] = organization_object.url
        form.fields['address'].widget.attrs['value'] = \
            organization_object.address

        self.context = {
            'form': form,
            'organization': organization
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            with transaction.atomic():
                organization_object = get_object_or_404(
                    Organization, pk=self.kwargs['organization'])
                name = form.cleaned_data['name']
                shortname = form.cleaned_data['shortname']
                url = form.cleaned_data['url']
                address = form.cleaned_data['address']

                organization_object.name = name
                organization_object.shortname = shortname
                organization_object.url = url
                organization_object.address = address
                organization_object.save()

                messages.success(self.request, "Organization saved")
                return redirect(self.request.META.get('PATH_INFO'))
        except ValidationError as e:
            messages.error(self.request, str(e.messages[0]))
            return redirect(self.request.META.get('PATH_INFO'))


class EditServiceStatusFormView(LoginRequiredMixin, LogsMixin, FormView):

    """This class has, as main objective, redenrize and submit the form to
       edit the status of service

    Attributes:
        context (dic): Dictionary with all information to be printed on the
            screen
        form_class (Instance of forms.EditServiceStatusForm):
            EditServiceStatusForm
        http_method_names (list): List containing the request types
        initial (dict): Boot Dictionary, if you need to start a field with a
            value
        template_name (str): Name of the template used for this form
        service_list (list): List of the services
    Returns:
        If the status of service has been edited successfully, it will return
            a successful message,
        else it will return a message with the error occurred
    """

    template_name = 'forms/edit_service_status_form.html'
    form_class = EditServiceStatusForm
    initial = {}
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, service):
        form = self.form_class()
        service_list = []
        service_list.extend(MLPAv4.objects.filter(
            pk=service))
        service_list.extend(MLPAv6.objects.filter(
            pk=service))
        service_list.extend(BilateralPeer.objects.filter(pk=service))
        service_list = service_list[0]
        form.fields['status'].initial = service_list.status
        self.context = {
            'form': form,
            'service': service
        }

        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            with transaction.atomic():
                service_list = []
                service_list.extend(MLPAv4.objects.filter(
                    pk=self.kwargs['service']))
                service_list.extend(MLPAv6.objects.filter(
                    pk=self.kwargs['service']))
                service_list.extend(BilateralPeer.objects.filter(
                    pk=self.kwargs['service']))
                service_list = service_list[0]
                status = form.cleaned_data['status']
                service_list.status = status
                service_list.save()

                messages.success(self.request, "Status saved")
                return redirect(self.request.META.get('PATH_INFO'))

        except ValidationError as e:
            messages.error(self.request, str(e.messages[0]))
            return redirect(self.request.META.get('PATH_INFO'))


class EditServicePrefixLimitFormView(LoginRequiredMixin, LogsMixin, FormView):

    """This class has, as main objective, redenrize and submit the form to
       edit the prefix limit of service

    Attributes:
        context (dic): Dictionary with all information to be printed on the
            screen
        form_class (Instance of forms.EditServicePrefixLimitForm):
            EditServicePrefixLimitForm
        http_method_names (list): List containing the request types
        initial (dict): Boot Dictionary, if you need to start a field with a
            value
        template_name (str): Name of the template used for this form
        service_list (list): List of the services
    Returns:
        If the prefix limit of service has been edited successfully, it will
            return a successful message,
        else it will return a message with the error occurred
    """

    template_name = 'forms/edit_service_prefix_limit_form.html'
    form_class = EditServicePrefixLimitForm
    initial = {}
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, service):
        form = self.form_class()
        service_list = []
        service_list.extend(MLPAv4.objects.filter(
            pk=service))
        service_list.extend(MLPAv6.objects.filter(
            pk=service))
        service_list.extend(BilateralPeer.objects.filter(pk=service))
        service_list = service_list[0]

        form.fields['prefix_limit'].widget.attrs['value'] = \
            service_list.prefix_limit

        self.context = {
            'form': form,
            'service': service
        }

        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            with transaction.atomic():
                service_list = []
                service_list.extend(MLPAv4.objects.filter(
                    pk=self.kwargs['service']))
                service_list.extend(MLPAv6.objects.filter(
                    pk=self.kwargs['service']))
                service_list.extend(BilateralPeer.objects.filter(
                    pk=self.kwargs['service']))
                service_list = service_list[0]
                prefix_limit = form.cleaned_data['prefix_limit']
                service_list.prefix_limit = prefix_limit
                service_list.save()

                messages.success(self.request, "Prefix Limit saved")
                return redirect(self.request.META.get('PATH_INFO'))

        except ValidationError as e:
            messages.error(self.request, str(e.messages[0]))
            return redirect(self.request.META.get('PATH_INFO'))


class EditServiceTagFormView(LoginRequiredMixin, LogsMixin, FormView):

    """This class has, as main objective, redenrize and submit the form to
       edit the tag of service

    Attributes:
        context (dic): Dictionary with all information to be printed on the
            screen
        form_class (Instance of forms.EditServiceTagForm): EditServiceTagForm
        http_method_names (list): List containing the request types
        initial (dict): Boot Dictionary, if you need to start a field with a
            value
        template_name (str): Name of the template used for this form
        service_list (list): List of the services
    Returns:
        If the tag of service has been edited successfully, it will return a
            successful message,
        else it will return a message with the error occurred
    """

    template_name = 'forms/edit_service_tag_form.html'
    form_class = EditServiceTagForm
    initial = {}
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, service, code):
        form = self.form_class()

        self.context = {
            'form': form,
            'service': service,
            'code': code
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            with transaction.atomic():
                tag = form.cleaned_data['tag']

                tag_new = Tag.objects.get(tag=tag, ix=self.kwargs['code'])
                service_list = []
                service_list.extend(MLPAv4.objects.filter(
                    pk=self.kwargs['service']))
                service_list.extend(MLPAv6.objects.filter(
                    pk=self.kwargs['service']))
                service_list.extend(BilateralPeer.objects.filter(
                    pk=self.kwargs['service']))
                service_list = service_list[0]

                tag_old = service_list.tag

                bilateral = BilateralPeer.objects.filter(pk=service_list.pk)
                if bilateral:
                    free_tags = get_tag_without_all_service(
                        ix=self.kwargs['code'],
                        channel=service_list.customer_channel)

                else:
                    free_tags = get_tag_without_bilateral(
                        ix=self.kwargs['code'],
                        channel=service_list.customer_channel)

                if tag_new in free_tags:
                    service_list.tag = tag_new

                    service_list.save()

                    tag_new.update_status('PRODUCTION')
                    if tag_old not in free_tags:
                        tag_old.update_status('AVAILABLE')

                else:
                    raise ValidationError("Tag status is PRODUCTION")

                messages.success(self.request, "Tag saved")
                return redirect(self.request.META.get('PATH_INFO'))

        except ValidationError as e:
            messages.error(self.request, str(e.messages[0]))
            return redirect(self.request.META.get('PATH_INFO'))
        except ValueError as e:
            messages.error(self.request, str(e))
            return redirect(self.request.META.get('PATH_INFO'))


class AddContactFormView(LoginRequiredMixin, LogsMixin, FormView):

    """This class has, as main objective, redenrize and submit the form to add
       a new contact

    Attributes:
        context (dic): Dictionary with all information to be printed on the
            screen
        form_class (Instance of forms.AddContactForm): AddContactForm
        http_method_names (list): List containing the request
            types
        initial (dict): Boot Dictionary, if you need to start a field with a
            value
        template_name (str): Name of the template used for this
            form
        last_ticket (int): Last ticket of contact, this data comes from the
            form when it is submitted
        name (str): Name of contact, this data comes from the form when it is
            submitted
        email (str): Email of contact, this data comes from the form when it
            is submitted
        noc (Bool): True if the type of contact is NOC, else, is False, this
            data comes from the form when it is submitted
        adm (Bool): True if the type of contact is ADM, else, is False, this
            data comes from the form when it is submitted
        peer (Bool): True if the type of contact is PEER, else, is False, this
            data comes from the form when it is submitted
        com (Bool): True if the type of contact is COM, else, is False, this
            data comes from the form when it is submitted
        contactsmap_object (<class 'django.db.models.query.QuerySet'>): Get a
            ContactsMap by the primary key passed by paramete
        contact (<class 'django.db.models.query.QuerySet'>): New created
            contact
    Returns:
         If the contact has been added successfully, it will return a
            successful message,
        else it will return a message with the error occurred
    """

    template_name = 'forms/add_contact_form.html'
    form_class = AddContactForm
    initial = {}
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, contactsmap):
        self.context = {
            'form': self.form_class(),
            'contactsmap': contactsmap
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        user = self.request.user
        try:
            with transaction.atomic():
                last_ticket = form.cleaned_data['last_ticket']
                name = form.cleaned_data['name']
                email = form.cleaned_data['email']
                noc = form.cleaned_data['noc']
                adm = form.cleaned_data['adm']
                peer = form.cleaned_data['peer']
                com = form.cleaned_data['com']

                contact = Contact.objects.create(
                    name=name, email=email,
                    last_ticket=last_ticket, modified_by=user)
                contact.save()

                contactsmap_object = ContactsMap.objects.get_or_none(
                    pk=self.kwargs['contactsmap'])

                if noc:
                    contactsmap_object.noc_contact = contact
                if adm:
                    contactsmap_object.adm_contact = contact
                if peer:
                    contactsmap_object.peer_contact = contact
                if com:
                    contactsmap_object.com_contact = contact

                contactsmap_object.save()

                messages.success(self.request, "Contact saved")
                return redirect(self.request.META.get('PATH_INFO'))
        except ValidationError as e:
            messages.error(self.request, str(e.messages[0]))
            return redirect(self.request.META.get('PATH_INFO'))


class EditCixTypeFormView(LoginRequiredMixin, LogsMixin, FormView):
    """This class has, as main objective, render and submit the form to edit a
       channel CIX Type

    Attributes:
        context (dic): Dictionary with all information to be printed on the
            screen
        form_class (Instance of forms.EditCixTypeForm): EditCixTypeForm
        http_method_names (list): List containing the request types
        initial (dict): Boot Dictionary, if you need to start a field with a
            value
        template_name (str): Name of the template used for this form
    Returns:
        If the channel CIX Type has been edited successfully, it will return a
            successful message,
        otherwise it will return a message with the error.
    """

    template_name = 'forms/edit_cix_type_form.html'
    form_class = EditCixTypeForm
    initial = {}
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, channel):
        form = self.form_class()
        channel_object = CustomerChannel.objects.get(uuid=channel)
        cix_type = channel_object.cix_type

        form.fields['cix_type'].initial = cix_type

        self.context = {
            'channel': channel_object,
            'form': form,
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            with transaction.atomic():
                cix_type = form.cleaned_data['cix_type']
                channel_object = CustomerChannel.objects.get(
                    pk=self.kwargs['channel'])
                channel_object.cix_type = cix_type
                channel_object.save()

                messages.success(self.request, "Port saved")
                return redirect(self.request.META.get('PATH_INFO'))
        except ValidationError as e:
            messages.error(self.request, str(e.messages[0]))
            return redirect(self.request.META.get('PATH_INFO'))


class EditPortPhysicalInterfaceFormView(LoginRequiredMixin,
                                        LogsMixin,
                                        FormView):

    """This class has, as main objective, redenrize and submit the form to
       edit a port physical interface

    Attributes:
        context (dic): Dictionary with all information to be printed on the
            screen
        form_class (Instance of forms.EditPortPhysicalInterfaceForm):
            EditPortPhysicalInterfaceForm
        http_method_names (list): List containing the request types
        initial (dict): Boot Dictionary, if you need to start a field with a
            value
        template_name (str): Name of the template used for this form
        port_object (<class 'django.db.models.query.QuerySet'>): Get a Port by
            the primary key passed by paramete
        physical_interface (<class 'django.db.models.query.QuerySet'>): Get a
            PhysicalInterface by the primary key passed by paramete
    Returns:
        If the port physical interface has been edited successfully, it will
            return a successful message,
        otherwise it will return a message with the error.
    """

    template_name = 'forms/edit_port_physical_interface_form.html'
    form_class = EditPortPhysicalInterfaceForm
    initial = {}
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, port):
        form = self.form_class()
        port_object = Port.objects.get(pk=port)
        physical_interface = PhysicalInterface.get_free_physical_interfaces()

        form.fields['physical_interface'].queryset = physical_interface
        form.fields['physical_interface'].initial = \
            port_object.physical_interface

        self.context = {
            'form': form,
            'port': port
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            with transaction.atomic():
                physical_interface = form.cleaned_data['physical_interface']
                port_object = Port.objects.get(pk=self.kwargs['port'])
                port_object.physical_interface = physical_interface
                port_object.save()
                messages.success(self.request, "Port saved")
                return redirect(self.request.META.get('PATH_INFO'))
        except ValidationError as e:
            messages.error(self.request, str(e.messages[0]))
            return redirect(self.request.META.get('PATH_INFO'))


class CreateOrganizationFormView(LoginRequiredMixin,
                                 LogsMixin,
                                 FormView):
    template_name = 'forms/create_organization_form.html'
    form_class = CreateOrganizationForm
    initial = {}
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    @ixapilog
    def form_valid(self, form):
        try:
            form_data = form.cleaned_data

            organization = Organization()
            organization.last_ticket = form_data['last_ticket']
            organization.name = form_data['name']
            organization.shortname = form_data['shortname']
            if form_data['cnpj']:
                validate_cnpj(form_data['cnpj'])
                organization.cnpj = form_data['cnpj']
            organization.url = form_data['url']
            organization.country_code = form_data['country_code']
            organization.state = form_data['state']
            organization.city = form_data['city']
            organization.address = form_data['address']
            organization.zip_code = form_data['zip_code']
            organization.description = form_data['description']

            organization.save()
            messages.success(self.request, "Organization created successfully")
            return redirect(self.request.META.get('PATH_INFO'))
        except ValidationError as e:
            messages.error(self.request, str(e.messages[0]))
            return redirect(self.request.META.get('PATH_INFO'))

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return redirect(self.request.META.get('PATH_INFO'))


class CreatePortPhysicalInterfaceFormView(LoginRequiredMixin,
                                          LogsMixin,
                                          FormView):
    template_name = 'forms/create_port_physical_interface_form.html'
    form_class = CreatePortPhysicalInterfaceForm
    initial = {}
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    @ixapilog
    def form_valid(self, form):
        user = self.request.user
        try:
            with transaction.atomic():
                connector_type = form.cleaned_data['connector_type']
                port_type = form.cleaned_data['port_type']
                serial_number = form.cleaned_data['serial_number']
                last_ticket = form.cleaned_data['last_ticket']

                PhysicalInterface.objects.create(
                    connector_type=connector_type,
                    last_ticket=last_ticket,
                    modified_by=user,
                    port_type=port_type,
                    serial_number=serial_number,
                )
                messages.success(self.request, "Port saved")
                return redirect(self.request.META.get('PATH_INFO'))
        except ValidationError as e:
            messages.error(self.request, str(e.messages[0]))
            return redirect(self.request.META.get('PATH_INFO'))


class AddPortChannelFormView(LoginRequiredMixin, LogsMixin, FormView):

    """This class has, as main objective, redenrize and submit the form to
       edit a port channel

    Attributes:
        context (dic): Dictionary with all information to be printed on the
            screen
        form_class (Instance of forms.EditPortPhysicalInterfaceForm):
            EditPortPhysicalInterfaceForm
        http_method_names (list): List containing the request types
        initial (dict): Boot Dictionary, if you need to start a field with a
            value
        template_name (str): Name of the template used for this form
        pix_object (<class 'django.db.models.query.QuerySet'>): Get a PIX by
            the primary key passed by paramete
        switch (<class 'django.db.models.query.QuerySet'>): Get all the
            Switches by the pix passed by paramete
        ports (<class 'django.db.models.query.QuerySet'>): Get all the ports
            free of all the switches of a pix
        customer_channel (<class 'django.db.models.query.QuerySet'>): Get a
            CustomerChannel by the primary key passed by paramete
    Returns:
        If the port has been successfully added to the customer channel, it
            will return a successful message,
        otherwise it will return an message with error.
    """

    template_name = 'forms/add_port_channel.html'
    form_class = AddPortChannel
    initial = {}
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, pix, channel):

        pix_object = PIX.objects.get(pk=pix)
        channel_object = CustomerChannel.objects.get(pk=channel)
        switch = channel_object.channel_port.port_set.first().switch
        ports = Port.objects.filter(switch=switch).filter(status='AVAILABLE')\
            .order_by_port_name()

        form = self.form_class()
        form.fields['ports'].queryset = ports

        self.context = {
            'pix': pix,
            'channel': channel,
            'form': form
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            with transaction.atomic():
                ports = form.cleaned_data['ports']

                customer_channel = CustomerChannel.objects.get(
                    pk=self.kwargs['channel'])

                for port in ports:
                    customer_channel.channel_port.port_set.add(port)
                    port.status = 'CUSTOMER'
                    port.save()
                customer_channel.is_lag = True
                customer_channel.save()

                messages.success(self.request, "Ports saved")
                return redirect(self.request.META.get('PATH_INFO'))
        except ValidationError as e:
            messages.error(self.request, str(e.messages[0]))
            return redirect(self.request.META.get('PATH_INFO'))


class AddIXtoASNFormView(LoginRequiredMixin, LogsMixin, FormView):
    """
    This class has, as main objective, redenrize and
    submit the form to edit a port channel

    Attributes:
        context (dic): Dictionary with all information to
            be printed on the screen
        form_class (Instance of forms.EditPortPhysicalInterfaceForm):
            EditPortPhysicalInterfaceForm
        http_method_names (list): List containing the request types
        initial (dict): Boot Dictionary, if you need to start a
            field with a value
        template_name (str): Name of the template used for this form
        ixs_by_asn (<class 'django.db.models.query.QuerySet'>): Get all the
            ContactsMap by the asn passed by paramete
        ixs (<class 'django.db.models.query.QuerySet'>): Get all IXs that the
            ASN does not have
    Returns:
        If IX was successfully added to the ASN, it will return a successful
            message, otherwise it will return a message with the error.
    """

    template_name = 'forms/add_ix_to_asn.html'
    form_class = AddIXtoASNForm
    initial = {}
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, asn):
        form = self.form_class()
        ixs_by_asn = ContactsMap.objects.filter(asn=asn)
        ixs = IX.objects.exclude(
            pk__in=ixs_by_asn.values_list('ix', flat=True))

        form.fields['ix'].queryset = ixs

        self.context = {
            'asn': asn,
            'form': form
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            with transaction.atomic():
                contactsmap = ContactsMap.objects.filter(
                    asn=self.kwargs['asn'])
                ix = form.cleaned_data['ix']
                ticket = form.cleaned_data['ticket']
                contactsmap_first = contactsmap.first()
                new_contactsmap = ContactsMap.objects.create(
                    last_ticket=ticket,
                    organization=contactsmap_first.organization,
                    ix=ix,
                    asn=contactsmap_first.asn,
                    noc_contact=contactsmap_first.noc_contact,
                    adm_contact=contactsmap_first.adm_contact,
                    peer_contact=contactsmap_first.peer_contact,
                    com_contact=contactsmap_first.com_contact,
                    org_contact=contactsmap_first.org_contact,
                    peering_url=contactsmap_first.peering_url,
                    peering_policy=contactsmap_first.peering_policy)
                new_contactsmap.save()
                messages.success(self.request, "IX saved")
                return redirect(self.request.META.get('PATH_INFO'))

        except ValidationError as e:
            messages.error(self.request, str(e.messages[0]))
            return redirect(self.request.META.get('PATH_INFO'))


class GenericMLPANewChannelFormView(AjaxableResponseMixin,
                                    LoginRequiredMixin,
                                    LogsMixin,
                                    FormView):
    template_name = 'forms/generic_mlpa_new_channel.html'
    form_class = GenericMLPANewChannelForm
    initial = {}
    tags_pk = {}
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def get(self, request, asn, code):
        ix = IX.objects.get(pk=code)
        form = self.form_class()
        form.fields['pix'].queryset = PIX.objects.filter(ix=ix)
        form.fields['switch'].queryset = Switch.objects.none()
        form.fields['customer_channel'].queryset = \
            CustomerChannel.objects.none()
        form.fields['asn'].widget.attrs['value'] = asn
        form.fields['code'].widget.attrs['value'] = code
        self.context = {
            'form': form,
            'code': code,
            'asn': asn,
        }

        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        context = {}
        try:
            with transaction.atomic():
                message = ''

                last_ticket = form.cleaned_data['last_ticket']
                asn = form.cleaned_data['asn']
                code = form.cleaned_data['code']
                service_option = form.cleaned_data['service_option']
                tag4 = form.cleaned_data['tag_v4']
                mlpav4_address = form.cleaned_data['mlpav4_address']
                tag6 = form.cleaned_data['tag_v6']
                mlpav6_address = form.cleaned_data['mlpav6_address']

                if 'channel' in form.cleaned_data:
                    customer_channel = CustomerChannel.objects.get(
                        pk=form.cleaned_data['channel'])
                else:
                    customer_channel = form.cleaned_data['customer_channel']

                asn = ASN.objects.get(pk=asn)
                ix = IX.objects.get(pk=code)

                if customer_channel.cix_type == 3:
                    inner_v4 = form.cleaned_data['inner_v4'] \
                        if form.cleaned_data['inner_v4'] else None
                    inner_v6 = form.cleaned_data['inner_v6'] \
                        if form.cleaned_data['inner_v6'] else None
                else:
                    inner_v4 = None
                    inner_v6 = None

                if service_option == "only_v6":
                    tag = GenericMLPANewChannelFormView.get_instance_tag(
                        code, tag6, customer_channel)
                    ipv6 = GenericMLPANewChannelFormView.get_instance_ipv6(
                        mlpav6_address)
                    if ipv6 is None:
                        message = GenericMLPANewChannelFormView.\
                            message_ip_not_found('IPv6')
                    else:
                        message = GenericMLPANewChannelFormView.save_mlpav6(
                            ipv6, customer_channel, asn, last_ticket, tag,
                            inner_v6, ix)

                elif service_option == "only_v4":
                    ipv4 = GenericMLPANewChannelFormView.get_instance_ipv4(
                        mlpav4_address)
                    tag = GenericMLPANewChannelFormView.get_instance_tag(
                        code, tag4, customer_channel)
                    if ipv4 is None:
                        message = GenericMLPANewChannelFormView.\
                            message_ip_not_found('IPv4')
                    else:
                        message = GenericMLPANewChannelFormView.save_mlpav4(
                            ipv4, customer_channel, asn, last_ticket,
                            tag, inner_v4, ix)

                elif service_option == "v4_and_v6":
                    if inner_v4 == inner_v6 and customer_channel.cix_type == 3:
                        raise ValidationError("Inner can not be the same")
                    else:
                        tag_v4 = GenericMLPANewChannelFormView.\
                            get_instance_tag(code, tag4, customer_channel)
                        tag_v6 = GenericMLPANewChannelFormView.\
                            get_instance_tag(code, tag6, customer_channel)
                        ipv6 = GenericMLPANewChannelFormView.get_instance_ipv6(
                            mlpav6_address)
                        ipv4 = GenericMLPANewChannelFormView.get_instance_ipv4(
                            mlpav4_address)

                        if ipv4 is None and ipv6 is None:
                            message = GenericMLPANewChannelFormView.\
                                message_ip_not_found('IPs')
                        elif ipv4 is None:
                            message = GenericMLPANewChannelFormView.\
                                message_ip_not_found('IPv4')
                        elif ipv6 is None:
                            message = GenericMLPANewChannelFormView.\
                                message_ip_not_found('IPv6')
                        else:
                            message = GenericMLPANewChannelFormView\
                                .save_mlpav4_mlpav6(
                                    ipv4=ipv4,
                                    ipv6=ipv6,
                                    customer_channel=customer_channel,
                                    asn=asn,
                                    last_ticket=last_ticket,
                                    tag_v4=tag_v4,
                                    tag_v6=tag_v6,
                                    inner_v4=inner_v4,
                                    inner_v6=inner_v6,
                                    ix=ix,)

                context = {'message': message}
                return HttpResponse(render_to_string(
                    'forms/modal_feedback_service.html', context))

        except (ValidationError, ValueError) as e:
            messages.error(self.request, str(e))
            return redirect(self.request.META.get('PATH_INFO'))

    def get_instance_ipv4(mlpav4_address):
        ipv4 = IPv4Address.objects.get_or_none(pk=mlpav4_address)

        return ipv4

    def get_instance_ipv6(mlpav6_address):
        ipv6 = IPv6Address.objects.get_or_none(pk=mlpav6_address)

        return ipv6

    def get_instance_tag(ix, tag, channel):
        free_tags = get_free_tags(channel=channel, ix=ix).filter(tag=tag)
        if len(free_tags) == 0:
            return instantiate_tag(channel=channel, ix=ix, tag_number=tag)
        return free_tags.first()

    def save_mlpav4(mlpav4_address, customer_channel, asn, last_ticket, tag,
                    inner, ix):
        message = ''
        if mlpav4_address.ix.code != ix.code:
            message = GenericMLPANewChannelFormView.message_ip_another_ix(
                mlpav4_address, 'IPv4', ix.ipv4_prefix, ix.code)
        else:
            if tag is None:
                message = GenericMLPANewChannelFormView.error_message_tags(
                    'IPv4')
            else:
                new_service = MLPAv4.objects.create(
                    mlpav4_address=mlpav4_address,
                    customer_channel=customer_channel,
                    asn=asn,
                    last_ticket=last_ticket,
                    tag=tag,
                    shortname='mlpav4',
                    inner=inner,
                    status='QUARANTINE'
                )
                tag.status = "PRODUCTION"
                tag.save()
                new_service.save()
                message = 'success'

        return message

    def save_mlpav6(mlpav6_address, customer_channel, asn, last_ticket, tag,
                    inner, ix):
        message = ''
        if mlpav6_address.ix.code != ix.code:
            message = GenericMLPANewChannelFormView.message_ip_another_ix(
                mlpav6_address, 'IPv6', ix.ipv6_prefix, ix.code)
        else:
            if tag is None:
                message = GenericMLPANewChannelFormView.error_message_tags(
                    'IPv6')
            else:
                new_service = MLPAv6.objects.create(
                    mlpav6_address=mlpav6_address,
                    customer_channel=customer_channel,
                    asn=asn,
                    last_ticket=last_ticket,
                    tag=tag,
                    shortname='mlpav6',
                    inner=inner,
                    status='QUARANTINE'
                )
                tag.status = "PRODUCTION"
                tag.save()
                new_service.save()
                message = 'success'

        return message

    def save_mlpav4_mlpav6(ipv4, ipv6, customer_channel, asn, last_ticket,
                           tag_v4, tag_v6, inner_v4, inner_v6, ix):
        message = ''
        if ipv4.ix.code != ix.code and ipv6.ix.code != ix.code:
            message = GenericMLPANewChannelFormView.message_ips_another_ix(
                ix.code)
        elif ipv4.ix.code != ix.code:
            message = GenericMLPANewChannelFormView.message_ip_another_ix(
                ipv4, 'IPv4', ix.ipv4_prefix, ix.code)
        elif ipv6.ix.code != ix.code:
            message = GenericMLPANewChannelFormView.message_ip_another_ix(
                ipv6, 'IPv6', ix.ipv6_prefix, ix.code)
        else:
            if tag_v4 is None:
                message = GenericMLPANewChannelFormView.error_message_tags(
                    'IPv4')
            elif tag_v6 is None:
                message = GenericMLPANewChannelFormView.error_message_tags(
                    'IPv6')
            else:
                new_service_v4 = MLPAv4.objects.create(
                    mlpav4_address=ipv4,
                    customer_channel=customer_channel,
                    asn=asn,
                    last_ticket=last_ticket,
                    tag=tag_v4,
                    shortname='mlpav4',
                    inner=inner_v4,
                    status='QUARANTINE'
                )
                new_service_v6 = MLPAv6.objects.create(
                    mlpav6_address=ipv6,
                    customer_channel=customer_channel,
                    asn=asn,
                    last_ticket=last_ticket,
                    tag=tag_v6,
                    shortname='mlpav6',
                    inner=inner_v6,
                    status='QUARANTINE'
                )
                tag_v4.status = "PRODUCTION"
                tag_v6.status = "PRODUCTION"
                tag_v4.save()
                tag_v6.save()
                new_service_v4.save()
                new_service_v6.save()
                message = 'success'
        return message

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

    def error_message_tags(type_service):
        message = (
            "Selected tag for {} is already in use.").format(type_service)

        return message


class AddBilateralFormView(AjaxableResponseMixin, LoginRequiredMixin,
                           LogsMixin, FormView):
    """This class has, as main objective, redenrize and submit the form to add
       bilateral service

    Attributes:
        context (dic): Dictionary with all information to be printed on the
            screen
        form_class (Instance of forms.EditPortPhysicalInterfaceForm):
            EditPortPhysicalInterfaceForm
        http_method_names (list): List containing the request types
        initial (dict): Boot Dictionary, if you need to start a field with a
            value
        template_name (str): Name of the template used for this form
    Returns:
        If Bilateral service was successfully added to the ASN, it will return
        a successful message,
        otherwise it will return a message with the error.
    """

    template_name = 'forms/add_bilateral_form.html'
    form_class = AddBilateralForm
    initial = {}
    http_method_names = ['get', 'post']

    def get(self, request, asn, channel):
        form = self.form_class()

        customer_channel_object = CustomerChannel.objects.get(
            pk=channel)
        pix_object = PIX.objects.get(switch=Switch.objects.get(
            port=customer_channel_object.channel_port.port_set.first()))

        form.fields['pix'].queryset = PIX.objects.filter(ix=pix_object.ix)
        form.fields['switch'].queryset = Switch.objects.none()
        form.fields['origin_channel'].widget.attrs['value'] = channel
        form.fields['ix'].widget.attrs['value'] = pix_object.ix.code
        form.fields['customer_channel'].queryset = \
            CustomerChannel.objects.none()
        tag = get_tag_without_all_service(
            ix=pix_object.ix, channel=customer_channel_object).first().tag
        form.fields['tag_a'].widget.attrs['value'] = tag
        form.fields['tag_b'].widget.attrs['value'] = tag

        self.context = {
            'form': form,
            'asn': asn,
            'channel': channel,
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            with transaction.atomic():
                ticket = form.cleaned_data['last_ticket']
                bilateral_type = form.cleaned_data['bilateral_type']

                # Stuff from peer A
                asn_peer_a = self.kwargs['asn']
                channel_a = form.cleaned_data['origin_channel']
                if isinstance(channel_a, str):
                    channel_a_object = CustomerChannel.objects.get(
                        pk=channel_a)
                else:
                    channel_a_object = channel_a
                asn_peer_a_object = ASN.objects.get(pk=asn_peer_a)

                # Stuff from peer B
                asn_peer_b = form.cleaned_data['asn']
                channel_b_object = form.cleaned_data['customer_channel']
                asn_peer_b_object = ASN.objects.filter(pk=asn_peer_b).first()

                tag_a = form.cleaned_data['tag_a']
                inner_a = form.cleaned_data['inner_a']
                tag_b = form.cleaned_data['tag_b']
                inner_b = form.cleaned_data['inner_b']

                ix = channel_b_object.channel_port.port_set.first()\
                    .switch.pix.ix

                bilateral_case = define_bilateral_case(
                    channel_a=channel_a_object,
                    channel_b=channel_b_object)

                bilateral = create_bilateral[bilateral_case](
                    peer_a=asn_peer_a_object,
                    peer_b=asn_peer_b_object,
                    channel_a=channel_a_object,
                    channel_b=channel_b_object,
                    ix=ix,
                    tag_a=tag_a,
                    tag_b=tag_b,
                    inner_b=inner_b,
                    inner_a=inner_a,
                    ticket=ticket,
                    b_type=bilateral_type)

                if bilateral:
                    messages.success(self.request, "Bilateral created")
                else:
                    messages.error(self.request, "Something is not right")
                return redirect(self.request.META.get('PATH_INFO'))
        except (ValidationError, ValueError, TypeError) as e:
            messages.error(self.request, str(e))
            return redirect(self.request.META.get('PATH_INFO'))


class AddBilateralNewChannelFormView(
        AjaxableResponseMixin, LoginRequiredMixin, LogsMixin, FormView):
    """This class has, as main objective, redenrize and submit the form to add
       bilateral service on an arbitrary channel in a given IX

    Attributes:
        context (dic): Dictionary with all information to be printed on the
            screen
        form_class (Instance of forms.EditPortPhysicalInterfaceForm):
            EditPortPhysicalInterfaceForm
        http_method_names (list): List containing the request types
        initial (dict): Boot Dictionary, if you need to start a field with a
            value
        template_name (str): Name of the template used for this form
    Returns:
        If Bilateral service was successfully added to the ASN, it will return
        a successful message,
        otherwise it will return a message with the error.
    """

    template_name = 'forms/add_bilateral_new_channel_form.html'
    form_class = AddBilateralNewChannelForm
    initial = {}
    http_method_names = ['get', 'post']

    def get(self, request, asn, code):
        form = self.form_class()
        ix = IX.objects.get(code=code)
        form.fields['origin_pix'].queryset = PIX.objects.filter(ix=ix)
        form.fields['pix'].queryset = PIX.objects.filter(ix=ix)
        form.fields['origin_switch'].queryset = Switch.objects.none()
        form.fields['switch'].queryset = Switch.objects.none()
        form.fields['origin_channel'].queryset = \
            CustomerChannel.objects.none()
        form.fields['ix'].widget.attrs['value'] = code
        form.fields['origin_asn'].widget.attrs['value'] = asn
        form.fields['customer_channel'].queryset = \
            CustomerChannel.objects.none()
        form.fields['tag_a'].widget.attrs['value'] = ''
        form.fields['tag_b'].widget.attrs['value'] = ''

        self.context = {
            'form': form,
            'asn': asn,
            'code': code,
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        return AddBilateralFormView.form_valid(self, form)


class EditDioPortFormView(LoginRequiredMixin, FormView):
    """This class has, as main objective, redenrize and submit the form to edit
        a DIO Port.

    Attributes:
        form_class (Instance of forms.EditDioPortForm):
            EditDioPortForm
        http_method_names (list): List containing the request types
        initial (dict): Boot Dictionary, if you need to start a field with a
        value template_name (str): Name of the template used for this form
    Returns:
        If association was successfully concluded, it will return a successful
        message, otherwise it will return a message with the error.
    """

    template_name = 'forms/edit_dio_port_form.html'
    form_class = EditDioPortForm
    initial = {}
    http_method_names = ['get', 'post']

    def get(self, request, pix, dio_port):
        dio_port_object = get_object_or_404(DIOPort, pk=dio_port)
        pix_object = get_object_or_404(PIX, pk=pix)
        switch_set = pix_object.switch_set.all()

        port_dict = dict()
        switch_dict = list()

        for switch in switch_set:
            switch_dict += (
                (switch.pk, switch.management_ip),
            )

        if dio_port_object.switch_port is None:
            switch_initial = switch_set.first()
        else:
            switch_initial = dio_port_object.switch_port.switch

        form = self.form_class()

        form.fields['switch'].choices = switch_dict
        form = self.form_class()
        form.fields['switch'].choices = switch_dict

        port_set = Port.objects.filter(
            switch=switch_initial)

        for port in port_set:
            if len(port.getDioPorts()) == 0:
                port_dict[str(port.name)] = str(port.uuid)

        ordered_ports = port_utils.port_sorting(port_dict)

        port_choices = ()
        for key in ordered_ports:
            port_choices += (
                (ordered_ports[key], key),
            )
        form.fields['ports'].choices = port_choices
        form.fields['switch'].initial = switch_initial
        form.fields['ports'].initial = dio_port_object.switch_port
        form.fields['ix_position'].initial = dio_port_object.ix_position
        form.fields['dc_position'].initial = dio_port_object. \
            datacenter_position

        self.context = {
            'form': form,
            'dio_port': dio_port,
            'pix': pix,
        }

        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            with transaction.atomic():
                dio_port_object = DIOPort.objects.get(
                    pk=self.kwargs['dio_port'])

                ix_position = form.cleaned_data['ix_position']
                dc_position = form.cleaned_data['dc_position']
                port = form.cleaned_data['ports']
                last_ticket = form.cleaned_data['last_ticket']

                if(dio_port_object.dio.validate_unique_ix_position(
                        dio_port_object, ix_position) is False):
                    raise ValueError("IX Position already exists")

                if(dio_port_object.dio.validate_unique_dc_position(
                        dio_port_object, dc_position) is False):
                    raise ValueError("Data center Position already exists")

                dio_port_object.last_ticket = last_ticket
                dio_port_object.ix_position = ix_position
                dio_port_object.datacenter_position = dc_position
                dio_port_object.switch_port = port
                dio_port_object.save()
                messages.success(self.request, "DIO Port saved")
                return redirect(self.request.META.get('PATH_INFO'))
        except (ValidationError, ValueError, TypeError) as e:
            messages.error(self.request, str(e))
            return redirect(self.request.META.get('PATH_INFO'))


class EditConfiguredCapacityPortFormView(LoginRequiredMixin,
                                         LogsMixin,
                                         FormView):
    """This class has, as main objective, redenrize and submit the form to
       edit configured capacity from a given port

    Attributes:
        context (dict): Dictionary with all information to be printed on the
            screen
        form_class (Instance of forms.EditConfiguredCapacityPort):
            EditConfiguredCapacityPort
        http_method_names (list): List containing the request types
        initial (dict): Boot Dictionary, if you need to start a field with a
            value
        template_name (str): Name of the template used for this form
    Returns:
        If edition of configured port was successfull, it will return a
        successful message, otherwise it will return a message with the error.
    """

    template_name = 'forms/edit_port_configured_capacity_form.html'
    form_class = EditConfiguredCapacityPort
    initial = {}
    http_method_names = ['get', 'post']

    def get(self, request, port):
        form = self.form_class()
        port_object = Port.objects.get(pk=port)
        form.fields['configured_capacity'].choices = \
            filter(lambda capacity: capacity[0] <= port_object.capacity,
                   CAPACITIES_CONF)
        form.fields['configured_capacity'].initial = \
            port_object.configured_capacity
        self.context = {
            'form': form,
            'port': port
        }
        return render(request, self.template_name, self.context)

    @updatelastticket
    @ixapilog
    def form_valid(self, form):
        try:
            with transaction.atomic():
                ticket = form.cleaned_data['last_ticket']
                configured_capacity = form.cleaned_data['configured_capacity']
                port = Port.objects.get(pk=self.kwargs['port'])
                port.configured_capacity = configured_capacity
                port.last_ticket = ticket
                port.save()

                messages.success(self.request, "Configured Capacity edited "
                                               "with success")
                return redirect(self.request.META.get('PATH_INFO'))
        except ValidationError as e:
            messages.error(self.request, str(e))
            return redirect(self.request.META.get('PATH_INFO'))

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return redirect(self.request.META.get('PATH_INFO'))


class EditDescriptionByPortFormView(LoginRequiredMixin, LogsMixin, FormView):
    template_name = 'forms/edit_description_form.html'
    form_class = EditDescriptionForm
    initial = {}
    http_method_names = ['get', 'post']

    def get(self, request, port):
        port_object = Port.objects.get(pk=port)

        form = self.form_class()
        form.fields['description'].initial = port_object.description

        self.context = {
            'form': form,
            'port': port
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            with transaction.atomic():
                description = form.cleaned_data['description']

                port_object = Port.objects.get(pk=self.kwargs['port'])
                port_object.description = description

                port_object.save()

                messages.success(
                    self.request, "Description edited with success")
                return redirect(self.request.META.get('PATH_INFO'))
        except (ValidationError, ValueError, TypeError) as e:
            messages.error(self.request, str(e))
            return redirect(self.request.META.get('PATH_INFO'))

    def form_invalid(self, form):
        messages.error(self.request, "This form is invalid")
        return redirect(self.request.META.get('PATH_INFO'))


class EditTagDescriptionFormView(LoginRequiredMixin, LogsMixin, FormView):
    template_name = 'forms/edit_description_form.html'
    form_class = EditDescriptionForm
    initial = {}
    http_method_names = ['get', 'post']

    def get(self, request, tag):
        tag_object = Tag.objects.get(pk=tag)

        form = self.form_class()
        form.fields['description'].initial = tag_object.description

        self.context = {
            'form': form,
            'tag': tag
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            with transaction.atomic():
                description = form.cleaned_data['description']

                tag = Tag.objects.get(pk=self.kwargs['tag'])
                tag.description = description

                tag.save()

                messages.success(
                    self.request, "Description edited with success")
                return redirect(self.request.META.get('PATH_INFO'))
        except (ValidationError, ValueError, TypeError) as e:
            messages.error(self.request, str(e))
            return redirect(self.request.META.get('PATH_INFO'))

    def form_invalid(self, form):
        messages.error(self.request, "This form is invalid")
        return redirect(self.request.META.get('PATH_INFO'))


class EditIPDescriptionFormView(LoginRequiredMixin, LogsMixin, FormView):
    template_name = 'forms/edit_description_form.html'
    form_class = EditDescriptionForm
    initial = {}
    http_method_names = ['get', 'post']

    def get(self, request, ipv4, ipv6):
        ip_object = IPv4Address.objects.get(pk=ipv4)

        form = self.form_class()
        form.fields['description'].initial = ip_object.description

        self.context = {
            'form': form,
            'ipv4': ipv4,
            'ipv6': ipv6
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            with transaction.atomic():
                description = form.cleaned_data['description']

                ipv4 = IPv4Address.objects.get(pk=self.kwargs['ipv4'])
                ipv4.description = description
                ipv4.save()

                ipv6 = IPv6Address.objects.get(pk=self.kwargs['ipv6'])
                ipv6.description = description
                ipv6.save()

                messages.success(
                    self.request, "Description edited with success")
                return redirect(self.request.META.get('PATH_INFO'))
        except (ValidationError, ValueError, TypeError) as e:
            messages.error(self.request, str(e))
            return redirect(self.request.META.get('PATH_INFO'))

    def form_invalid(self, form):
        messages.error(self.request, "This form is invalid")
        return redirect(self.request.META.get('PATH_INFO'))


class MigrateSwitchFormView(LoginRequiredMixin, LogsMixin, FormView):
    """This class has, as main objective, redenrize and submit the form to
       migrate the switch ports to the new switch.

    Attributes:
        context (dict): Dictionary with all information to be printed on the
            screen
        form_class (Instance of forms.MigrateSwitchForm):MigrateSwitchForm
        http_method_names (list): List containing the request types
        initial (dict): Boot Dictionary, if you need to start a field with a
            value
        template_name (str): Name of the template used for this form
    Returns:
        If migration of switch was successfull, it will return a
        successful message, otherwise it will return a message with the error.
    """

    template_name = 'forms/migrate_switch_form.html'
    form_class = MigrateSwitchForm
    initial = {}
    http_method_names = ['get', 'post']

    def get(self, request, pix):
        pix_object = PIX.objects.get(uuid=pix)
        form = self.form_class()
        form.fields['switch'].queryset = Switch.objects.filter(pix=pix)
        self.context = {
            'form': form,
            'pix': pix_object}
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            pix = PIX.objects.get(uuid=self.kwargs['pix'])
            ticket = form.cleaned_data['last_ticket']
            switch = form.cleaned_data['switch']
            new_model = form.cleaned_data['new_model']
            description = form.cleaned_data['description']

            with transaction.atomic():
                new_switch = Switch.objects.create(
                    pix=pix,
                    description=description,
                    model=new_model,
                    last_ticket=ticket)
                migrate_switch(switch, new_switch)

                messages.success(
                    self.request, "Switch migrated successfully")
                return redirect(self.request.META.get('PATH_INFO'))
        except (ValidationError, ValueError) as e:
            messages.error(self.request, str(e))
            return redirect(self.request.META.get('PATH_INFO'))


class ReserveIPResourceFormView(LoginRequiredMixin, LogsMixin, FormView):
    """

    """
    template_name = 'forms/reserve_ip_resource.html'
    form_class = ReserveIPResourceForm
    initial = {}
    http_method_names = ['get', 'post']
    # ipv4_free = IPv4Address.objects.filter(Q(reserved=False) & Q(ix__code=ix)

    def get(self, request, ix):
        form = self.form_class()
        ipv4_free = IPv4Address.objects.filter(Q(reserved=False) &
                                               Q(ix__code=ix))
        ipv6_free = IPv6Address.objects.filter(Q(reserved=False) &
                                               Q(ix__code=ix))
        form.fields['IPv4'].queryset = ipv4_free
        form.fields['IPv6'].queryset = ipv6_free

        self.context = {
            'form': form,
            'ix': ix,
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        user = self.request.user
        try:
            with transaction.atomic():
                ipv4_list = form.cleaned_data['IPv4']
                ipv6_list = form.cleaned_data['IPv6']
                if ipv4_list:
                    for ipv4 in ipv4_list:
                        ipv4.reserve_this()
                if ipv6_list:
                    for ipv6 in ipv6_list:
                        ipv6.reserve_this()

                messages.success(self.request, "IP(s) Reserved")
                return redirect(self.request.META.get('HTTP_REFERER'))

        except ValidationError as e:
            messages.error(self.request, str(e.messages[0]))
            return redirect(self.request.META.get('PATH_INFO'))


class ReleaseIPResourceFormView(LoginRequiredMixin, LogsMixin, FormView):
    """

    """
    template_name = 'forms/release_ip_resource.html'
    form_class = ReleaseIPResourceForm
    initial = {}
    http_method_names = ['get', 'post']

    def get(self, request, ix):
        form = self.form_class()
        ipv4_free = IPv4Address.objects.filter(Q(reserved=True) &
                                               Q(ix__code=ix))
        ipv6_free = IPv6Address.objects.filter(Q(reserved=True) &
                                               Q(ix__code=ix))
        form.fields['IPv4'].queryset = ipv4_free
        form.fields['IPv6'].queryset = ipv6_free

        self.context = {
            'form': form,
            'ix': ix,
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        user = self.request.user
        try:
            with transaction.atomic():
                ipv4_list = form.cleaned_data['IPv4']
                ipv6_list = form.cleaned_data['IPv6']

                if ipv4_list:
                    for ipv4 in ipv4_list:
                        ipv4.free_this()
                if ipv6_list:
                    for ipv6 in ipv6_list:
                        ipv6.free_this()

                messages.success(self.request, "IP(s) Released")
                return redirect(self.request.META.get('HTTP_REFERER'))

        except ValidationError as e:
            messages.error(self.request, str(e.messages[0]))
            return redirect(self.request.META.get('PATH_INFO'))


class ReservePortResourceFormView(LoginRequiredMixin, LogsMixin, FormView):
    """

    """
    template_name = 'forms/reserve_port_resource.html'
    form_class = ReservePortResourceForm
    initial = {}
    http_method_names = ['get', 'post']

    def get(self, request, sw):
        form = self.form_class()
        ports_to_reserve = Port.objects.filter(
            Q(switch_id=sw) & Q(reserved=False)).order_by_port_name()
        form.fields['ports_to_reserve'].queryset = ports_to_reserve

        self.context = {
            'form': form,
            'sw': sw,
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        user = self.request.user
        try:
            with transaction.atomic():
                ports = self.request.POST.getlist('ports_to_reserve')
                for port in ports:
                    get_object_or_404(Port, pk=port).reserve_this()

                messages.success(self.request, "Port(s) Reserved")
                return redirect(self.request.META.get('PATH_INFO'))

        except ValidationError as e:
            messages.error(self.request, str(e.messages[0]))
            return redirect(self.request.META.get('PATH_INFO'))

        except ValueError as e:
            messages.error(self.request, str(e))
            return redirect(self.request.META.get('PATH_INFO'))


class ReleasePortResourceFormView(LoginRequiredMixin, LogsMixin, FormView):
    """

    """
    template_name = 'forms/release_port_resource.html'
    form_class = ReleasePortResourceForm
    initial = {}
    http_method_names = ['get', 'post']

    def get(self, request, sw):
        form = self.form_class()
        ports_to_release = Port.objects.filter(
            Q(switch_id=sw) & Q(reserved=True)).order_by_port_name()
        form.fields['ports_to_release'].queryset = ports_to_release

        self.context = {
            'form': form,
            'sw': sw,
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        user = self.request.user
        try:
            with transaction.atomic():
                ports = self.request.POST.getlist('ports_to_release')

                for port in ports:
                    get_object_or_404(Port, pk=port).free_this()

                messages.success(self.request, "Port(s) Released")
                return redirect(self.request.META.get('PATH_INFO'))

        except ValidationError as e:
            messages.error(self.request, str(e.messages[0]))
            return redirect(self.request.META.get('PATH_INFO'))

        except ValueError as e:
            messages.error(self.request, str(e))
            return redirect(self.request.META.get('PATH_INFO'))


class AllocateTagStatusFormView(LoginRequiredMixin, LogsMixin, FormView):
    template_name = 'forms/allocate_tag_status.html'
    form_class = AllocateTagStatusForm
    initial = {}
    http_method_names = ['get', 'post']

    def get(self, request, **kwargs):
        form = self.form_class()

        self.context = {
            'ix': kwargs['ix'],
        }
        if request.META['QUERY_STRING']:
            bundle_pk = request.GET.get('bundle_pk')
            tag_to_allocate = DownlinkChannel.objects.get(
                pk=bundle_pk).channel_port.tag_set.filter(status='AVAILABLE')
            self.context['bundle_pk'] = bundle_pk
        else:
            tag_to_allocate = Tag.objects.filter(
                ix_id=kwargs['ix'],
                status='AVAILABLE'
            )

        form.fields['tag_to_allocate'].queryset = tag_to_allocate
        self.context['form'] = form

        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            with transaction.atomic():
                tags = form.cleaned_data['tag_to_allocate']
                if tags:
                    for tag in tags:
                        tag.status = 'ALLOCATED'
                        tag.save()

                ix = self.kwargs['ix']
                if self.request.META['QUERY_STRING']:
                    bundle = self.request.GET.get('bundle_pk')
                    url = reverse(
                        'core:tag_list_with_bundle', args=[ix, bundle])
                else:
                    url = reverse('core:tag_list_without_bundle', args=[ix])

                messages.success(self.request, "Tag Allocated")
                return redirect(url)

        except ValidationError as e:
            messages.error(self.request, str(e.messages[0]))
            return redirect(self.request.META.get('PATH_INFO'))

        except ValueError as e:
            messages.error(self.request, str(e))
            return redirect(self.request.META.get('PATH_INFO'))


class DeallocateTagStatusFormView(LoginRequiredMixin, LogsMixin, FormView):
    template_name = 'forms/deallocate_tag_status.html'
    form_class = DeallocateTagStatusForm
    initial = {}
    http_method_names = ['get', 'post']

    def get(self, request, **kwargs):

        form = self.form_class()
        self.context = {
            'ix': kwargs['ix'],
        }
        if request.META['QUERY_STRING']:
            bundle_pk = request.GET.get('bundle_pk')
            tag_to_deallocate = DownlinkChannel.objects.get(
                pk=bundle_pk).channel_port.tag_set.filter(status='ALLOCATED')
            self.context['bundle_pk'] = bundle_pk
        else:
            tag_to_deallocate = Tag.objects.filter(
                ix_id=kwargs['ix'],
                status='ALLOCATED'
            )

        form.fields['tag_to_deallocate'].queryset = tag_to_deallocate
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            with transaction.atomic():
                tags = form.cleaned_data['tag_to_deallocate']

                if tags:
                    for tag in tags:
                        tag.status = 'AVAILABLE'
                        tag.save()

                ix = self.kwargs['ix']
                if self.request.META['QUERY_STRING']:
                    bundle = self.request.GET.get('bundle_pk')
                    url = reverse(
                        'core:tag_list_with_bundle', args=[ix, bundle])
                else:
                    url = reverse('core:tag_list_without_bundle', args=[ix])

                messages.success(self.request, "Tag Deallocated")
                return redirect(url)

        except ValidationError as e:
            messages.error(self.request, str(e.messages[0]))
            return redirect(self.request.META.get('PATH_INFO'))

        except ValueError as e:
            messages.error(self.request, str(e))
            return redirect(self.request.META.get('PATH_INFO'))


class ReserveTagResourceFormView(LoginRequiredMixin, LogsMixin, FormView):
    template_name = 'forms/reserve_tag_resource.html'
    form_class = ReserveTagResourceForm
    initial = {}
    http_method_names = ['get', 'post']

    def get(self, request, **kwargs):
        form = self.form_class()

        self.context = {
            'ix': kwargs['ix'],
        }
        try:
            if (not request.META['QUERY_STRING'] or request.GET.get(
                    'bundle_pk') is None):
                raise Exception
            bundle_pk = request.GET.get('bundle_pk')
            tag_to_reserve = DownlinkChannel.objects.get(
                pk=bundle_pk).channel_port.tag_set.filter(reserved=False)
            self.context['bundle_pk'] = bundle_pk
        except Exception:
            tag_to_reserve = Tag.objects.filter(Q(ix_id=kwargs['ix']) &
                                                Q(reserved=False))

        form.fields['tag_to_reserve'].queryset = tag_to_reserve
        self.context['form'] = form

        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            with transaction.atomic():
                tags = form.cleaned_data['tag_to_reserve']

                if tags:
                    for tag in tags:
                        tag.reserve_this()

                ix = self.kwargs['ix']
                try:
                    if (not self.request.META['QUERY_STRING'] or not
                            self.request.GET.get('bundle_pk')):
                        raise Exception
                    bundle = self.request.GET.get('bundle_pk')
                    url = reverse(
                        'core:tag_list_with_bundle', args=[ix, bundle])
                except Exception:
                    url = reverse('core:tag_list_without_bundle', args=[ix])

                messages.success(self.request, "Tag Reserved")
                return redirect(url)

        except ValidationError as e:
            messages.error(self.request, str(e.messages[0]))
            return redirect(self.request.META.get('PATH_INFO'))


class ReleaseTagResourceFormView(LoginRequiredMixin, LogsMixin, FormView):
    template_name = 'forms/release_tag_resource.html'
    form_class = ReleaseTagResourceForm
    initial = {}
    http_method_names = ['get', 'post']

    def get(self, request, **kwargs):
        form = self.form_class()

        self.context = {
            'ix': kwargs['ix'],
        }
        try:
            if not request.META['QUERY_STRING'] or not request.GET.get(
                    'bundle_pk'):
                raise Exception
            bundle_pk = request.GET.get('bundle_pk')
            tag_to_release = DownlinkChannel.objects.get(
                pk=bundle_pk).channel_port.tag_set.filter(reserved=True)
            self.context['bundle_pk'] = bundle_pk
        except Exception:
            tag_to_release = Tag.objects.filter(Q(ix_id=kwargs['ix']) &
                                                Q(reserved=True))

        form.fields['tag_to_release'].queryset = tag_to_release
        self.context['form'] = form

        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            with transaction.atomic():
                tags = form.cleaned_data['tag_to_release']

                if tags:
                    for tag in tags:
                        tag.free_this()

                ix = self.kwargs['ix']
                try:
                    if (not self.request.META['QUERY_STRING'] or not
                            self.request.GET.get('bundle_pk')):
                        raise Exception
                    bundle = self.request.GET.get('bundle_pk')
                    url = reverse(
                        'core:tag_list_with_bundle', args=[ix, bundle])
                except Exception:
                    url = reverse('core:tag_list_without_bundle', args=[ix])

                messages.success(self.request, "Tag Released")
                return redirect(url)

        except ValidationError as e:
            messages.error(self.request, str(e.messages[0]))
            return redirect(self.request.META.get('PATH_INFO'))


class CreateSwitchFormView(LoginRequiredMixin, LogsMixin, FormView):

    template_name = 'forms/create_switch_form.html'
    form_class = CreateSwitchForm
    initial = {}
    http_method_names = ['get', 'post']

    def get(self, request, pix):

        pix_object = PIX.objects.get(uuid=pix)
        form = self.form_class()
        form.fields['model'].queryset = SwitchModel.objects.all()
        self.context = {
            'pix': pix_object,
            'form': form
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            pix = PIX.objects.get(uuid=self.kwargs['pix'])
            ticket = form.cleaned_data['last_ticket']
            mgmt_ip = form.cleaned_data['mgmt_ip']
            model = form.cleaned_data['model']
            is_pe = form.cleaned_data['is_pe']
            translation = form.cleaned_data['translation']
            create_ports = form.cleaned_data['create_ports']

            with transaction.atomic():
                Switch.objects.create(
                    pix=pix,
                    model=model,
                    management_ip=mgmt_ip,
                    create_ports=create_ports,
                    is_pe=is_pe,
                    translation=translation,
                    last_ticket=ticket
                )
                messages.success(self.request, "Switch created successfully")
                return redirect(self.request.META.get('PATH_INFO'))
        except ValidationError as e:
            messages.warning(self.request, e.messages[0])
            return redirect(self.request.META.get('PATH_INFO'))
        except ValueError as e:
            messages.error(self.request, str(e))
            return redirect(self.request.META.get('PATH_INFO'))


class AddNewSwitchModuleFormView(LoginRequiredMixin, FormView):
    template_name = 'forms/add_switch_module_form.html'
    form_class = AddSwitchModuleForm
    initial = {}
    http_method_names = ['get', 'post']

    def get(self, request, switch):

        form = self.form_class()
        self.context = {
            'form': form,
            'switch': switch,
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        user = self.request.user
        try:
            with transaction.atomic():
                switch = Switch.objects.get(pk=self.kwargs['switch'])
                ticket = form.cleaned_data['last_ticket']
                capacity = form.cleaned_data['capacity']
                connector = form.cleaned_data['connector_type']
                name = form.cleaned_data['name_format']
                begin = form.cleaned_data['begin']
                end = form.cleaned_data['end']
                model = form.cleaned_data['model']
                vendor = form.cleaned_data['vendor']

                create_switch_module_with_ports_use_case(
                    ticket=ticket,
                    switch=switch,
                    vendor=vendor,
                    model=model,
                    name=name,
                    capacity=capacity,
                    connector=connector,
                    name_format=name,
                    begin=begin,
                    end=end)

                messages.success(self.request, "Module associated")
                return redirect(self.request.META.get('PATH_INFO'))


        except ValidationError as e:
            messages.error(self.request, str(e.messages[0]))
            return redirect(self.request.META.get('PATH_INFO'))


class CreatePixFormView(LoginRequiredMixin, LogsMixin, FormView):

    template_name = 'forms/create_pix_form.html'
    form_class = CreatePixForm
    initial = {}
    http_method_names = ['get', 'post']

    def get(self, request, ix):
        ix_object = IX.objects.get(pk=ix)
        form = self.form_class()
        self.context = {
            'ix': ix_object,
            'form': form
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            ix = IX.objects.get(pk=self.kwargs['ix'])
            ticket = form.cleaned_data['last_ticket']
            desc = form.cleaned_data['description']
            code = form.cleaned_data['code']

            with transaction.atomic():
                PIX.objects.create(
                    description=desc,
                    ix=ix,
                    last_ticket=ticket,
                    code=code
                )
                messages.success(self.request, "PIX created successfully")
                return redirect(self.request.META.get('PATH_INFO'))

        except ValidationError as e:
            messages.warning(self.request, e.messages[0])
            return redirect(self.request.META.get('PATH_INFO'))
        except ValueError as e:
            messages.error(self.request, str(e))
            return redirect(self.request.META.get('PATH_INFO'))


class CreateSwitchModelFormView(LoginRequiredMixin, LogsMixin, FormView):

    template_name = 'forms/create_switch_model_form.html'
    form_class = CreateSwitchModelForm
    initial = {}
    http_method_names = ['get', 'post']

    def get(self, request):
        form = self.form_class()
        self.context = {
            'form': form
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            ticket = form.cleaned_data['last_ticket']
            desc = form.cleaned_data['description']
            model = form.cleaned_data['model']
            vendor = form.cleaned_data['vendor']

            # SwitchPortRange

            capacity = form.cleaned_data['capacity']
            connector_type = form.cleaned_data['connector_type']
            name_format = form.cleaned_data['name_format']
            begin = form.cleaned_data['begin']
            end = form.cleaned_data['end']

            # SwitchPortRange extra
            extra_ports = form.cleaned_data['extra_ports']
            if extra_ports:
                capacity_extra = form.cleaned_data['capacity_extra']
                connector_type_extra = form.cleaned_data['connector_type_extra']
                begin_extra = form.cleaned_data['begin_extra']
                end_extra = form.cleaned_data['end_extra']

                if begin_extra <= end:
                    raise ValidationError("Extra ports begin must be greater than end field")
                if capacity_extra == capacity and connector_type == connector_type_extra:
                    raise ValidationError(
                        "Extra ports capacity and connector_type are equal to common ports")

            with transaction.atomic():
                switch_model = SwitchModel.objects.create(
                    model=model,
                    description=desc,
                    vendor=vendor,
                    last_ticket=ticket
                )

                # SwitchPortRange

                SwitchPortRange.objects.create(
                    capacity=capacity,
                    connector_type=connector_type,
                    name_format=name_format,
                    begin=begin,
                    end=end,
                    switch_model=switch_model,
                    last_ticket=ticket)

                # SwitchPortRange extra

                if extra_ports:
                    SwitchPortRange.objects.create(
                        capacity=capacity_extra,
                        connector_type=connector_type_extra,
                        name_format=name_format,
                        begin=begin_extra,
                        end=end_extra,
                        switch_model=switch_model,
                        last_ticket=ticket)

                messages.success(
                    self.request, "Switch Model created successfully")
                return redirect(self.request.META.get('PATH_INFO'))

        except ValidationError as e:
            messages.warning(self.request, e.messages[0])
            return redirect(self.request.META.get('PATH_INFO'))
        except ValueError as e:
            messages.error(self.request, str(e))
            return redirect(self.request.META.get('PATH_INFO'))

    def form_invalid(self, form):
        context = {'form': form}
        messages.error(self.request, form.errors)
        return render(self.request, self.template_name, context)


class CreateIXFormView(LoginRequiredMixin, LogsMixin, FormView):

    template_name = 'forms/create_ix_form.html'
    form_class = CreateIXForm
    initial = {}
    http_method_names = ['get', 'post']

    def get(self, request):
        form = self.form_class()
        self.context = {
            'form': form
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):
        try:
            ticket = form.cleaned_data['last_ticket']
            code = form.cleaned_data['code']
            shortname = form.cleaned_data['shortname']
            fullname = form.cleaned_data['fullname']
            ipv4_prefix = form.cleaned_data['ipv4_prefix']
            ipv6_prefix = form.cleaned_data['ipv6_prefix']
            management_prefix = form.cleaned_data['management_prefix']
            create_ips = form.cleaned_data['create_ips']
            tags_policy = form.cleaned_data['tags_policy']

            create_tags = tags_policy == 'ix_managed'

            with transaction.atomic():
                IX.objects.create(
                    last_ticket=ticket,
                    code=code,
                    shortname=shortname,
                    fullname=fullname,
                    ipv4_prefix=ipv4_prefix,
                    ipv6_prefix=ipv6_prefix,
                    management_prefix=management_prefix,
                    create_ips=create_ips,
                    create_tags=create_tags,
                    tags_policy=tags_policy)
                messages.success(self.request, "IX created successfully")
                return redirect(self.request.META.get('PATH_INFO'))

        except ValidationError as e:
            context = {'form': form}
            messages.error(self.request, str(e.messages[0]))
            return render(self.request, self.template_name, context)
        except ValueError as e:
            context = {'form': form}
            messages.error(self.request, str(e))
            return render(self.request, self.template_name, context)

    def form_invalid(self, form):
        context = {'form': form}
        messages.error(self.request, form.errors)
        return render(self.request, self.template_name, context)


class CreateUplinkCoreChannelModelFormView(
        LoginRequiredMixin, LogsMixin, FormView):

    template_name = 'forms/add_uplink_core_form.html'
    form_class = CreateUplinkCoreChannelModelForm
    initial = {}
    http_method_names = ['get', 'post']

    def get(self, request, ix, switch, port):

        ix_object = IX.objects.get(pk=ix)
        switch_object = Switch.objects.get(pk=switch)
        port_object = Port.objects.get(pk=port)
        form = self.form_class()

        channel_prefix = SWITCH_MODEL_CHANNEL_PREFIX[
            switch_object.model.vendor]
        form.fields['channel_name'].initial = channel_prefix

        ports_set = Port.objects.filter(
            switch__pix__ix=ix,
            status='AVAILABLE').order_by_port_name().exclude(pk=port)

        form.fields['channel_ports'] = forms.ChoiceField(
            choices=[(_port.pk, _port) for _port in ports_set],
            widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
            required=False)

        dest_ports_set = ports_set.exclude(switch=switch_object)

        form.fields['destination_ports'] = forms.ChoiceField(
            choices=[(_port.pk, _port) for _port in dest_ports_set],
            widget=forms.SelectMultiple(
                attrs={'class': 'form-control'})
        )

        self.context = {
            'ix': ix_object,
            'switch': switch_object,
            'port': port_object,
            'form': form
        }
        return render(request, self.template_name, self.context)

    @ixapilog
    def form_valid(self, form):

        try:
            ticket = form.cleaned_data['last_ticket']
            channel_name = form.cleaned_data['channel_name']
            channel_type = form.cleaned_data['channel_type']
            channel_ports = [
                Port.objects.get(pk=port)
                for port in self.request.POST.getlist('channel_ports')]
            destination_ports = [
                Port.objects.get(pk=port)
                for port in self.request.POST.getlist('destination_ports')]
            destination_name = form.cleaned_data['destination_name']
            create_tags = form.cleaned_data['create_tags']

            port = self.kwargs['port']
            port_object = Port.objects.get(pk=port)

            channel_ports.append(port_object)

            with transaction.atomic():
                create_uplink_core_channel_use_case(
                    origin_ports=channel_ports,
                    dest_ports=destination_ports,
                    channel_origin_name=channel_name,
                    channel_dest_name=destination_name,
                    create_tags=create_tags,
                    ticket=ticket,
                    channel_type=channel_type)

            messages.success(self.request, "Channel created successfully")
            return redirect(self.request.META.get('PATH_INFO'))

        except ValidationError as e:
            messages.warning(self.request, e.messages[0])
            return redirect(self.request.META.get('PATH_INFO'))
        except ValueError as e:
            messages.error(self.request, str(e))
            return redirect(self.request.META.get('PATH_INFO'))

    def form_invalid(self, form):

        messages.error(self.request, form.errors)
        return redirect(self.request.META.get('PATH_INFO'))
