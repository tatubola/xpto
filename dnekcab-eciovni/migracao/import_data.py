import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from database import Connect, Query

template_search_dir = os.getcwd()
output_file_dir = os.getcwd() + "/output/"
timestamp  = datetime.utcnow().strftime('%s')


file_output_name = "importa_participante_" + timestamp
f = open(output_file_dir + file_output_name, 'a')

con = Connect(user='desenv',
      password='Sigma1597',
      hostname='200.160.11.109',
      db='ptt')
cursor = con.mariadb().cursor()
q_cobranca = Query(['*'])
cursor.execute(q_cobranca.ptt_info_cobranca())
p_dict = dict()
participante_number = 0

template_env = Environment(loader=FileSystemLoader(template_search_dir))
c = template_env.get_template('template_insere_as')

for p in cursor.fetchall():
    c_participante = con.mariadb().cursor()
    c_participante.execute(q_cobranca.ptt_participante_ix(p[0]))
    ix_query_res = c_participante.fetchall()
    c_participante.close()
    if len(ix_query_res) > 0:
        ix_list = [ix_id[0] for ix_id in ix_query_res]
    else:
        ix_list = [0]

    for ix in ix_list:
        k = "part" + "_" + str(participante_number)
        p_dict[k] = {
            "asn":p[0],
            "razao_social":p[1],
            "cnpj":p[2],
            "responsavel":p[3],
            "enredeco_rua":p[6],
            "endereco_numero":p[7],
            "endereco_complemento":p[8],
            "endereco_bairro":p[9],
            "endereco_cep":p[10],
            "endereco_cidade":p[11],
            "endereco_estado":p[12],
            "telefone_numero":p[15],
            "telefone_ddd":p[14],
            "telefone_ramal":p[16],
            "ix_id": ix
        }
        f.write(c.render(p_dict[k]))

    participante_number = participante_number + 1


f.close()

########### Importacao de dados do IX

file_output_name = "importa_ix_" + timestamp
f = open(output_file_dir + file_output_name, 'a')

con = Connect(user='desenv',
      password='Sigma1597',
      hostname='200.160.11.109',
      db='ptt')
cursor = con.mariadb().cursor()
q_cobranca = Query(['*'])
cursor.execute(q_cobranca.ptt_ptt())
p_dict = dict()
ix_number = 0

template_env = Environment(loader=FileSystemLoader(template_search_dir))
c = template_env.get_template('template_insere_ix')

for p in cursor.fetchall():
    k = "part" + "_" + str(ix_number)
    p_dict[k] = {
        "ix_id":p[0],
        "codigo":p[1],
        "nome_curto":'',
        "nome_longo":'',
        "estado":p[3],
        "cidade":p[2]
    }
    ix_number = ix_number + 1
    f.write(c.render(p_dict[k]))

f.close()
cursor.close()
