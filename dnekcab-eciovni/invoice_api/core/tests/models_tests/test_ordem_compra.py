from itertools import cycle

from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy
from model_mommy.recipe import seq

from invoice_api.core.models import Fatura, OrdemDeCompra


class TestOrdemCompra(TestCase):
    """
    Teste do modelo OrdemCompra.
    """
    def setUp(self):
        self.identificacao_oc = '2017'
        self.fatura = mommy.make(
            Fatura,
            boleto_url='http://www.nic.br/boleto/1'
        )
        self.url = '/volumeX/OrdemDeCompra/20180810/ordem_de_compra_01.pdf'
        self.ordem_compra = mommy.make(
            OrdemDeCompra,
            fatura=self.fatura,
            identificacao_oc=self.identificacao_oc,
            url=self.url,
        )

    def teste__str__(self):
        """
        Verifica se __str__ do modelo retorna conforme o padrão atribuido:
            [<identificacao_oc>]
        """
        self.assertEqual(
            str(self.ordem_compra),
            '[{0}]'.format(
                self.identificacao_oc
            )
        )

    def teste_deletar_faturas_ordens_compra_apagados_em_cascata(self):
        """
        Garantir que ao deletar uma Fatura, todos as Ordens de Compra
            atrelados a ele também serão apagados em cascata da base de dados.
        """
        faturas = mommy.make(
            Fatura,
            _quantity=2,
            boleto_url='http://www.nic.br/boleto/2'
        )
        mommy.make(
            OrdemDeCompra,
            _quantity=2,
            fatura=cycle(faturas),
            url='/volumeX/OrdemDeCompra/20180810/ordem_de_compra_02.pdf'
        )

        qs_ordem_compra = OrdemDeCompra.objects.all()
        self.assertEqual(qs_ordem_compra.count(), 3)

        qs_faturas = Fatura.objects.all()
        self.assertEqual(qs_faturas.count(), 3)

        faturas[0].delete()

        qs_ordem_compra = OrdemDeCompra.objects.all()
        self.assertEqual(qs_ordem_compra.count(), 2)

        qs_faturas = Fatura.objects.all()
        self.assertEqual(qs_faturas.count(), 2)

    def teste_meta_verbose_name(self):
        """
        Verifica se o OrdemDeCompra.Meta.verbose_name corresponde com o nome da
            classe.
        """
        self.assertEqual(
            str(OrdemDeCompra._meta.verbose_name), 'OrdemDeCompra')

    def teste_meta_verbose_name_plural(self):
        """
        Verifica se o OrdemDeCompra.Meta.verbose_name_plural corresponde com o
            nome da classe no plural.
        """
        self.assertEqual(
            str(OrdemDeCompra._meta.verbose_name_plural),
            'OrdensDeCompra'
        )

    def teste_related_name_e_related_query_name_ix(self):
        """
        Garantir se o related_name e related_query_name no atributo fatura
            retornam valores corretos.
        """

        qs = Fatura.objects.get(
            ordem_compra__identificacao_oc=self.identificacao_oc
        )
        self.assertEqual(qs, self.fatura)
        self.assertEqual(self.ordem_compra, qs.ordem_compra)

    def teste_ordenacao(self):
        """
        Verifica se a ordem de filtro corresponde ao definido no modelo:
            ('-identificacao_oc', )
        """
        ordens_compra = mommy.make(
            OrdemDeCompra,
            _quantity=4,
            fatura__boleto_url='http://www.nic.br/boleto/2',
            identificacao_oc=seq(2018),
            url='/volumeX/OrdemDeCompra/20180810/ordem_de_compra_02.pdf'
        )

        qs = OrdemDeCompra.objects.all()

        self.assertEqual(qs[0], ordens_compra[3])
        self.assertEqual(qs[1], ordens_compra[2])
        self.assertEqual(qs[2], ordens_compra[1])
        self.assertEqual(qs[3], ordens_compra[0])
        self.assertEqual(qs[4], self.ordem_compra)
