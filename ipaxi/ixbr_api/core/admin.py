from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import (ASN, DIO, IX, PIX, Bilateral, BilateralPeer,
                     ChannelPort, Contact, ContactsMap, CoreChannel,
                     CustomerChannel, DIOPort, DownlinkChannel,
                     IPv4Address, IPv6Address, MACAddress, MLPAv4, MLPAv6,
                     Monitorv4, Organization, Phone, PhysicalInterface,
                     Port, Route, Switch, SwitchModel, SwitchPortRange,
                     Tag, TranslationChannel, UplinkChannel, SwitchModule)

admin.site.register(ASN, SimpleHistoryAdmin)
admin.site.register(Bilateral, SimpleHistoryAdmin)
admin.site.register(BilateralPeer, SimpleHistoryAdmin)
admin.site.register(ChannelPort, SimpleHistoryAdmin)
admin.site.register(Contact, SimpleHistoryAdmin)
admin.site.register(ContactsMap, SimpleHistoryAdmin)
admin.site.register(CoreChannel, SimpleHistoryAdmin)
admin.site.register(CustomerChannel, SimpleHistoryAdmin)
admin.site.register(DIO, SimpleHistoryAdmin)
admin.site.register(DIOPort, SimpleHistoryAdmin)
admin.site.register(DownlinkChannel, SimpleHistoryAdmin)
admin.site.register(IPv4Address, SimpleHistoryAdmin)
admin.site.register(IPv6Address, SimpleHistoryAdmin)
admin.site.register(IX, SimpleHistoryAdmin)
admin.site.register(MACAddress, SimpleHistoryAdmin)
admin.site.register(MLPAv4, SimpleHistoryAdmin)
admin.site.register(MLPAv6, SimpleHistoryAdmin)
admin.site.register(Monitorv4, SimpleHistoryAdmin)
admin.site.register(Organization, SimpleHistoryAdmin)
admin.site.register(PIX, SimpleHistoryAdmin)
admin.site.register(Phone, SimpleHistoryAdmin)
admin.site.register(PhysicalInterface, SimpleHistoryAdmin)
admin.site.register(Port, SimpleHistoryAdmin)
admin.site.register(Route, SimpleHistoryAdmin)
admin.site.register(Switch, SimpleHistoryAdmin)
admin.site.register(SwitchModel, SimpleHistoryAdmin)
admin.site.register(SwitchPortRange, SimpleHistoryAdmin)
admin.site.register(Tag, SimpleHistoryAdmin)
admin.site.register(TranslationChannel, SimpleHistoryAdmin)
admin.site.register(UplinkChannel, SimpleHistoryAdmin)
admin.site.register(SwitchModule, SimpleHistoryAdmin)
