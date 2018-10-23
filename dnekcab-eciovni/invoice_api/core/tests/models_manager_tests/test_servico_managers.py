from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy

from invoice_api.core.models import IX, Fatura, Participante, Servico


class TestServico(TestCase):

    def setUp(self):

        self.hoje = timezone.now().replace(
            hour=12,
            minute=00
        )

        self.ix_sp = mommy.make(IX,
                             codigo="sp",
                             cidade="Sao Paulo")

        self.participantes_sp = mommy.make(
            Participante,
            asn=26615
        )
        self.boleto_url = "http://nic.br/boleto/2982392"

    def test_lista_servico_em_fatura_cancelada(self):
        """
        Testa se um servico em uma fatura cancelada é listada como servico a
        ser cobrado
        """

        servico_cancelado = mommy.make(
            Servico,
            preco=100.99,
            ix=self.ix_sp,
            participante=self.participantes_sp,
            data_expiracao=self.hoje.replace(
                day=28,
                month=self.hoje.month - 2
            )
        )

        fatura_cancelada = mommy.make(
            Fatura,
            servicos=[servico_cancelado],
            estado='cancelada',
            vencimento=self.hoje.replace(
                day=28,
                month=self.hoje.month - 1
            ),
            boleto_url=self.boleto_url
        )

        self.assertIn(servico_cancelado, Servico.em_fatura.aberta())
        self.assertNotIn(servico_cancelado, Servico.em_fatura.fechada())

    def test_lista_servico_em_fatura_cancelada_e_fatura_paga(self):
        """
        Testa se um servico que estava em uma fatura cancelada e,
        posteriormente, é paga em uma fatura não é listada no mês corrente
        """

        servico = mommy.make(
            Servico,
            preco=100.99,
            ix=self.ix_sp,
            participante=self.participantes_sp,
            data_expiracao=self.hoje.replace(
                day=28,
                month=self.hoje.month - 3
            )
        )

        fatura_cancelada = mommy.make(
            Fatura,
            servicos=[servico],
            estado='cancelada',
            vencimento=self.hoje.replace(
                day=28,
                month=self.hoje.month - 2
            ),
            boleto_url=self.boleto_url
        )

        fatura_gerada = mommy.make(
            Fatura,
            servicos=[servico],
            estado='paga',
            vencimento=self.hoje.replace(
                day=28,
                month=self.hoje.month - 1
            ),
            boleto_url=self.boleto_url
        )

        self.assertIn(servico, Servico.em_fatura.fechada())
        self.assertNotIn(servico, Servico.em_fatura.aberta())

    def test_lista_servico_em_fatura_paga(self):
        """
        Testa se um servico é listado quando aparece em uma fatura paga.
        """

        servico = mommy.make(
            Servico,
            preco=100.99,
            ix=self.ix_sp,
            participante=self.participantes_sp,
            data_expiracao=self.hoje.replace(
                day=28,
                month=self.hoje.month - 2
            )
        )

        fatura_gerada = mommy.make(
            Fatura,
            servicos=[servico],
            estado='paga',
            vencimento=self.hoje.replace(
                day=28,
                month=self.hoje.month - 1
            ),
            boleto_url=self.boleto_url
        )

        self.assertIn(servico, Servico.em_fatura.fechada())
        self.assertNotIn(servico, Servico.em_fatura.aberta())

    def test_lista_servico_expirado_mes_corrente(self):
        """
        Testa se um servico criado no mes corrente NAO é listado em nenhum
        dos casos. Este tipo de servico somente deve ser listado no mes
        seguinte.
        """
        servico = mommy.make(
            Servico,
            preco=100.99,
            ix=self.ix_sp,
            participante=self.participantes_sp,
            data_expiracao=self.hoje.replace(
                day=28,
                hour=00,
                minute=00
            )
        )

        self.assertNotIn(servico, Servico.em_fatura.fechada())
        self.assertNotIn(servico, Servico.em_fatura.aberta())

    def test_lista_servico_expirado_mes_passado(self):
        """
        Testa se um servico cuja expiracao é o mes passado é listado como
        aberta.
        """
        servico = mommy.make(
            Servico,
            preco=100.99,
            ix=self.ix_sp,
            participante=self.participantes_sp,
            data_expiracao=self.hoje.replace(
                day=28,
                month=self.hoje.month - 1,
            )
        )

        self.assertIn(servico, Servico.em_fatura.aberta())
        self.assertNotIn(servico, Servico.em_fatura.fechada())

    def test_lista_servico_recorrente_expiracao_em_tres_meses(self):
        """
        Testa se um servico que foi pago antecipadamente por 3 meses (
        expiracao do servico sera em 3 meses) é listado como aberto.
        """
        month_mod = (self.hoje.month + 3) % 12
        servico = mommy.make(
            Servico,
            preco=100.99,
            ix=self.ix_sp,
            participante=self.participantes_sp,
            data_expiracao=self.hoje.replace(
                day=28,
                month=month_mod,
                year=(self.hoje.year + 1) if month_mod > 0 else self.hoje.year
            )
        )

        self.assertIn(servico, Servico.em_fatura.aberta())
        self.assertNotIn(servico, Servico.em_fatura.fechada())

    # def test_lista_servico_recorrente_pago_um_mes_expiracao_em_tres_meses(self):
    #     """
    #     Testa se um servico que foi pago antecipadamente e ja foi pago um
    #     mes, isto é, ele aparecera em uma fatura paga/gerada, é listado como
    #     em aberto e também como já fechado (já que este Servico aparece em
    #     uma fatura paga/gerada)
    #     """
    #
    #     servico = mommy.make(
    #         Servico,
    #         preco=100.99,
    #         ix=self.ix_sp,
    #         participante=self.participantes_sp,
    #         data_expiracao=self.hoje.replace(
    #             day=28,
    #             month=self.hoje.month + 3,
    #         )
    #     )
    #
    #     fatura = mommy.make(
    #         Fatura,
    #         servicos=[servico],
    #         estado='paga',
    #         vencimento=self.hoje.replace(
    #             day=28,
    #             month=self.hoje.month - 1
    #         ),
    #         boleto_url=self.boleto_url
    #     )
    #
    #     self.assertIn(servico, Servico.em_fatura.aberta())
    #     self.assertIn(servico, Servico.em_fatura.fechada())
