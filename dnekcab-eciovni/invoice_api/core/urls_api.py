from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (ContratoViewSet, FaturaViewSet, IXPorParticipanteViewSet,
                    IXViewSet, OrdemDeCompraViewSet, ParticipantesViewSet,
                    PerfilParticipanteViewSet, ServicosFaturadosViewSet,
                    ServicosNaoFaturadosViewSet, ServicoViewSet)

v1router = DefaultRouter()

app_name = "api"

v1router.register(r'participante', ParticipantesViewSet, 'participante')
v1router.register(r'contrato', ContratoViewSet, 'contrato')
v1router.register(r'fatura', FaturaViewSet, 'fatura')
v1router.register(r'ordemdecompra', OrdemDeCompraViewSet, 'ordemdecompra')
v1router.register(r'servico', ServicoViewSet, 'servico')
v1router.register(r'ix', IXViewSet, 'ix')
v1router.register(r'ix-por-participante/(?P<asn>[\d]+)',
                  IXPorParticipanteViewSet, 'ix-por-participante')
v1router.register(r'perfilparticipante', PerfilParticipanteViewSet,
                  'perfilparticipante')
v1router.register(r'servicos-nao-faturados/(?P<asn>[\d]+)/(?P<ix_codigo>[\w]+)',
                  ServicosNaoFaturadosViewSet, 'servicos_nao_faturados')
v1router.register(r'servicos-faturados/(?P<asn>[\d]+)/(?P<ix_codigo>[\w]+)',
                  ServicosFaturadosViewSet, 'servicos_faturados')

urlpatterns = [
    path('', include(v1router.urls)),
]
