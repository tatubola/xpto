from uuid import uuid4

from dirtyfields import DirtyFieldsMixin
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    URLValidator)
from django.db import models
from django.utils import timezone

from simple_history.models import HistoricalRecords

from .models_manager import (ContratosAssinados, ContratosNaoAssinados,
                             ContratosVigentes, FaturaAbertaManager,
                             FaturaVencidaManager, ServicoManager)
from .validators import validacao_cnpj


class Participante(DirtyFieldsMixin, models.Model):
    # atributos do modelo
    asn = models.PositiveIntegerField()
    cnpj = models.CharField(
        blank=True,
        max_length=14,
        null=True,
        validators=[validacao_cnpj],
    )
    data_criacao = models.DateTimeField(default=timezone.now, editable=False,)
    endereco_bairro = models.CharField(blank=True, max_length=128, null=True)
    endereco_cep = models.CharField(blank=True, max_length=8, null=True)
    endereco_cidade = models.CharField(blank=True, max_length=45, null=True)
    endereco_complemento = models.CharField(max_length=45, blank=True)
    telefone_ddd = models.CharField(blank=True, max_length=2, null=True)
    endereco_estado = models.CharField(blank=True, max_length=2, null=True)
    endereco_numero = models.CharField(blank=True, max_length=10, null=True)
    endereco_rua = models.CharField(blank=True, max_length=100, null=True)
    perfil = models.ForeignKey(
        'PerfilParticipante',
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name='participantes',
        related_query_name='participante',
    )
    razao_social = models.CharField(blank=True, max_length=150, null=True)
    responsavel = models.CharField(blank=True, max_length=150, null=True)
    telefone_numero = models.CharField(blank=True, max_length=150, null=True)
    telefone_ramal = models.CharField(blank=True, max_length=5, null=True)
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    ix_id = models.ForeignKey(
        'IX',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='participantes',
        related_query_name='participante'
    )

    def save(self, *args, **kwargs):

        campos_alteram_contrato = ['razao_social', 'cnpj', 'endereco_rua',
                                   'endereco_numero', 'endereco_numero',
                                   'endereco_complemento', 'endereco_cidade',
                                   'endereco_estado', 'endereco_cep',
                                   'responsavel', 'endereco_bairro']
        if (self.is_dirty() and set(self.get_dirty_fields().keys()).issubset(
                set(campos_alteram_contrato))):
                    contrato_corrente = Contrato.objects.filter(
                        models.Q(participante__asn__exact=self.asn) &
                        models.Q(participante__ix_id_id=self.ix_id_id) &
                        models.Q(vigente=True))
                    if len(contrato_corrente) > 0:
                        for contrato in contrato_corrente:
                            contrato.assinado = False
                            contrato.save()
        self.full_clean()
        super(Participante, self).save(*args, **kwargs)

    # Rastreia alterações neste modelo
    history = HistoricalRecords()

    def __str__(self):
        return "[ASN: %s - %s]" % (self.asn, self.ix_id.codigo)

    class Meta:
        unique_together = (('asn', 'ix_id'),)
        ordering = ('asn',)
        verbose_name = 'Participante'
        verbose_name_plural = 'Participantes'


class PerfilParticipante(models.Model):

    uuid = models.UUIDField(primary_key=True, default=uuid4)
    tipo = models.CharField(max_length=30)
    fator_de_desconto = models.FloatField(
        default=0.00,
        error_messages={
            'min_value': 'Insira um valor de desconto válido. Certifique-se '
                         'de que a entrada esteja entre 0 e 100.',
            'max_value': 'Insira um valor de desconto válido. Certifique-se '
                         'de que a entrada esteja entre 0 e 100.',
        },
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)]
    )

    def __str__(self):
        return "[%s]" % self.uuid

    class Meta:
        ordering = ('uuid',)
        verbose_name = 'PerfilParticipante'
        verbose_name_plural = 'PerfisParticipantes'

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(PerfilParticipante, self).save(*args, **kwargs)


class IX(models.Model):
    cidade = models.CharField(max_length=45)
    codigo = models.CharField(max_length=4)
    estado = models.CharField(max_length=4)
    ix_id = models.IntegerField(primary_key=True)
    nome_curto = models.CharField(max_length=16, verbose_name='Nome Curto')
    nome_longo = models.CharField(max_length=48, verbose_name='Nome')

    class Meta:
        ordering = ('codigo',)
        verbose_name = 'IX'
        verbose_name_plural = 'IXs'

    def __str__(self):
        return "[%s]" % (self.codigo,)


class Contrato(models.Model):
    objects = models.Manager()

    # atributos do modelo
    assinado = models.BooleanField()
    data_assinatura = models.DateTimeField(
        default=timezone.now,
        editable=False,
    )
    ix = models.ForeignKey(
        'IX',
        on_delete=models.CASCADE,
        related_name='contratos',
        related_query_name='contrato',
    )
    participante = models.ForeignKey(
        'Participante',
        on_delete=models.CASCADE,
        related_name='contratos',
        related_query_name='contrato',
    )
    template_pt = models.CharField(max_length=25000, null=True, blank=True)
    template_en = models.CharField(max_length=25000, null=True, blank=True)
    tipo = models.CharField(max_length=30)
    vigente = models.BooleanField()
    usuario = models.CharField(max_length=30)
    uuid = models.UUIDField(primary_key=True, default=uuid4)

    # model managers
    assinados = ContratosAssinados()
    nao_assinados = ContratosNaoAssinados()
    vigentes = ContratosVigentes()

    class Meta:
        ordering = ('-data_assinatura',)
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'

    def __str__(self):
        return "[Contrato: %s - Vigente: %s | Participante: %s]" % (
            self.uuid,
            self.vigente,
            self.participante.asn,
        )


class Servico(models.Model):
    objects = models.Manager()

    data_expiracao = models.DateField()
    hash = models.CharField(max_length=30)
    ix = models.ForeignKey(
        'IX',
        on_delete=models.CASCADE,
        related_name='servicos',
        related_query_name='servico',
    )
    participante = models.ForeignKey(
        'Participante',
        on_delete=models.CASCADE,
        related_name='servicos',
        related_query_name='servico',
    )
    preco = models.FloatField(
        default=0.00,
        error_messages={
            'min_value': 'Insira uma preço válido.'
        },
        validators=[MinValueValidator(0.0)]
    )
    recorrente = models.BooleanField()
    tipo = models.CharField(max_length=255)
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid4,
    )

    em_fatura = ServicoManager()

    # ### Quando Listar Servico como Aberta
    # ToDO: Query: data de expiracao do servico <= data de hoje E
    # ToDO: Query: data de expiracao do servico > fatura data de emissao OU
    # ToDO: Query: data de expiracao do servico <= data fatura emitida E
    #       status da fatura cancelado

    class Meta:
        ordering = ('participante', 'data_expiracao',)
        verbose_name = 'Servico'
        verbose_name_plural = 'Servicos'

    def __str__(self):
        return "[%s | ASN: %s]" % (self.uuid, self.participante.asn,)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Servico, self).save(*args, **kwargs)


class Fatura(models.Model):

    def auto_increment_id_financeiro():
        if Fatura.objects.all():
            return Fatura.objects.all().order_by(
                'id_financeiro').last().id_financeiro + 1
        else:
            return 0

    objects = models.Manager()

    # atributos do modelo
    boleto_gerado = models.BooleanField(default=False)
    boleto_url = models.CharField(
        error_messages={
            'invalid': 'Insira uma url válida.'
        },
        max_length=255,
        null=True,
        blank=True,
        validators=[URLValidator()]
    )
    data_fatura_gerada = models.DateField(
        default=timezone.now,
        editable=False,
    )
    encerrada = models.BooleanField(default=False)
    estado = models.CharField(max_length=30)
    id_financeiro = models.BigIntegerField(default=auto_increment_id_financeiro)  # id usado pela equipe Financeira
    servicos = models.ManyToManyField(
        'Servico',
        related_name='faturas',
        related_query_name='fatura',
    )
    # ToDo: Poderia remover essa FK pois o Participante tem no Serviço.
    participante = models.ForeignKey(
        'Participante',
        related_name='faturas',
        related_query_name='fatura',
        on_delete=models.CASCADE
    )
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid4,
    )
    valor = models.FloatField()
    vencimento = models.DateField()

    # model managers
    abertas = FaturaAbertaManager()
    vencidas = FaturaVencidaManager()

    class Meta:
        ordering = ('-vencimento',)
        verbose_name = 'Fatura'
        verbose_name_plural = 'Faturas'

    def __str__(self):
        return "[%s | ANS: %s]" % (self.uuid, self.participante.asn)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Fatura, self).save(*args, **kwargs)


class OrdemDeCompra(models.Model):

    fatura = models.OneToOneField(
        'Fatura',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='ordem_compra',
        related_query_name='ordem_compra',
    )
    identificacao_oc = models.CharField(max_length=30)
    url = models.CharField(
        error_messages={
            'invalid': 'Insira uma url válida.'
        },
        max_length=255,
        blank=True,
    )

    class Meta:
        ordering = ('-identificacao_oc',)
        verbose_name = 'OrdemDeCompra'
        verbose_name_plural = 'OrdensDeCompra'

    def __str__(self):
        return "[%s]" % self.identificacao_oc

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(OrdemDeCompra, self).save(*args, **kwargs)
