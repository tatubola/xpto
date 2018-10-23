from datetime import datetime
from itertools import cycle

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from invoice_api.core.models import IX, Participante, Servico
from model_mommy import mommy


class TestServico(TestCase):
    """
    Teste do modelo Servico.
    """
    def setUp(self):
        self.ix = mommy.make(IX, _quantity=2)
        self.asns = [3231, 22548]
        self.participantes = mommy.make(
            Participante,
            _quantity=len(self.asns),
            asn=cycle(self.asns),
        )
        self.preco = 289.01
        self.servico = mommy.make(
            Servico,
            ix=self.ix[0],
            participante=self.participantes[1],
            preco=self.preco,
        )

    def teste__str__(self):
        """
        Verifica se __str__ do modelo retorna conforme o padrão atribuido:
            [<servico.uuid> | ASN: <participante.asn>]
        """
        self.assertEqual(
            str(self.servico),
            '[{0} | ASN: {1}]'.format(
                self.servico.uuid,
                self.asns[1],
            )
        )

    def teste_deletar_ix_contratos_apagados_em_cascata(self):
        """
        Garantir que ao deletar um IX, todos os Servicos relacionados a ele
            também serão apagados em cascata da base de dados.
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

        # Novos servicos criados com os participantes e ix listados acima
        servicos = mommy.make(
            Servico,
            _quantity=len(_participantes),
            ix=cycle(_ix),
            participante=cycle(_participantes),
        )

        self.ix[0].delete()
        # Garante que o IX foi apagado e sua relação com servico também
        self.assertEqual(Servico.objects.all().count(), 1)
        self.assertIn(servicos[2], Servico.objects.all())

    def teste_deletar_participante_contratos_apagados_em_cascata(self):
        """
        Garantir que ao deletar um Participante, todos os Contratos atrelados a
            ele também serão apagados em cascata da base de dados.
        """

        _participantes = [
            self.participantes[0],
            self.participantes[0],
            self.participantes[0],
        ]

        _ix = [
            self.ix[0],
            self.ix[0],
            self.ix[1],
        ]

        mommy.make(
            Servico,
            _quantity=len(_participantes),
            ix=cycle(_ix),
            participante=cycle(_participantes),
        )

        self.participantes[0].delete()
        # Garante que o participante foi apagado e sua relação com
        # servicos também
        self.assertEqual(Servico.objects.all().count(), 1)
        self.assertIn(self.servico, Servico.objects.all())

    def teste_meta_verbose_name(self):
        """
        Verifica se o Servico.Meta.verbose_name corresponde com o nome da
            classe.
        """
        self.assertEqual(
            str(Servico._meta.verbose_name), 'Servico')

    def teste_meta_verbose_name_plural(self):
        """
        Verifica se o Servico.Meta.verbose_name_plural corresponde com o nome
            da classe no plural.
        """
        self.assertEqual(str(Servico._meta.verbose_name_plural), 'Servicos')

    def teste_preco_invalido(self):
        """
        Verifica a mensagem de erro do atributo preco caso seja persistido uma
            entrada de preco inválido.
        """
        mensagem = (
            'Insira uma preço válido.'
        )

        with self.assertRaisesMessage(ValidationError, mensagem):
            mommy.make(Servico, preco=-1)

    def teste_related_name_e_related_query_name_ix(self):
        """
        Garantir se o related_name e related_query_name no atributo ix
            retornam valores corretos.
        """
        preco = 231.00
        servico = mommy.make(
            Servico,
            ix=self.ix[0],
            preco=preco,
        )

        qs = IX.objects.get(
            servico__preco=preco
        )
        self.assertEqual(qs, self.ix[0])
        self.assertIn(self.servico, qs.servicos.all())
        self.assertIn(servico, qs.servicos.all())

    def teste_related_name_e_related_query_name_participante(self):
        """
        Garantir se o related_name e related_query_name no atributo
            participante retornam valores corretos.
        """
        preco = 231.00
        servico = mommy.make(
            Servico,
            participante=self.participantes[1],
            preco=preco,
        )

        qs = Participante.objects.get(
            servico__preco=preco
        )
        self.assertEqual(qs, self.participantes[1])
        self.assertIn(self.servico, qs.servicos.all())
        self.assertIn(servico, qs.servicos.all())

    def teste_ordenacao(self):
        """
        Verifica se a ordem de filtro corresponde ao definido no modelo:
            ('participante', 'data_expiracao',)
        """
        data_expiracao = [
            datetime(2017, 7, 26, tzinfo=timezone.utc),
            datetime(2017, 8, 26, tzinfo=timezone.utc),
            datetime(2015, 7, 26, tzinfo=timezone.utc),
            datetime(2017, 5, 8, tzinfo=timezone.utc),
        ]

        participantes = [
            self.participantes[0],
            self.participantes[1],
            self.participantes[1],
            self.participantes[0]
        ]

        servicos = mommy.make(
            Servico,
            participante=cycle(participantes),
            data_expiracao=cycle(data_expiracao),
            _quantity=len(data_expiracao),
        )

        qs = Servico.objects.all()
        self.assertEqual(qs[0], servicos[3])
        self.assertEqual(qs[1], servicos[0])
        self.assertEqual(qs[2], servicos[2])
        self.assertEqual(qs[3], servicos[1])
        self.assertEqual(qs[4], self.servico)