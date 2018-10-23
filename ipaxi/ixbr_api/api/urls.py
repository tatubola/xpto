from .api_views import (BilateralViewSet, IXViewSet)
from ixbr_api.core.utils.regex import Regex
from rest_framework.routers import DefaultRouter

v1router = DefaultRouter()
regex = Regex()

v1router.register(r'ix', IXViewSet, 'ix')
v1router.register(r'ix/(?P<code>' + regex.ix_code + ')/asn/(?P<asn>' +
                  regex.number + ')/bilaterals', BilateralViewSet,
                  'bilateral')
