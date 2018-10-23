from rest_framework import serializers

from .models import (IX, Contrato, Fatura, OrdemDeCompra, Participante,
                     PerfilParticipante, Servico)


class ParticipanteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Participante
        fields = ('__all__')


class PerfilParticipanteSerializer(serializers.ModelSerializer):

    class Meta:
        model = PerfilParticipante
        fields = ('tipo', 'fator_de_desconto')


class FaturaSerializer(serializers.ModelSerializer):
    participante = serializers.PrimaryKeyRelatedField(
        queryset=Participante.objects.all())

    class Meta:
        model = Fatura
        fields = ('__all__')
        depth = 1


class ContratoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contrato
        fields = ('__all__')
        depth = 1


class ServicoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Servico
        fields = ('tipo', 'hash', 'recorrente', 'data_expiracao',
                  'participante', 'ix', 'preco', 'uuid')


class OrdemCompraSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrdemDeCompra
        fields = ('fatura', 'identificacao_oc', 'url')


class IXSerializer(serializers.ModelSerializer):

    class Meta:
        model = IX
        fields = ('ix_id', 'codigo', 'nome_curto', 'nome_longo', 'estado',
                  'cidade')
