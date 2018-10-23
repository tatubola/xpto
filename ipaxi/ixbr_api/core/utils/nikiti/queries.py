""" This script perform queries on Django DB to build Nikiti Pages
"""

# System Imports
from re import compile

# Local source tree Imports
from ....core.models import IX, PIX, ChannelPort, Port, Switch

# Third-party Imports




class Query(object):
    """
    Parent Query class
    """

    def __init__(self, ix):
        self.ix_obj = IX.objects.get(code=ix)
        self.ix = ix

    def get_all_pix(self):
        """
        Query for all pixes in a location (IX)

        Returns: a list with all pixes of a given location

        """
        return PIX.objects.filter(ix=self.ix)

    def get_all_switches(self):
        """
        Query all switches of a location (IX)

        Returns: a list with all switches of a given location

        """
        pix_list = self.get_all_pix()
        sw_list = [Switch.objects.get(pk=sw_pk) for sw_pk in
                   pix_list.values_list('switch', flat=True)]

        return sw_list

    def get_last_ticket(self, port_uuid):
        """
        Get the last ticket related to a Port, look for all services related
        to a Port and get the latest ticket

        Args:
            port_uuid: Port UUID to query last ticket

        Returns: The last ticket

        """
        recent_date = None
        recent_ticket = None

        port_services = self.get_services_per_port(port_uuid=port_uuid)

        for service, val in port_services.items():
            if len(val) > 0:
                for s in val:
                    if recent_date is None:
                        recent_date = s.created
                        recent_ticket = s.last_ticket
                    else:
                        if s.created > recent_date:
                            recent_date = s.created
                            recent_ticket = s.last_ticket
                        else:
                            continue

        return recent_ticket

    def get_services_per_port(self, port_uuid):
        """
        Query all services related to a port

        Args:
            port_uuid: The port to query

        Returns: A dict mapping all services allocated to a given service

        """
        services_dict = dict()
        cur_port = Port.objects.get(uuid=port_uuid)

        if cur_port.status != "CUSTOMER":
            return services_dict
        else:
            customer_channel = cur_port.channel_port.customerchannel

            if customer_channel.mlpav4_set is not None:
                services_dict["mlpav4"] = list(
                    customer_channel.mlpav4_set.all())

            if customer_channel.mlpav6_set is not None:
                services_dict["mlpav6"] = list(
                    customer_channel.mlpav6_set.all())

            if customer_channel.bilateralpeer_set is not None:
                services_dict["bilateralpeer"] = list(
                    customer_channel.bilateralpeer_set.all())

            if customer_channel.monitorv4_set is not None:
                services_dict["monitorv4"] = list(
                    customer_channel.monitorv4_set.all())

            return services_dict

    def get_tag_per_port(self, port_uuid):
        """
        This method finds all tags related to a given port
        Args:
            port_uuid: The port to query

        Returns: A dict with all tags per service for a port

        """
        tag_dict = dict()
        port = Port.objects.get(uuid=port_uuid)
        service_list = self.get_services_per_port(port.uuid)

        for service_type, service_list in service_list.items():
            if len(service_list) > 0:
                if service_type not in tag_dict:
                    tag_dict[service_type] = list()
                for service in service_list:
                    if service not in tag_dict[service_type]:
                        tag_dict[service_type].append(service.tag)

        return tag_dict

    def get_asn_per_port(self, port_uuid):
        """
        Finds the ASN related to a given port

        Args:
            port_uuid: The port UUID which AS must be found

        Returns: An ASN object

        """
        cur_port = Port.objects.get(uuid=port_uuid)
        if cur_port.status == "CUSTOMER":
            customer_channel = cur_port.channel_port.customerchannel
        else:
            return None

        return customer_channel.asn


class MonitoracaoInterfaces(Query):
    """
    This class defines queries related to Monitoracao de Interfaces
    """

    def get_asn_per_switch_port(self, switch_uuid):
        """
        Finds ASN related to a given Port of a Switch

        Args:
            switch_uuid: The UUID (pk) of a Switch to find all ASs related to it

        Returns: A dict mapping a port to an AS

        """

        switch = Switch.objects.get(pk=switch_uuid)
        asn_port_mapping = dict()

        for port in switch.port_set.all():
            if port.status == "CUSTOMER":
                port_asn = self.get_asn_per_port(port_uuid=port.uuid)
                asn_port_mapping[port.name] = port_asn.number

        return asn_port_mapping

    def get_port_type(self, port_uuid):
        """
        Identifies if a port is Uplink, Downlink (type=U) or Customer (type=P).
        Args:
            port_uuid: The port UUID that owns the ports to query

        Returns: Port type (U or P)

        """
        port = Port.objects.get(uuid = port_uuid)
        if port.status == "CUSTOMER":
            port_type = "P"
        elif port.status == "INFRASTRUCTURE":
            port_type = "D"
        else:
            port_type = None

        return port_type

    def get_channel_master(self, port_uuid):
        """
        If port belongs to a Channel, this query returns the master port

        Args:
            port_uuid: Port UUID to query

        Returns: The master port of a channel or None if port does not belong
        to a Channel

        """

        cur_port = Port.objects.get(uuid=port_uuid)
        channel_port = ChannelPort.objects.get(uuid=cur_port.channel_port.uuid)

        if cur_port.status != "INFRASTRUCTURE":
            return None
        else:
            # Verify channel type (Downlink or Uplink)
            if getattr(channel_port, "downlinkchannel", None) is not None:
                channel = channel_port.downlinkchannel
            elif getattr(channel_port, "uplinkchannel", None) is not None:
                channel = channel_port.uplinkchannel
            else:
                channel = channel_port.corechannel

        return channel.get_master_port()

    def get_port_connection(self, port_uuid):
        """
        This method finds the channel that connects to another connection

        Args:
            port_uuid: The port UUID to query the connection

        Returns: List of ports connected

        """
        cur_port = Port.objects.get(uuid=port_uuid)
        channel_port = ChannelPort.objects.get(uuid=cur_port.channel_port.uuid)

        if getattr(channel_port, "downlinkchannel", None) is not None:
            return list(channel_port.downlinkchannel.uplinkchannel.get_ports())
        elif getattr(channel_port, "uplinkchannel", None) is not None:
            return list(channel_port.uplinkchannel.downlink_channel.get_ports())
        else:
            return list(channel_port.corechannel.get_ports())

    def get_port_status(self, port_uuid):
        """
        Populates the nikiti's status column
        Args:
            port_uuid: The UUID of a Port to query

        Returns: Status information for a port

        """
        port = Port.objects.get(pk=port_uuid)
        tag_occur_v4 = list()
        tag_occur_v6 = list()

        if port.status == "CUSTOMER":
            port_status_mapping = list()
            switch_model = port.switch.model.vendor
            if switch_model == "EXTREME":
                nikiti_sw_model = "- extreme-tr"
            elif switch_model == "CISCO":
                nikiti_sw_model = "- cisco-tr"
            else:
                nikiti_sw_model = "- "

            port_asn = self.get_asn_per_port(port_uuid=port.uuid)
            nikiti_asn = nikiti_sw_model + "  as" + str(port_asn.number)

            port_tags = self.get_tag_per_port(port_uuid=port.uuid)
            for service_type, tag_list in port_tags.items():
                if service_type == "mlpav6":
                    nikiti_service_type = nikiti_asn + "-tr-v6"
                else:
                    nikiti_service_type = nikiti_asn + "-tr"

                if len(tag_list) == 1:
                    nikiti_final_name = nikiti_service_type + "     (" + str(
                        tag_list[0].tag) + ")"
                    port_status_mapping.append(nikiti_final_name)
                    tag_occur_v4.append(tag_list[0].tag) if service_type == \
                                                             "mlpav4" else \
                        tag_occur_v6.append(tag_list[0].tag)

                elif len(tag_list) > 1:
                    tag_count = 0
                    for tag in tag_list:
                        if tag.tag in tag_occur_v4 or tag.tag in tag_occur_v6:
                            continue
                        else:
                            tag_occur_v4.append(tag.tag) if \
                                service_type == "mlpav4" else \
                                tag_occur_v6.append(tag.tag)
                            if tag_count == 0:
                                nikiti_final_name = nikiti_service_type + "     (" \
                                                    + str(tag.tag) + ")"
                            else:
                                nikiti_final_name = nikiti_service_type + "-" + \
                                                    str(tag_count) + "     (" + \
                                    str(tag.tag) + ")"
                            tag_count += 1
                            port_status_mapping.append(nikiti_final_name)
            return port_status_mapping

        elif port.status == "INFRASTRUCTURE":
            port_status_mapping = ""
            master_port = self.get_channel_master(port_uuid=port_uuid)

            if master_port.name == port.name:
                status_ticket = "Ativo Principal"
            else:
                status_ticket = "Ativo"
            port_status_mapping = status_ticket
            return port_status_mapping

        else:
            # Returns an empty string to "render nothing"
            return ""


class AlocacaoDeIps(Query):
    """
    This class defines queries related to IP Allocation
    """

    def ip_used_dict(self, channel_port):
        """
        This private method generates a dict where the index is the IP
        address and the value is the ASN.

        Args:
            channel_port: The channel port to query the IP addr and ASN

        Returns:
            {
                ipv4: {
                        <IPv4>: <ASN>,
                        <IPv4>: <ASN>,
                        ...
                    }
                ipv6: {

                        <IPv6>: <ASN>,
                        <IPv6>: <ASN>,
                        ...
                }

            }
        """
        ipv4_dict = dict()
        ipv6_dict = dict()

        if getattr(channel_port, "customerchannel", None) is not None:
            for srv in channel_port.customerchannel.mlpav4_set.all():
                ipv4_dict[srv.get_address().address] = srv.asn

            for srv in channel_port.customerchannel.mlpav6_set.all():
                ipv6_dict[srv.get_address().address] = srv.asn

        return {
            "ipv4": ipv4_dict,
            "ipv6": ipv6_dict
        }

    def find_asn_per_last_ip_value(self, ip_to_match, ip_dict):
        """
        This private method looks for an ASN allocated to a given IP.
        However, it is used the final octets (IPv4 Addr) or final hextet (
        IPv6 Addr).

        Args:
            ip_to_match: The final number (last octet for an IPv4 Address or the
            last hextet for an IPv6 Address)
            ip_dict: A dict in the following form
                {
                    <IP_Addr> : <ASN>,
                    <IP_Addr> : <ASN>,
                    ....
                }

        Returns: None if the IP is not found inside the Dict or the ASN for
        that IP.
        """

        is_ipv4_regex = compile("\A[\d]+\.{1}")
        last_octet_v4_regex = compile("\.(\d+)$")
        last_hextet_v6_regex = compile(":{1,2}([\w|\d]+)$")

        if is_ipv4_regex.match(ip_to_match):
            is_ipv4 = True
            final = last_octet_v4_regex.search(ip_to_match).group(1)
        else:
            is_ipv4 = False
            final = last_hextet_v6_regex.search(ip_to_match).group(1)

        for ip, asn in ip_dict.items():
            if is_ipv4:
                if final == last_hextet_v6_regex.search(ip).group(1):
                    return {"ip": ip,
                            "asn": asn}
                else:
                    continue
            else:
                if final == last_octet_v4_regex.search(ip).group(1):
                    return {"ip": ip,
                            "asn": asn}
                else:
                    continue

        return None

    def get_ip_range(self):
        """
        Get IP (v4 and v6) prefixes of a given IX

        Returns: A dict with ipv4 and ipv6 prefixes

        """

        return {
            "ipv4_range": self.ix_obj.ipv4_prefix,
            "ipv6_range": self.ix_obj.ipv6_prefix
                }

    def get_all_channel_port(self):
        """

        Returns: A list with all channel ports of a pix

        """
        switch_list = self.get_all_switches()
        channel_port_list = set()

        for switch in switch_list:
            for port in switch.port_set.all():
                if port.channel_port is not None:
                    channel_port_list.add(port.channel_port)

        return channel_port_list


class AlocacaoDeVlans(Query):
    """
    This class defines queries relates to VLAN Allocation
    """
    def get_production_vlans_name(self):
        """
        This method gets the vlan names used by nikiti, generated by method
        get_port_status, implemented in MonitoracaoInterfaces class.

        Returns: A dict with vlan name and the tag id.
            tag_dict = {
                'as1234-tr': '2010',
                'as4321-tr-v6': '2011'
                ...
            }
        """
        tag_dict = dict()
        mi = MonitoracaoInterfaces(ix=self.ix)

        v4_vlan_regex = compile("as\d+-tr(\s|\-\d+)")
        v6_vlan_regex = compile("as\d+-tr-v6(\s|\-\d+)")
        tag_id_regex = compile("\((\d+)\)")

        sw_list = self.get_all_switches()
        for switch in sw_list:
            for port in switch.port_set.all():
                port_status = mi.get_port_status(port.uuid)
                for status in port_status:
                    tag_name_finder_v4 = v4_vlan_regex.search(status)
                    if tag_name_finder_v4 is not None:
                        tag_id = tag_id_regex.search(status)
                        tag_dict[tag_name_finder_v4.group(0).strip()] = \
                            int(tag_id.group(1))

                    tag_name_finder_v6 = v6_vlan_regex.search(status)
                    if tag_name_finder_v6 is not None:
                        tag_id = tag_id_regex.search(status)
                        tag_dict[tag_name_finder_v6.group(0).strip()] = \
                            int(tag_id.group(1))

        return tag_dict

    def get_vlans_type(self):
        """
        According to the service type, the tag related to it is classified.

        Args:
            port_uuid:

        Returns: A dictionary
        tag_dict = {
                        "mlpav4":
                        {
                                {
                                    "PRODUCTION": [ list ]
                                },
                                {
                                    "QUARANTINE": [ list ]
                                },
                                {
                                    "INTERNAL": [ list ]
                                }
                        },
                        "mlpav6":
                        {
                                {
                                    "PRODUCTION": [ list ]
                                },
                                {
                                    "QUARANTINE": [ list ]
                                },
                                {
                                    "INTERNAL": [ list ]
                                }
                        }
        }

        """
        tag_dict = dict()
        sw_list = self.get_all_switches()

        for switch in sw_list:
            for p in switch.port_set.all():
                srv_p_list = self.get_services_per_port(p.uuid)
                for service_type, service_list in srv_p_list.items():
                    if len(service_list) > 0:
                        if service_type not in tag_dict:
                            tag_dict[service_type] = dict()
                        for service in service_list:
                            if service.status not in tag_dict[service_type]:
                                tag_dict[service_type][service.status] = \
                                    list()
                            if service.tag not in \
                                tag_dict[service_type][service.status]:
                                tag_dict[service_type][service.status].\
                                    append(service.tag)

        return tag_dict
