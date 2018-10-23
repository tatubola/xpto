from datetime import datetime
from itertools import cycle

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy

from invoice_api.core.models import Fatura, Participante, Servico


class TestFatura(TestCase):
    """
    Teste do modelo Fatura.
    """
    def setUp(self):
        self.asn = 22548
        self.participante = mommy.make(Participante, asn=self.asn)
        self.boleto_gerado = True
        self.boleto_url = 'http://nic.br/boleto/2982389'
        self.data_fatura_gerada = datetime(2018, 7, 26, tzinfo=timezone.utc)
        self.encerrada = False
        self.id_financeiro = '3612'
        self.servicos = mommy.make(
            Servico,
            _quantity=3,
            participante=self.participante,
        )
        self.valor = 25485
        self.vencimento = datetime(2018, 5, 14, tzinfo=timezone.utc)
        self.fatura = mommy.make(
            Fatura,
            boleto_gerado=self.boleto_gerado,
            boleto_url=self.boleto_url,
            data_fatura_gerada=self.data_fatura_gerada,
            encerrada=self.encerrada,
            id_financeiro=self.id_financeiro,
            participante=self.participante,
            servicos=self.servicos,
            valor=self.valor,
            vencimento=self.vencimento,
        )

    def teste__str__(self):
        """
        Verifica se __str__ do modelo retorna conforme o padrão atribuido:
            [<uuid> | ASN: <participante.asn>]
        """
        self.assertEqual(
            str(self.fatura),
            '[{0} | ANS: {1}]'.format(
                self.fatura.uuid,
                self.asn,
            )
        )

    def teste_deletar_participante_faturas_apagados_em_cascata(self):
        """
        Garantir que ao deletar um Participante, todos as faturas relacionadas
            a ele também serão apagados em cascata da base de dados.
        """

        participantes = mommy.make(Participante, _quantity=4)

        faturas = mommy.make(
            Fatura,
            _quantity=len(participantes),
            boleto_url='http://nic.br/boleto/2982392',
            participante=cycle(participantes),
        )
        self.assertEqual(Fatura.objects.all().count(), 5)
        self.assertEqual(Participante.objects.all().count(), 5)

        participantes[0].delete()
        # Garante que o participante foi apagado e sua relação com a fatura
        # também
        self.assertEqual(Fatura.objects.all().count(), 4)
        self.assertIn(faturas[1], Fatura.objects.all())
        self.assertIn(faturas[2], Fatura.objects.all())
        self.assertIn(faturas[3], Fatura.objects.all())
        self.assertIn(self.fatura, Fatura.objects.all())

    def teste_meta_verbose_name(self):
        """
        Verifica se o Fatura.Meta.verbose_name corresponde com o nome da
            classe.
        """
        self.assertEqual(
            str(Fatura._meta.verbose_name), 'Fatura')

    def teste_meta_verbose_name_plural(self):
        """
        Verifica se o Fatura.Meta.verbose_name_plural corresponde com o nome
            da classe no plural.
        """
        self.assertEqual(str(Fatura._meta.verbose_name_plural), 'Faturas')

    def teste_model_manager_faturas_vencidas(self):
        """
        Garantir que o model manager FaturaVencidaManager retorna todos as
            faturas que estão vencidas.
        """
        vencimentos = [
            datetime(2018, 5, 7, tzinfo=timezone.utc),
            datetime(2018, 2, 17, tzinfo=timezone.utc),
            datetime(2014, 3, 3, tzinfo=timezone.utc),
        ]

        faturas_vencidas = mommy.make(
            Fatura,
            _quantity=len(vencimentos),
            boleto_url='http://nic.br/boleto/2982392',
            vencimento=cycle(vencimentos),
        )

        fatura_abertas = mommy.make(
            Fatura,
            _quantity=3,
            boleto_url='http://nic.br/boleto/2982392',
            vencimento=datetime(
                datetime.today().year + 1,
                datetime.today().month,
                datetime.today().day,
                tzinfo=timezone.utc
            )
        )

        self.assertEqual(Fatura.vencidas.all().count(), 4)
        for fatura in faturas_vencidas:
            self.assertIn(
                fatura,
                Fatura.vencidas.all()
            )
        self.assertIn(self.fatura, Fatura.vencidas.all())

        for fatura in fatura_abertas:
            self.assertNotIn(fatura, Fatura.vencidas.all())

    def teste_related_name_e_related_query_name_participante(self):
        """
        Garantir se o related_name e related_query_name no atributo
            participante retornam valores corretos.
        """
        fatura_2 = mommy.make(
            Fatura,
            boleto_url='http://nic.br/boleto/2982392',
            participante=self.participante
        )

        qs = Participante.objects.get(
            fatura__boleto_url=self.boleto_url
        )
        self.assertEqual(qs, self.participante)
        self.assertIn(self.fatura, qs.faturas.all())
        self.assertIn(fatura_2, qs.faturas.all())

    def teste_related_name_e_related_query_name_servicos(self):
        """
        Garantir se o related_name e related_query_name no atributo
            participante retornam valores corretos.
        """
        vencimento = datetime(2018, 5, 14, tzinfo=timezone.utc)
        fatura_2 = mommy.make(
            Fatura,
            participante=self.participante,
            servicos=[self.servicos[0], self.servicos[2]],
            boleto_url='http://nic.br/boleto/2982390',
            vencimento=vencimento,
        )

        qs_servicos = Servico.objects.filter(
            fatura__participante=self.participante
        )
        for servico in self.servicos:
            self.assertIn(servico, qs_servicos)

        qs_fatura = self.servicos[0].faturas.filter(vencimento=vencimento)
        self.assertIn(fatura_2, qs_fatura)
        self.assertIn(self.fatura, qs_fatura)

    def teste_ordenacao(self):
        """
        Verifica se a ordem de filtro corresponde ao definido no modelo:
            ('-vencimento', )
        """
        vencimentos = [
            datetime(2017, 7, 26, tzinfo=timezone.utc),
            datetime(2017, 8, 26, tzinfo=timezone.utc),
            datetime(2015, 7, 26, tzinfo=timezone.utc),
            datetime(2017, 5, 8, tzinfo=timezone.utc),
        ]
        faturas = mommy.make(
            Fatura,
            _quantity=len(vencimentos),
            boleto_url='http://nic.br/boleto/2982391',
            vencimento=cycle(vencimentos),
        )

        qs = Fatura.objects.all()
        self.assertEqual(qs[0], self.fatura)
        self.assertEqual(qs[1], faturas[1])
        self.assertEqual(qs[2], faturas[0])
        self.assertEqual(qs[3], faturas[3])
        self.assertEqual(qs[4], faturas[2])

    def teste_url_invalida(self):
        """
        Verifica a mensagem de erro do atributo boleto_url caso seja persistido
            uma entrada de url inválido.
        """
        mensagem = (
            'Insira uma url válida'
        )

        with self.assertRaisesMessage(ValidationError, mensagem):
            mommy.make(Fatura, boleto_url='url inválida')
