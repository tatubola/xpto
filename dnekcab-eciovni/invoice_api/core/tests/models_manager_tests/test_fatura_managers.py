from datetime import datetime
from itertools import cycle

from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy

from invoice_api.core.models import Fatura, Participante, Servico


class TestFatura(TestCase):
    """
    Teste do managers Fatura.
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

    def teste_model_manager_faturas_abertas(self):
        """
        Garantir que o model manager FaturaAbertaManager retorna todos as
            faturas que estão abertas.
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

        fatura_aberta_hoje = mommy.make(
            Fatura,
            boleto_url='http://nic.br/boleto/2982392',
            vencimento=datetime.today()
        )

        self.assertEqual(Fatura.abertas.all().count(), 4)
        for fatura in faturas_vencidas:
            self.assertNotIn(
                fatura,
                Fatura.abertas.all()
            )
        self.assertNotIn(self.fatura, Fatura.abertas.all())

        for fatura in fatura_abertas:
            self.assertIn(fatura, Fatura.abertas.all())
        self.assertIn(fatura_aberta_hoje, Fatura.abertas.all())
