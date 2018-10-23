from itertools import cycle

from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy

from invoice_api.core.models import PerfilParticipante


class TestPerfilParticipante(TestCase):
    """"
    Teste modelo PerfilParticipante
    """
    def setUp(self):
        self.fator_desconto = 60
        self.perfil_participante = mommy.make(
            PerfilParticipante,
            uuid='2e314354-fcb6-4131-a5f5-a3d349c9a368',
            fator_de_desconto=self.fator_desconto
        )

    def teste__str__(self):
        """
        Verifica se __str__ do modelo retorna conforme o padrão atribuido:
            [<uuid>]
        """
        self.assertEqual(
            str(self.perfil_participante),
            '[{0}]'.format(
                self.perfil_participante.uuid,
            )
        )

    def teste_meta_verbose_name(self):
        """
        Verifica se o PerfilParticipante.Meta.verbose_name corresponde com o
            nome da classe.
        """
        self.assertEqual(
            str(PerfilParticipante._meta.verbose_name), 'PerfilParticipante')

    def teste_meta_verbose_name_plural(self):
        """
        Verifica se o PerfilParticipante.Meta.verbose_name_plural corresponde
            com o nome da classe no plural.
        """
        self.assertEqual(
            str(PerfilParticipante._meta.verbose_name_plural),
            'PerfisParticipantes'
        )

    def teste_ordenacao(self):
        """
        Verifica se a ordem de filtro corresponde ao definido no modelo:
            ('uuid',)
        """
        uuid = [
            '5dc817a2-40a0-44d9-982b-0e20718e48c1',
            'dc7414cb-9f2f-4854-9d61-e48d2d8bdb41',
            'eb04ae6a-c5f3-49c2-9ecd-e5aca6ed4047',
        ]
        perfis_participantes = mommy.make(
            PerfilParticipante,
            _quantity=len(uuid),
            uuid=cycle(uuid),
        )

        qs = PerfilParticipante.objects.all()
        self.assertEqual(qs[0], self.perfil_participante)
        self.assertEqual(qs[1], perfis_participantes[0])
        self.assertEqual(qs[2], perfis_participantes[1])
        self.assertEqual(qs[3], perfis_participantes[2])

    def teste_validacao_fator_de_desconto(self):
        """
        Garantir que a validação de `MinValueValidator` e `MaxValueValidator`
            exibe a mensagem de erro correta.
        """
        mensagem = 'Insira um valor de desconto válido. Certifique-se ' \
                   'de que a entrada esteja entre 0 e 100.'
        with self.assertRaisesMessage(ValidationError, mensagem):
            mommy.make(PerfilParticipante, fator_de_desconto=-1)

        with self.assertRaisesMessage(ValidationError, mensagem):
            mommy.make(PerfilParticipante, fator_de_desconto=101)
