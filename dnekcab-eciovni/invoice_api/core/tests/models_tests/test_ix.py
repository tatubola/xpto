from itertools import cycle

from django.test import TestCase
from model_mommy import mommy

from invoice_api.core.models import IX


class TestIX(TestCase):
    """
    Teste do modelo IX
    """
    def setUp(self):
        self.codigo = 'jpa'
        self.nome_curto = 'João Pessoa'
        self.nome_longo = 'João Pessoa - JPA'
        self.estado = 'PB'
        self.cidade = 'João Pessoa'
        self.ix = mommy.make(
            IX,
            codigo=self.codigo,
            nome_curto=self.nome_curto,
            nome_longo=self.nome_longo,
            estado=self.estado,
            cidade=self.cidade,

        )

    def teste__str__(self):
        """
        Verifica se __str__ do modelo retorna conforme o padrão atribuido:
            [<codigo>]
        """
        self.assertEqual(str(self.ix), '[{0}]'.format(self.codigo))

    def teste_meta_verbose_name(self):
        """
        Verifica se o IX.Meta.verbose_name corresponde com o nome da
            classe.
        """
        self.assertEqual(
            str(IX._meta.verbose_name), 'IX')

    def teste_meta_verbose_name_plural(self):
        """
        Verifica se o IX.Meta.verbose_name_plural corresponde com o nome
            da classe no plural.
        """
        self.assertEqual(str(IX._meta.verbose_name_plural), 'IXs')

    def teste_ordenacao(self):
        """
        Verifica se a ordem de filtro corresponde ao definido no modelo:
            ('codigo', )
        """

        codigos = ['rs', 'sp', 'rj', 'df']
        ixs = mommy.make(IX, codigo=cycle(codigos), _quantity=4)

        qs = IX.objects.all()
        self.assertEqual(qs[0], ixs[3])
        self.assertEqual(qs[1], self.ix)
        self.assertEqual(qs[2], ixs[2])
        self.assertEqual(qs[3], ixs[0])
        self.assertEqual(qs[4], ixs[1])

    def teste_verbose_name_atributo_nome_curto(self):
        """
        Verifica se o IX.nome_curto.verbose_name_plural corresponde com o nome
            atribuido.
        """
        self.assertEqual(
            IX._meta.get_field('nome_curto').verbose_name,
            'Nome Curto'
        )

    def teste_verbose_name_atributo_nome_longo(self):
        """
        Verifica se o IX.nome_longo.verbose_name_plural corresponde com o nome
            atribuido.
        """
        self.assertEqual(
            IX._meta.get_field('nome_longo').verbose_name,
            'Nome'
        )
