from itertools import cycle

from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy

from invoice_api.core.models import (IX, Contrato, Participante,
                                     PerfilParticipante)
from invoice_api.core.validators import CNPJ_INVALIDO


class TestParticipante(TestCase):
    """
    Teste modelo Participante
    """
    def setUp(self):
        self.ix = mommy.make(IX)
        self.asn = 22548
        self.razao_social = 'Núcleo de Inf. e Coord. do Ponto BR - NIC.BR'
        self.cnpj = '05506560000136'
        self.responsavel = 'Demi Getschko'
        self.endereco_rua = 'Avenida das Nações Unidas'
        self.endereco_numero = '11541'
        self.endereco_complemento = '7º andar'
        self.endereco_bairro = 'Brooklin Paulista'
        self.endereco_cep = '04578000'
        self.endereco_cidade = 'São Paulo'
        self.endereco_estado = 'SP'
        self.perfil_participante = mommy.make(
            PerfilParticipante,
            fator_de_desconto=50
        )
        self.telefone_ddd = '11'
        self.telefone_numero = '55093500'
        self.telefone_ramal = '3527'
        self.participante = mommy.make(
            Participante,
            ix_id=self.ix,
            asn=self.asn,
            razao_social=self.razao_social,
            cnpj=self.cnpj,
            responsavel=self.responsavel,
            endereco_rua=self.endereco_rua,
            endereco_numero=self.endereco_numero,
            endereco_complemento=self.endereco_complemento,
            endereco_bairro=self.endereco_bairro,
            endereco_cep=self.endereco_cep,
            endereco_cidade=self.endereco_cidade,
            endereco_estado=self.endereco_estado,
            perfil=self.perfil_participante,
            telefone_ddd=self.telefone_ddd,
            telefone_numero=self.telefone_numero,
            telefone_ramal=self.telefone_ramal,
        )

        # Contrato para o participante
        self.contrato = Contrato.objects.create(
            assinado=True,
            ix=self.ix,
            participante=self.participante,
            tipo='',
            vigente=True,
            usuario=''
        )

    def teste__str__(self):
        """
        Verifica se __str__ do modelo retorna conforme o padrão atribuido:
            [ASN: <asn>]
        """
        self.assertEqual(
            str(self.participante),
            '[ASN: {} - {}]'.format(
                self.participante.asn, self.participante.ix_id.codigo
            )
        )

    def teste_cnpj_invalido(self):
        """
        Verifica a mensagem de erro do atributo cnpj caso seja persistido uma
            entrada de cnpj inválido.
        """

        with self.assertRaisesMessage(ValidationError, CNPJ_INVALIDO):
            mommy.make(Participante, cnpj='CNPJ inválido')

    def teste_meta_verbose_name(self):
        """
        Verifica se o Participante.Meta.verbose_name corresponde com o
            nome da classe.
        """
        self.assertEqual(
            str(Participante._meta.verbose_name), 'Participante')

    def teste_meta_verbose_name_plural(self):
        """
        Verifica se o Participante.Meta.verbose_name_plural corresponde
            com o nome da classe no plural.
        """
        self.assertEqual(
            str(Participante._meta.verbose_name_plural),
            'Participantes'
        )

    def teste_ordenacao(self):
        """
        Verifica se a ordem de filtro corresponde ao definido no modelo:
            ('asn', )
        """
        asns = [2893, 1234, 11224]
        participantes = mommy.make(
            Participante,
            asn=cycle(asns),
            _quantity=len(asns)
        )
        qs = Participante.objects.all()
        self.assertEqual(qs[0], participantes[1])
        self.assertEqual(qs[1], participantes[0])
        self.assertEqual(qs[2], participantes[2])
        self.assertEqual(qs[3], self.participante)

    def teste_related_name_e_related_query_name_participante(self):
        """
        Garantir se o related_name e related_query_name no atributo
            perfil retornam valores corretos.
        """
        participante = mommy.make(
            Participante,
            asn=32131,
            cnpj=self.cnpj,
            perfil=self.perfil_participante
        )

        qs = PerfilParticipante.objects.get(
            participante__asn=self.asn
        )
        self.assertEqual(qs, self.perfil_participante)
        self.assertIn(self.participante, qs.participantes.all())
        self.assertIn(participante, qs.participantes.all())

    def teste_alteracao_campo_que_nao_alteram_contrato(self):
        """
        Garantir que ao alterar um campo que não é usado no contrato,
        mantém o estado de assinado do contrato em True
        """
        p = self.participante
        p.telefone_ddd = '13'
        p.save()

        contrato_assinado = Contrato.objects.get(
            participante=self.participante)
        self.assertEqual(contrato_assinado.assinado, True)

    def teste_alteracao_campo_que_alteram_contrato(self):
        """
        Garantir que ao alterar um campo que é usado no contrato, o estado do
        contrato de assinado é atualizado para False
        :return:
        """

        p = self.participante
        p.endereco_numero = '22542'
        p.save()
        contrato_assinado = Contrato.objects.get(
            participante=self.participante)

        self.assertEqual(contrato_assinado.assinado, False)
