from django.db import models
from django.utils import timezone

from datetime import datetime


# Managers for Contrato Model
class ContratosAssinados(models.Manager):
    def get_queryset(self):
        return super(ContratosAssinados, self).get_queryset().filter(
            assinado=True)


class ContratosNaoAssinados(models.Manager):
    def get_queryset(self):
        return super(ContratosNaoAssinados, self).get_queryset().filter(
            assinado=False)


class ContratosVigentes(models.Manager):
    def get_queryset(self):
        return super(ContratosVigentes, self).get_queryset().filter(
            vigente=True)


# Manager para o modelo Fatura
class FaturaVencidaManager(models.Manager):
    def get_queryset(self):
        return super(FaturaVencidaManager, self).get_queryset().filter(
            vencimento__lt=datetime.today())


class FaturaAbertaManager(models.Manager):
    def get_queryset(self):
        return super(FaturaAbertaManager, self).get_queryset().filter(
            vencimento__gte=datetime.today())


# Manager e QuerySet para o modelo Servico
class ServicoQuerySet(models.QuerySet):
    def faturados(self):
        """
        Esta queryset mostra os Servicos que já foram pagos ou estão em
        alguma fatura com status de gerada.
        """
        return self.filter(
            models.Q(fatura__estado='paga') |
            models.Q(fatura__estado='gerada'))

    def abertos(self):
        """

        """
        hoje = timezone.now()
        venc_mes_corrente = hoje.replace(day=28)
        venc_mes_passado = hoje.replace(day=28, month=hoje.month - 1)

        servicos_pagos_gerados = self.faturados()

        servicos_em_faturas_canceladas = self.filter(
            fatura__estado='cancelada').\
            exclude(uuid__in=servicos_pagos_gerados)

        servicos_mes_corrente = self.filter(
            models.Q(data_expiracao__range=(
                   venc_mes_passado.replace(hour=00, minute=00),
                   venc_mes_passado.replace(hour=23, minute=59))) |
            models.Q(data_expiracao__gt=venc_mes_corrente)).exclude(
            uuid__in=servicos_pagos_gerados)

        return (servicos_em_faturas_canceladas |
                servicos_mes_corrente).distinct()


class ServicoManager(models.Manager):
    def get_queryset(self):
        return ServicoQuerySet(self.model, using=self._db)

    def fechada(self):
        return self.get_queryset().faturados()

    def aberta(self):
        return self.get_queryset().abertos()
