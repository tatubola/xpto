from django.db.models import Q
from django_filters.rest_framework import (BaseInFilter, CharFilter,
                                           DjangoFilterBackend, FilterSet,
                                           NumberFilter)
from rest_framework import filters, viewsets

from .models import (IX, Contrato, Fatura, OrdemDeCompra, Participante,
                     PerfilParticipante, Servico)
from .serializers import (ContratoSerializer, FaturaSerializer, IXSerializer,
                          OrdemCompraSerializer, ParticipanteSerializer,
                          PerfilParticipanteSerializer, ServicoSerializer)


class ParticipantesViewSet(viewsets.ModelViewSet):
    queryset = Participante.objects.all()
    serializer_class = ParticipanteSerializer
    lookup_field = 'uuid'
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('ix_id__codigo', 'asn', 'cnpj')


class PerfilParticipanteViewSet(viewsets.ModelViewSet):
    queryset = PerfilParticipante.objects.all()
    serializer_class = PerfilParticipanteSerializer
    lookup_field = 'uuid'
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)


class ContratoViewSet(viewsets.ModelViewSet):
    queryset = Contrato.objects.all()
    serializer_class = ContratoSerializer
    lookup_field = 'uuid'
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('assinado', 'vigente', 'ix__codigo', 'participante__asn')


class FaturaViewSet(viewsets.ModelViewSet):
    queryset = Fatura.objects.all()
    serializer_class = FaturaSerializer
    lookup_field = 'id_financeiro'
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('participante__asn', 'participante__ix_id__codigo',
                     'encerrada', 'estado')


class OrdemDeCompraViewSet(viewsets.ModelViewSet):
    queryset = OrdemDeCompra.objects.all()
    serializer_class = OrdemCompraSerializer
    lookup_field = 'identificacao_oc'
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)


class ServicoViewSet(viewsets.ModelViewSet):
    queryset = Servico.objects.all()
    serializer_class = ServicoSerializer
    lookup_field = 'uuid'
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('participante', 'hash', 'ix')


class IXViewSet(viewsets.ModelViewSet):
    queryset = IX.objects.all()
    serializer_class = IXSerializer
    lookup_field = 'codigo'
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)


class IXPorParticipanteViewSet(viewsets.ModelViewSet):
    serializer_class = IXSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)

    def get_queryset(self):
        asn = self.kwargs['asn']

        return IX.objects.filter(participante__asn=asn)


class ServicosNaoFaturadosViewSet(viewsets.ModelViewSet):
    serializer_class = ServicoSerializer
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        ix_codigo = self.kwargs['ix_codigo']
        asn = self.kwargs['asn']

        return Servico.em_fatura.aberta().filter(Q(participante__asn=asn) and
                                                 (Q(ix__codigo=ix_codigo)))


class ServicosFaturadosViewSet(viewsets.ModelViewSet):
    serializer_class = ServicoSerializer
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        ix_codigo = self.kwargs['ix_codigo']
        asn = self.kwargs['asn']

        return Servico.em_fatura.fechada().filter(Q(participante__asn=asn) and
                                                 (Q(ix__codigo=ix_codigo)))
