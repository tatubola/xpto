""" This script contains views related to Nikiti HTML Generator
"""

# System Imports
from re import findall, sub

# Third-party Imports
from django.shortcuts import render
from django.views.generic import View

# Local source tree Imports
from ..utils.nikiti.queries import (AlocacaoDeIps, AlocacaoDeVlans,
                                    MonitoracaoInterfaces,)


class MonitoramentoInterfaces(View):
    """
    This class implements the View to render nikiti's Monitoramento de
    Interfaces page.
    """

    def build_dict(self, ix):
        """
        This method creates the data structure to be used by Monitoramento de
        Interfaces template.

        Args:
            ix: The ix code to query and builds Nikiti page

        Returns: Dict with all necessary data to build Monitoramento de
        Interfaces page

        """
        query = MonitoracaoInterfaces(ix=ix)
        nikiti_dict_built = dict()

        # First, get all Switches
        sw_ix_list = query.get_all_switches()

        for switch in sw_ix_list:
            s_ip = switch.management_ip
            nikiti_dict_built[s_ip] = dict()
            switch_model = sub(
                r"(\[|\])",
                "",
                str(switch.model)
            )

            nikiti_dict_built[s_ip]["sw_model"] = switch_model
            nikiti_dict_built[s_ip]["pix"] = switch.pix.code
            nikiti_dict_built[s_ip]["ports"] = dict()

            for port in switch.port_set.all():

                if port.status == "CUSTOMER":
                    nikiti_dict_built[s_ip]["ports"][port.name] = dict()
                    port_asn = query.get_asn_per_port(port_uuid=port.uuid)
                    port_tkt = query.get_last_ticket(port_uuid=port.uuid)
                    nikiti_dict_built[s_ip]["ports"][port.name]["ticket"] = \
                        port_tkt
                    nikiti_dict_built[s_ip]["ports"][port.name]["asn"] = \
                        port_asn.number
                    nikiti_dict_built[s_ip]["ports"][port.name]["participante"] =\
                        port_asn.contactsmap_set.first().organization.name
                    port_type = query.get_port_type(port_uuid=port.uuid)
                    nikiti_dict_built[s_ip]["ports"][port.name]["type"] = port_type
                    port_status = query.get_port_status(port_uuid=port.uuid)
                    nikiti_dict_built[s_ip]["ports"][port.name]["status"] = \
                        port_status

                elif port.status == "INFRASTRUCTURE":
                    nikiti_dict_built[s_ip]["ports"][port.name] = dict()
                    nikiti_dict_built[s_ip]["ports"][port.name]["asn"] = "     "

                    # Finds the Router that this port is connected to
                    port_connected = query.get_port_connection(
                        port_uuid=port.uuid)

                    sw_model = port_connected[0].switch.model.model
                    sw_final_oc = findall(r'(\.\d+)$',
                                          port_connected[0]
                                          .switch.management_ip)[0]
                    participant_string = "Uplink-" + sw_model + "    (" + \
                                    sw_final_oc + ")"
                    nikiti_dict_built[s_ip]["ports"][port.name][
                        "participante"] = participant_string
                    port_type = query.get_port_type(port_uuid=port.uuid)
                    nikiti_dict_built[s_ip]["ports"][port.name][
                        "type"] = port_type
                    port_status = query.get_port_status(port_uuid=port.uuid)
                    nikiti_dict_built[s_ip]["ports"][port.name][
                        "status"] = port_status
                else:
                     continue

        return nikiti_dict_built

    def get(self, request, ix):
        context = self.build_dict(ix=ix)
        return render(request,
                      'nikiti/monitoramento_de_interfaces_template.html',
                      {'context': context})


class AlocacaoDeIP(View):
    """
    This class implements the View to render nikiti's Alocacao de IPs page.
    """
    def build_dict(self, ix):
        """

        Args:
            ix:

        Returns:
            {
                ipv4_range:
                ipv6_range:

                <ipv4>: {
                    asn: <yyyy>
                    participante: <yyy>,
                    IPV6: <yyyy>,
                    PIX: <yyyy>,
                    Chamado: <yyyy>
                },
                <ipv4>: {
                    asn: <yyyy>
                    participante: <zzz>,
                    IPV6: <zzzz>,
                    PIX: <zzzz>,
                    Chamado: <zzzz>
                },
                ...
            }
        """
        query = AlocacaoDeIps(ix=ix)
        ip_alloc_dict = dict()
        space = ' '

        ip_alloc_dict["ips_range"] = query.get_ip_range()
        ip_alloc_dict["lines"] = list()
        channel_port_list = query.get_all_channel_port()

        for channel_port in channel_port_list:
            line = ""
            ip_dict = query.ip_used_dict(channel_port)
            last_ticket = str(channel_port.last_ticket)
            pix_id = channel_port.port_set.first().switch.pix.code
            for ip4, asn in ip_dict["ipv4"].items():
                as_name = asn.contactsmap_set.first().organization.name
                line = str(asn.number) + 9*space + as_name + 7*space + ip4
                ip6 = query.find_asn_per_last_ip_value(ip4, ip_dict["ipv6"])
                if ip6 is not None:
                    line = line + 5*space + ip6["ip"]
                    ip_dict["ipv6"].pop(ip6["ip"])
                else:
                    line = line + 15*space
                line = line + 5*space + pix_id + 5*space + "Em ativação [" + \
                       last_ticket + "]"
                ip_alloc_dict["lines"].append(line)
            for ip6, asn in ip_dict["ipv6"]:
                as_name = asn.contactsmap_set.first().organization.name
                line = str(asn.number) + 5*space + as_name + 15*space + ip6

                line = line + 5*space + pix_id + 5*space + "Em ativação [" + \
                   last_ticket + "]"
                ip_alloc_dict["lines"].append(line)
        return ip_alloc_dict

    def get(self, request, ix):
        context = self.build_dict(ix=ix)
        print(context)
        return render(request,
                      'nikiti/alocacao_ips_template.html',
                      {'context': context})


class Vlans(View):
    """
    This class implements the View to render nikiti's VLAN's page.
    """

    def build_dict(self, ix):
        """

        Args:
            ix:

        Returns:

        """
        query = AlocacaoDeVlans(ix=ix)
        special_tag_names = {
            ix + "v4": 10,
            ix + "v6": 20,
            ix + "mgmt": 99
        }

        tags_dict = dict()
        customer_tags_dict = query.get_production_vlans_name()
        tags_type_dict = query.get_vlans_type()

        # QUARANTINE TAGS
        for service, service_type_dict in tags_type_dict.items():
            for service_status in service_type_dict.keys():
                if service_status == "QUARANTINE":
                    qt_count = 1
                    for tag in tags_type_dict[service][service_status]:
                        tag_name_prefix = "qt-v4-" if service == "mlpav4" \
                            else "qt-v6-"
                        if qt_count < 10:
                            tag_sufix = "0" + str(qt_count)
                            tag_qt_name = tag_name_prefix + tag_sufix
                            qt_count += 1
                            tags_dict[tag_qt_name] = tag.tag

        # CUSTOMER TAG
        internal_tags_list = list()
        if 'INTERNAL' in tags_type_dict['mlpav4'].keys():
            internal_tags_list += [k.tag for k in
                                  tags_type_dict['mlpav4']['INTERNAL']]
        if 'INTERNAL' in tags_type_dict['mlpav6'].keys():
            internal_tags_list += [k.tag for k in
                                   tags_type_dict['mlpav6']['INTERNAL']]

        for tag_name, tag_id in customer_tags_dict.items():
            if tag_id not in internal_tags_list:
                tags_dict[tag_name] = tag_id
            else:
                continue

        # SPECIAL TAGS (Internal Use)
        tags_to_remove = [key for key, value in tags_dict.items()
                          if value in special_tag_names]
        for tag, tag_id in tags_to_remove:
            tags_dict.pop(tag)

        tags_dict.update(special_tag_names)
        return tags_dict

    def get(self, request, ix):
        context = self.build_dict(ix=ix)
        return render(request,
                      'nikiti/vlans_template.html',
                      {'context': context})
