# import re

from django.core.exceptions import ValidationError

from .utils.regex import Regex

# from django.core.validators import RegexValidator


regex = Regex()

# ------- Mensagens -------
CNPJ_INVALIDO = ('CNPJ inválido. Insira um CNPJ válido.')

# ------- Regex -------
# CNPJ = re.compile(r'^{0}$'.format(regex.cnpj))


# ------- Validation Functions -------


def validacao_cnpj(cnpj):
    if len(cnpj) != 14:
        raise ValidationError(CNPJ_INVALIDO, code='invalid')
    try:
        cnpj = [int(item) for item in list(cnpj)]
        pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        resto_1 = sum([a * b for a, b in zip(cnpj[:12], pesos_1)]) % 11
        digito_verificador_1 = 0 if resto_1 < 2 else 11 - resto_1

        if digito_verificador_1 != cnpj[12]:
            raise ValidationError(CNPJ_INVALIDO, code='invalid')

        pesos_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        resto_2 = sum([a * b for a, b in zip(cnpj[:13], pesos_2)]) % 11
        digito_verificador_2 = 0 if resto_2 < 2 else 11 - resto_2

        if digito_verificador_2 != cnpj[13]:
            raise ValidationError(CNPJ_INVALIDO, code='invalid')

    except Exception:
        raise ValidationError(CNPJ_INVALIDO, code='invalid')
