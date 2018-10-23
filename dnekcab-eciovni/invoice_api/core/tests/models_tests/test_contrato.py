from datetime import datetime
from itertools import cycle
import random

from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy

from invoice_api.core.models import Contrato, IX, Participante


class TestContrato(TestCase):
    """
    Teste do modelo Contrato.
    """
    def setUp(self):
        # Atributos
        self.assinado = True
        self.ix = mommy.make(IX, _quantity=2)
        self.asns = [3231, 22548]
        self.participantes = mommy.make(
            Participante,
            _quantity=len(self.asns),
            asn=cycle(self.asns),
        )
        self.tipo = ''
        self.vigente = True
        self.usuario = ''

        # Objeto com os atributos setados
        self.contrato = Contrato.objects.create(
            assinado=self.assinado,
            ix=self.ix[0],
            participante=self.participantes[0],
            tipo=self.tipo,
            vigente=self.vigente,
            usuario=self.usuario,
        )

    def teste__str__(self):
        """
        Verifica se __str__ do modelo retorna conforme o padrão atribuido:
            [Contrato: <uuid> - Vigente: <vidente> | Participante: <cnpj>]
        """
        self.assertEqual(
            str(self.contrato),
            '[Contrato: {0} - Vigente: {1} | Participante: {2}]'.format(
                self.contrato.uuid,
                self.contrato.vigente,
                self.asns[0],
            )
        )

    def teste_deletar_ix_contratos_apagados_em_cascata(self):
        """
        Garantir que ao deletar um IX, todos os Contratos atrelados a
            ele também serão apagados em cascata da base de dados.
        """

        # Lista de participantes
        _participantes = [
            self.participantes[0],
            self.participantes[1],
            self.participantes[0],
        ]

        # Lista  de ix
        _ix = [
            self.ix[0],
            self.ix[0],
            self.ix[1],
        ]

        # Novos contratos criados com os participantes e ix listados acima
        contratos = mommy.make(
            Contrato,
            _quantity=len(_participantes),
            ix=cycle(_ix),
            participante=cycle(_participantes),
        )

        self.ix[0].delete()
        # Garante que o IX foi apagado e sua relação com contrato também
        self.assertEqual(Contrato.objects.all().count(), 1)
        self.assertIn(contratos[2], Contrato.objects.all())

    def teste_deletar_participante_contratos_apagados_em_cascata(self):
        """
        Garantir que ao deletar um Participante, todos os Contratos atrelados a
            ele também serão apagados em cascata da base de dados.
        """

        _participantes = [
            self.participantes[0],
            self.participantes[1],
            self.participantes[0],
        ]

        _ix = [
            self.ix[0],
            self.ix[0],
            self.ix[1],
        ]

        contratos = mommy.make(
            Contrato,
            _quantity=len(_participantes),
            ix=cycle(_ix),
            participante=cycle(_participantes),
        )

        self.participantes[0].delete()
        # Garante que o participante foi apagado e sua relação com
        # contrato também
        self.assertEqual(Contrato.objects.all().count(), 1)
        self.assertIn(contratos[1], Contrato.objects.all())

    def teste_meta_verbose_name(self):
        """
        Verifica se o Contrato.Meta.verbose_name corresponde com o nome da
            classe.
        """
        self.assertEqual(
            str(Contrato._meta.verbose_name), 'Contrato')

    def teste_meta_verbose_name_plural(self):
        """
        Verifica se o Contrato.Meta.verbose_name_plural corresponde com o nome
            da classe no plural.
        """
        self.assertEqual(str(Contrato._meta.verbose_name_plural), 'Contratos')

    def teste_model_manager_contratos_assinados(self):
        """
        Garantir que o model manager ContratosAssinados retorna todos os
            contratos que foram assinados apenas.
        """
        contratos_assinados = mommy.make(
            Contrato,
            _quantity=2,
            assinado=True,
            ix=random.choice(self.ix),
            participante=random.choice(self.participantes),
        )

        contratos_nao_assinados = mommy.make(
            Contrato,
            _quantity=2,
            assinado=False,
            ix=random.choice(self.ix),
            participante=random.choice(self.participantes),
        )

        self.assertEqual(Contrato.assinados.all().count(), 3)
        for contrato in contratos_assinados:
            self.assertIn(contrato, Contrato.assinados.all())
        self.assertIn(self.contrato, Contrato.assinados.all())

        for contrato in contratos_nao_assinados:
            self.assertNotIn(contrato, Contrato.assinados.all())

    def teste_model_manager_contratos_nao_assinados(self):
        """
        Garantir que o model manager ContratosNaoAssinados retorna todos os
            contratos que não foram assinados apenas.
        """
        contratos_assinados = mommy.make(
            Contrato,
            _quantity=2,
            assinado=True,
            ix=random.choice(self.ix),
            participante=random.choice(self.participantes),
        )

        contratos_nao_assinados = mommy.make(
            Contrato,
            _quantity=3,
            assinado=False,
            ix=random.choice(self.ix),
            participante=random.choice(self.participantes),
        )

        self.assertEqual(Contrato.assinados.all().count(), 3)
        for contrato in contratos_nao_assinados:
            self.assertIn(
                contrato,
                Contrato.nao_assinados.all()
            )

        for contrato in contratos_assinados:
            self.assertNotIn(contrato, Contrato.nao_assinados.all())
        self.assertNotIn(self.contrato, Contrato.nao_assinados.all())

    def teste_model_manager_contratos_vigentes(self):
        """
        Garantir que o model manager ContratosVigentes retorna todos os
            contratos que estão vigentes apenas.
        """
        contratos_vigentes = mommy.make(
            Contrato,
            _quantity=3,
            vigente=True,
            ix=random.choice(self.ix),
            participante=random.choice(self.participantes),
        )

        contratos_nao_vigentes = mommy.make(
            Contrato,
            _quantity=3,
            vigente=False,
            ix=random.choice(self.ix),
            participante=random.choice(self.participantes),
        )

        self.assertEqual(Contrato.vigentes.all().count(), 4)
        for contrato in contratos_vigentes:
            self.assertIn(
                contrato,
                Contrato.vigentes.all()
            )
        self.assertIn(self.contrato, Contrato.vigentes.all())

        for contrato in contratos_nao_vigentes:
            self.assertNotIn(contrato, Contrato.vigentes.all())

    def teste_related_name_e_related_query_name_ix(self):
        """
        Garantir se o related_name e related_query_name no atributo ix
            retornam valores corretos.
        """
        contrato_2 = mommy.make(
            Contrato,
            ix=self.ix[0],
            vigente=False
        )

        qs = IX.objects.get(
            contrato__vigente=self.vigente
        )
        self.assertEqual(qs, self.ix[0])
        self.assertIn(self.contrato, qs.contratos.all())
        self.assertIn(contrato_2, qs.contratos.all())

    def teste_related_name_e_related_query_name_participante(self):
        """
        Garantir se o related_name e related_query_name no atributo
            participante retornam valores corretos.
        """
        contrato_2 = mommy.make(
            Contrato,
            participante=self.participantes[0],
            vigente=False
        )

        qs = Participante.objects.get(
            contrato__vigente=self.vigente
        )
        self.assertEqual(qs, self.participantes[0])
        self.assertIn(self.contrato, qs.contratos.all())
        self.assertIn(contrato_2, qs.contratos.all())

    def teste_ordenacao(self):
        """
        Verifica se a ordem de filtro corresponde ao definido no modelo:
            ('-data_assinatura', )
        """
        datas_assinatura = [
            datetime(2017, 7, 26, tzinfo=timezone.utc),
            datetime(2017, 8, 26, tzinfo=timezone.utc),
            datetime(2015, 7, 26, tzinfo=timezone.utc),
            datetime(2017, 5, 8, tzinfo=timezone.utc),
        ]
        contratos = mommy.make(
            Contrato,
            data_assinatura=cycle(datas_assinatura),
            _quantity=len(datas_assinatura),
        )

        qs = Contrato.objects.all()
        self.assertEqual(qs[0], self.contrato)
        self.assertEqual(qs[1], contratos[1])
        self.assertEqual(qs[2], contratos[0])
        self.assertEqual(qs[3], contratos[3])
        self.assertEqual(qs[4], contratos[2])
