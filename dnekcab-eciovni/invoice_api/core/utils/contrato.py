def campos_contrato(campos_alterados):
    """
    Funcao que verifica se o campo alterado do cadastro do participante
    implica em renovação da assinatura do contrato
    :param campos_alterados: Dicionario com os campos que foram alterados
    :return: True or False
    """

    lista_campos_contrato = ['razao_social', 'cnpj', 'responsavel',
                             'endereco_rua', 'endereco_numero',
                             'endereco_complemente', 'endereco_cep',
                             'endereco_bairro', 'endereco_cidade',
                             'endereco_estado']

    for campo in campos_alterados.keys():
        if campo in lista_campos_contrato:
            return True

    return False
