from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.db.models import Q

from ..models import CustomerChannel, MACAddress

def search_customer_channel_by_mac_address(**kwargs):

	address = kwargs.pop('address')
	channels = CustomerChannel.objects.filter(
		Q(mlpav4__mac_addresses__address=address)|
		Q(mlpav6__mac_addresses__address=address)|
		Q(monitorv4__mac_addresses__address=address)|
		Q(bilateralpeer__mac_addresses__address=address))

	return set(channels)

