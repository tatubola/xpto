from django.conf.urls import url
from django.views.generic import TemplateView

from .utils.regex import Regex
from .views import (as_views, core_views, form_views, function_based_views,
                    ip_views, ix_views, nikiti_views, switch_views, tag_views)

app_name = 'core'
regex = Regex()

as_urls = [
    url(
        regex=r'^as/(?P<asn>' + regex.number + ')/$',
        view=as_views.ASDetailView.as_view(),
        name='as_detail'
    ),
    url(
        regex=r'^as/search/',
        view=as_views.ASSearchView.as_view(),
        name='as_search'
    ),
    url(
        regex=r'^as/(?P<asn>' + regex.number + ')/whois/$',
        view=as_views.ASWhoisView.as_view(),
        name='as_whois'
    ),
    url(
        regex=r'^ix/(?P<code>' + regex.ix_code + ')/'
        '(?P<asn>' + regex.number + ')/$',
        view=as_views.ASIXDetailView.as_view(),
        name='ix_as_detail'
    ),
]

core_urls = [
    url(
        regex=r'^ix/(?P<code>' + regex.ix_code + ')/bundle/$',
        view=core_views.BundleEtherListView.as_view(),
        name='bundle_list'
    ),
    url(
        regex=r'^(?:home)?/?$',
        view=core_views.HomeView.as_view(),
        name='home'
    ),
    url(
        regex=r'^name/search/',
        view=core_views.SearchASNByNameView.as_view(),
        name='name_search'
    ),
    url(
        regex=r'^uuid/search/',
        view=core_views.SearchUUIDView.as_view(),
        name='uuid_search'
    ),
]

forms_urls = [
    url(
        regex=r'^form/add-contact/(?P<asn>' + regex.number + ')/$',
        view=form_views.AddASContactFormView.as_view(),
        name='add_as_contact_form'
    ),
    url(
        regex=r'^form/add-customer-channel/(?P<asn>' + regex.number +
        ')/(?P<pix>' + regex.uuid + ')/$',
        view=form_views.AddCustomerChannelFormView.as_view(),
        name='add_customer_channel_form'
    ),
    url(
        regex=r'^form/add-bilateral/(?P<asn>' + regex.number +
        ')/(?P<channel>' + regex.uuid + ')/$',
        view=form_views.AddBilateralFormView.as_view(),
        name='add_bilateral_form'
    ),
    url(
        regex=r'^form/add-contact/(?P<contactsmap>' + regex.uuid + ')/$',
        view=form_views.AddContactFormView.as_view(),
        name='add_contact_form'
    ),
    url(
        regex=r'^form/add-dio/(?P<pix>' + regex.uuid + ')/$',
        view=form_views.AddDIOToPIXFormView.as_view(),
        name='add_dio_form'
    ),
    url(
        regex=r'^form/add-ix-to-asn/(?P<asn>' + regex.number + ')/$',
        view=form_views.AddIXtoASNFormView.as_view(),
        name='add_ix_to_asn_form'
    ),
    url(
        regex=r'^form/add-phone/(?P<contact>' + regex.uuid + ')/$',
        view=form_views.AddPhoneFormView.as_view(),
        name='add_phone_form'
    ),
    url(
        regex=r'^form/create-ix/$',
        view=form_views.CreateIXFormView.as_view(),
        name='create_ix_form'
    ),
    url(
        regex=r'^form/edit-contact/(?P<contact>' + regex.uuid +
        ')/(?P<contactsmap>' + regex.uuid + ')/(?P<type_contact>' +
        regex.type + ')/$',
        view=form_views.EditContactFormView.as_view(),
        name='edit_contact_form'
    ),
    url(
        regex=r'^form/edit-contacts-map/(?P<contactsmap>' + regex.uuid +
        ')/(?P<ix>' + regex.ix_code + ')/(?P<asn>' + regex.number + ')/$',
        view=form_views.EditContactsMapFormView.as_view(),
        name='edit_contacts_map_form'
    ),
    url(
        regex=r'^form/create-organization/$',
        view=form_views.CreateOrganizationFormView.as_view(),
        name='create_organization_form'
    ),
    url(
        regex=r'^form/create-port-physical-interface/$',
        view=form_views.CreatePortPhysicalInterfaceFormView.as_view(),
        name='create_port_physical_interface_form'
    ),
    url(
        regex=r'^form/migrate-switch/(?P<pix>' + regex.uuid + ')/$',
        view=form_views.MigrateSwitchFormView.as_view(),
        name='migrate_switch_form'
    ),
    url(
        regex=r'^form/edit-dio-port/(?P<pix>' + regex.uuid +
        ')/(?P<dio_port>' + regex.uuid + ')/$',
        view=form_views.EditDioPortFormView.as_view(),
        name='edit_dio_port_form'
    ),
    url(
        regex=r'^form/edit_description_by_port/(?P<port>' + regex.uuid +
        ')/$',
        view=form_views.EditDescriptionByPortFormView.as_view(),
        name='edit_description_by_port_form'
    ),
    url(
        regex=r'^form/edit-tag-description/(?P<tag>' + regex.uuid +
        ')/$',
        view=form_views.EditTagDescriptionFormView.as_view(),
        name='edit_tag_description_form'
    ),
    url(
        regex=r'^form/edit-ip-description/(?P<ipv4>' + regex.ipv4 +
        ')/(?P<ipv6>' + regex.ipv6 + ')/$',
        view=form_views.EditIPDescriptionFormView.as_view(),
        name='edit_ip_description_form'
    ),
    url(
        regex=r'^form/edit-cix-type/(?P<channel>' + regex.uuid + ')/$',
        view=form_views.EditCixTypeFormView.as_view(),
        name='edit_cix_type_form'
    ),
    url(
        regex=r'^form/phone-edit/(?P<phone>' + regex.uuid + ')/$',
        view=form_views.EditPhoneFormView.as_view(),
        name='edit_phone_form'
    ),
    url(
        regex=r'^form/add-port-channel/(?P<pix>' + regex.uuid +
        ')/(?P<channel>' + regex.uuid + ')/$',
        view=form_views.AddPortChannelFormView.as_view(),
        name='add_port_channel_form'
    ),
    url(
        regex=r'^form/edit-port-interface-physical/(?P<port>' + regex.uuid +
        ')/$',
        view=form_views.EditPortPhysicalInterfaceFormView.as_view(),
        name='edit_port_physical_interface_form'
    ),
    url(
        regex=r'^form/edit-port-configured-capacity/(?P<port>' +
        regex.uuid + ')/$',
        view=form_views.EditConfiguredCapacityPortFormView.as_view(),
        name='edit_port_configured_capacity_form'
    ),
    url(
        regex=r'^form/generic-mlpa-add/(?P<asn>' + regex.number +
        ')/(?P<channel>' + regex.uuid + ')/(?P<code>' + regex.ix_code + ')/$',
        view=form_views.GenericMLPAUsedChannelFormView.as_view(),
        name='generic_mlpa_add_form'
    ),
    url(
        regex=r'^form/generic-new-mlpa-add/(?P<asn>' + regex.number +
        ')/(?P<code>' + regex.ix_code + ')/$',
        view=form_views.GenericMLPANewChannelFormView.as_view(),
        name='generic_new_mlpa_add_form'
    ),
    url(
        regex=r'^form/new-bilateral-used-channel/(?P<asn>' + regex.number +
        ')/(?P<code>' + regex.ix_code + ')/$',
        view=form_views.AddBilateralNewChannelFormView.as_view(),
        name='new_bilateral_used_channel'
    ),
    url(
        regex=r'^form/add-mac-service/(?P<service>' + regex.uuid + ')/$',
        view=form_views.AddMACServiceFormView.as_view(),
        name='add_mac_service_form'
    ),
    url(
        regex=r'^form/tag/allocate-status/(?P<ix>' + regex.ix_code +
              ')/$',
        view=form_views.AllocateTagStatusFormView.as_view(),
        name='allocate_tag_status'
    ),
    url(
        regex=r'^form/tag/deallocate-status/(?P<ix>' + regex.ix_code +
              ')/$',
        view=form_views.DeallocateTagStatusFormView.as_view(),
        name='deallocate_tag_status'
    ),
    url(
        regex=r'^form/edit-mlpav4/(?P<service>' + regex.uuid +
        ')/(?P<code>' + regex.ix_code + ')/$',
        view=form_views.EditMLPAv4FormView.as_view(),
        name='edit_mlpav4_form'
    ),
    url(
        regex=r'^form/edit-mlpav6/(?P<service>' + regex.uuid +
        ')/(?P<code>' + regex.ix_code + ')/$',
        view=form_views.EditMLPAv6FormView.as_view(),
        name='edit_mlpav6_form'
    ),
    url(
        regex=r'^form/modal-feedback/$',
        view=form_views.EditContactFormView.as_view(),
        name='modal_feedback'
    ),
    url(
        regex=r'^form/edit-organization/(?P<organization>' + regex.uuid +
        ')/$',
        view=form_views.EditOrganizationFormView.as_view(),
        name='edit_organization_form'
    ),
    url(
        regex=r'^form/add-pix-to-asn/(?P<ix>' + regex.ix_code +
        ')/(?P<asn>' + regex.number + ')/$',
        view=form_views.AddPixToAsnFormView.as_view(),
        name='add_pix_to_asn_form'
    ),
    url(
        regex=r'^form/edit-service-status/(?P<service>' + regex.uuid + ')/$',
        view=form_views.EditServiceStatusFormView.as_view(),
        name='edit_service_status_form'
    ),
    url(
        regex=r'^form/service-prefix-limit-edit/(?P<service>' + regex.uuid +
        ')/$',
        view=form_views.EditServicePrefixLimitFormView.as_view(),
        name='edit_service_prefix_limit_form'
    ),
    url(
        regex=r'^form/edit-service-tag/(?P<service>' + regex.uuid +
        ')/(?P<code>' + regex.ix_code + ')/$',
        view=form_views.EditServiceTagFormView.as_view(),
        name='edit_service_tag_form'
    ),
    url(
        regex=r'^form/ip/resource-reserve/(?P<ix>' + regex.ix_code + ')/$',
        view=form_views.ReserveIPResourceFormView.as_view(),
        name='reserve_ip_resource'
    ),
    url(
        regex=r'^form/ip/resource-release/(?P<ix>' + regex.ix_code + ')/$',
        view=form_views.ReleaseIPResourceFormView.as_view(),
        name='release_ip_resource'
    ),
    url(
        regex=r'^form/port/resource-reserve/(?P<sw>' + regex.uuid +
              ')/$',
        view=form_views.ReservePortResourceFormView.as_view(),
        name='reserve_port_resource'
    ),
    url(
        regex=r'^form/port/resource-release/(?P<sw>' + regex.uuid + ')/$',
        view=form_views.ReleasePortResourceFormView.as_view(),
        name='release_port_resource'
    ),
    url(
        regex=r'^form/port/add-switch-module/(?P<switch>' + regex.uuid + ')/$',
        view=form_views.AddNewSwitchModuleFormView.as_view(),
        name='add_switch_module'
    ),
    url(
        regex=r'^form/tag/resource-reserve/(?P<ix>' + regex.ix_code +
              ')/$',
        view=form_views.ReserveTagResourceFormView.as_view(),
        name='reserve_tag_resource'
    ),
    url(
        regex=r'^form/tag/resource-release/(?P<ix>' + regex.ix_code + ')/$',
        view=form_views.ReleaseTagResourceFormView.as_view(),
        name='release_tag_resource'
    ),
    url(
        regex=r'^form/switch/create/(?P<pix>' + regex.uuid + ')/$',
        view=form_views.CreateSwitchFormView.as_view(),
        name='create_switch_form'
    ),
    url(
        regex=r'^form/pix/create/(?P<ix>' + regex.ix_code + ')/$',
        view=form_views.CreatePixFormView.as_view(),
        name='create_pix_form'
    ),
    url(
        regex=r'^form/switchmodel/create/$',
        view=form_views.CreateSwitchModelFormView.as_view(),
        name='create_switch_model_form'
    ),
    url(
        regex=r'^form/add-uplink-core-channel-port/(?P<ix>' + regex.ix_code +
        ')/(?P<switch>' + regex.uuid + ')/(?P<port>' + regex.uuid + ')/$',
        view=form_views.CreateUplinkCoreChannelModelFormView.as_view(),
        name='add_uplink_core_channel_port_form'
    ),
]

function_based_urls = [
    url(
        regex=r'^as/populate-as-contact/',
        view=function_based_views.get_ticket_add_add_ajax__as_view,
        name='as_populate_contact'
    ),
    url(
        regex=r'^get-cix-type-by-customer-channel/$',
        view=function_based_views.get_cix_type_by_customer_channel,
        name='get_cix_type_by_customer_channel'
    ),
    url(
        regex=r'^get-bilateral-type/$',
        view=function_based_views.get_bilateral_type,
        name='get_bilateral_type'
    ),
    url(
        regex=r'^get-customer-channels-by-switch/$',
        view=function_based_views.get_new_customer_channels_by_switch,
        name='get_customer_channels_by_switch'
    ),
    url(
        regex=r'^get-customer-channels-by-switch-and-asn/$',
        view=function_based_views.get_customer_channels_by_switch_and_asn,
        name='get_customer_channels_by_switch_and_asn'
    ),
    url(
        regex=r'^(?P<code>' + regex.ix_code + ')/'
        'get-ip-informations-by-click/$',
        view=function_based_views.get_ip_informations_by_click__ip_views,
        name='get_ip_informations_by_click__ip_views'
    ),
    url(
        regex=r'^get-ips-and-tags-by-ix/$',
        view=function_based_views.get_ips_and_tags_by_ix,
        name='get_ips_and_tags_by_ix'
    ),
    url(
        regex=r'^get-lag-port/$',
        view=function_based_views.get_lag_port,
        name='get_lag_port'
    ),
    url(
        regex=r'^(?P<code>' + regex.ix_code + ')/'
        'get-match-ips-by-asn-search/$',
        view=function_based_views.get_match_ips_by_asn_search__ip_views,
        name='get_match_ips_by_asn_search__ip_views'
    ),
    url(
        regex=r'^(?P<code>' + regex.ix_code + ')/'
        'get-match-tags-by-asn-search/$',
        view=function_based_views.get_match_tags_by_asn_search__tag_views,
        name='get_match_tags_by_asn_search__tag_views'
    ),
    url(
        regex=r'^get-ports-by-switch/$',
        view=function_based_views.get_ports_by_switch_search__as_detail,
        name='get_ports_by_switch_search__as_detail'
    ),
    url(
        regex=r'^get-switchs-by-pix/$',
        view=function_based_views.get_switchs_by_pix_search__as_detail,
        name='get_switchs_by_pix_search__as_detail'
    ),
    url(
        regex=r'^get-tags-by-port/$',
        view=function_based_views.get_tags_by_port,
        name='get_tags_by_port'
    ),
    url(
        regex=r'^(?P<code>' + regex.ix_code + ')/'
        'get-tag-informations-by-click/$',
        view=function_based_views.get_tag_informations_by_click__tag_views,
        name='get_tag_informations_by_click__tag_views'
    ),
    url(
        regex=r'^get-used-customer-channels-by-switch/$',
        view=function_based_views.get_used_customer_channels_by_switch,
        name='get_used_customer_channels_by_switch'
    ),
    url(
        regex=r'^search-customer-channel-by-mac/$',
        view=function_based_views.search_customer_channel_by_mac,
        name='search_customer_channel_by_mac'
    ),
]

delete_urls = [
    url(
        regex=r'^form/delete-mac-address/$',
        view=form_views.MACDeleteView.as_view(),
        name='delete_mac_address_form'
    ),
    url(
        regex=r'^form/phone-delete/(?P<phone>' + regex.uuid + ')/$',
        view=form_views.DeletePhoneView.as_view(),
        name='delete_phone_form'
    ),
    url(
        regex=r'^remove-switch-module/$',
        view=function_based_views.remove_switch_module,
        name='remove_switch_module'
    ),
    url(
        regex=r'^service/delete/(?P<service_pk>' + regex.uuid + ')/$',
        view=function_based_views.delete_service,
        name='service_delete'
    ),
]

ip_urls = [
    url(
        regex=r'^ix/(?P<code>' + regex.ix_code + ')/ips/$',
        view=ip_views.IPListView.as_view(),
        name='ip_list'
    ),
]

ix_urls = [
    url(
        regex=r'^ix/(?P<dio>' + regex.uuid + ')/dio/$',
        view=ix_views.DIOView.as_view(),
        name='dio_detail'
    ),
    url(
        regex=r'^ix/(?P<code>' + regex.ix_code + ')/pix/(?P<pix>' +
        regex.uuid + ')/dio/$',
        view=ix_views.DIOListView.as_view(),
        name='dio_list'
    ),
    url(
        regex=r'^ix/(?P<code>' + regex.ix_code + ')/(?P<asn>[\d]+)/stats/$',
        view=ix_views.IXStatsView.as_view(),
        name='ix_as_stats'
    ),
    url(
        regex=r'^ix/(?P<code>' + regex.ix_code + ')/$',
        view=ix_views.IXDetailView.as_view(),
        name='ix_detail'
    ),
    url(
        regex=r'^(' + regex.ix_code + ')/cix-detail/$',
        view=function_based_views.ix_detail_cix_ajax__ix_views,
        name='ix_detail_cix'
    ),
    url(
        regex=r'^(' + regex.ix_code + ')/pix-detail/$',
        view=function_based_views.ix_detail_pix_ajax__ix_views,
        name='ix_detail_pix'
    ),
    url(
        regex=r'^ip/search/(?P<code>' + regex.ix_code + ')/$',
        view=ix_views.IPSearchView.as_view(),
        name='ip_search'
    ),
    url(
        regex=r'^mac/search/(?P<code>' + regex.ix_code + ')',
        view=ix_views.MacSearchView.as_view(),
        name='mac_search'
    ),
    url(
        regex=r'^tag/search/(?P<code>' + regex.ix_code + ')',
        view=ix_views.TagSearchView.as_view(),
        name='tag_search'
    ),
    url(
        regex=r'^ix/(?P<code>' + regex.ix_code +
        ')/(?P<asn>[\d]+)/bilaterals/$',
        view=TemplateView.as_view(template_name='ix/bilateral_list.html'),
        name='bilateral_list'
    ),
]

switch_urls = [
    url(
        regex=r'^ix/(?P<code>' + regex.ix_code + ')/switch/'
        '(?P<switch_uuid>' + regex.uuid + ')/$',
        view=switch_views.SwitchListView.as_view(),
        name='switch_detail'
    ),
    url(
        regex=r'^switch-module-detail/(?P<module>' + regex.uuid + ')/$',
        view=switch_views.SwitchModuleDetailView.as_view(),
        name='switch_module_detail'
    ),
]

tag_urls = [
    url(
        regex=r'^ix/(?P<code>' + regex.ix_code + ')/bundle/'
        '(?P<bundle_pk>' + regex.uuid + ')/$',
        view=tag_views.TAGsListView.as_view(),
        name='tag_list_with_bundle'
    ),
    url(
        regex=r'^ix/(?P<code>' + regex.ix_code + ')/tags/$',
        view=tag_views.TAGsListView.as_view(),
        name='tag_list_without_bundle'
    ),
    url(
        regex=r'^ix/(?P<code>' + regex.ix_code + ')/tags/(?P<status>' +
              regex.tag_status + ')$',
        view=tag_views.TAGsListView.as_view(),
        name='filtered_tag_list_without_bundle'
    ),
]

nikiti_urls = [
    url(
        regex=r'^nikiti/monitoramento_interface/(?P<ix>' + regex.ix_code +
              ')',
        view=nikiti_views.MonitoramentoInterfaces.as_view(),
        name='nikiti_monitoramento_de_interfaces'
    ),
    url(
        regex=r'^nikiti/alocacao_de_ip/(?P<ix>' + regex.ix_code + ')',
        view=nikiti_views.AlocacaoDeIP.as_view(),
        name='nikiti_alocacao_de_ip'
    ),
    url(
        regex=r'^nikiti/vlans/(?P<ix>' + regex.ix_code + ')',
        view=nikiti_views.Vlans.as_view(),
        name='nikiti_vlans'
    )
]


urlpatterns = core_urls + as_urls + ix_urls + forms_urls + delete_urls + \
    function_based_urls + ip_urls + switch_urls + tag_urls + nikiti_urls
