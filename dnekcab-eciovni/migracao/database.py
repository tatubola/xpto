import mysql.connector
from mysql.connector import errorcode


class Connect(object):

    def __init__(self, user, hostname, password, db, port=3306):
        self.user = user
        self.hostname = hostname
        self.password = password
        self.db = db
        self.port = port

    def mariadb(self):
        try:
            self.c = mysql.connector.connect(user=self.user,
                                        password=self.password,
                                        host=self.hostname,
                                        database=self.db,
                                        port=self.port)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                msg = "Erro na Autenticacao - Verifique Usuario e Senha"
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                msg = "O Banco " + self.db + "nao existe"
            else:
                msg = err
            return msg

        return self.c

    def __del__(self):
        """
        Esse metodo foi necessario para evitar problema de Weak Reference
        """
        self.c.close()


class Query(object):

    def __init__(self, fields):
        """
        :param fields: Uma lista com os campos que devem ser buscados na tabela
        """

        self.fields_to_fetch = ", ".join(fields)

    def ptt_info_cobranca(self):

        query = "SELECT " + self.fields_to_fetch + " from info_cobranca"
        return query

    def ptt_ptt(self):

        query = "SELECT " + self.fields_to_fetch + " from ptt"
        return query

    def ptt_participante_ix(self, asn):

        query = "SELECT ptt_id from ptt WHERE codigo IN (SELECT ptt FROM pix " \
                "WHERE pix_id IN (SELECT pix_id FROM asn_pix WHERE asn=" + \
                str(asn) + "))"
        return query
