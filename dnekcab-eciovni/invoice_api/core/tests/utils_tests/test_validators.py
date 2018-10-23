from django.core.exceptions import ValidationError
from django.test import TestCase
from invoice_api.core.validators import CNPJ_INVALIDO, validacao_cnpj


class TestCNPJValidator(TestCase):
    def teste_cnpj_invalido(self):
        cnpj_set = (
            '',
            '12222',
            '231231231156',
            '47744w36000122',
            '808222280001048',
            '80822228000101',
            '80822228000114'
        )

        for cnpj in cnpj_set:
            with self.assertRaisesMessage(ValidationError, CNPJ_INVALIDO):
                validacao_cnpj(cnpj)

    def teste_cnpj_valido(self):
        cnpj_set = (
            '80822228000104',
            '64934767000170',
            '96964120000188',
            '62151571000184',
            '47744336000122',
        )

        for cnpj in cnpj_set:
            validacao_cnpj(cnpj)
