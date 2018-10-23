"""Module with classes and routines to improve app operations """
# System imports
import re
from subprocess import (CalledProcessError, PIPE, run)

# Third-party imports
from jinja2 import (FileSystemLoader, Environment)
from MySQLdb import (cursors, connect)

# Local source tree imports
from utils.whois import WhoIsHandler


class DBConnect(object):
    """
    Class to handle Data Base connections
    """
    host = '200.160.6.194'
    port = 3306

    def mysql_connect(self, mysql_user, mysql_password):
        """ Connect to a MySQL Database

        This method connects to a MySQL Server and returns a connection cursor
        to execute queries.

        Args:
            mysql_user: Valid user in MySQL server
            mysql_password: User's password

        Returns: MySQL Cursor to perform queries

        """
        my_db = connect(user=mysql_user,
                        passwd=mysql_password,
                        host=self.host, port=self.port,
                        cursorclass=cursors.DictCursor)

        my_cursor = my_db.cursor()
        return my_cursor


class FormatJson(object):
    """
    Class to format DB queries in JSON
    """
    template_search_dir = "/app/api/"
    # template_search_dir = "/home/abaruchi/Projects/NIC/ix-ticket-api/api/"

    @classmethod
    def format_ticket_detail(self, dict, ticket_id, ix_codigo):
        """ This method render a query in a structured JSON template

        Template Path inside the docker: /app/api/templates/

        Args:
            dict: Dictionary with the query output
            ticket_id: The ticket ID used to build th JSON

        Returns: A dict with the template filled

        """
        TEMPLATE_FILE = "templates/ticket_detail.json"

        template_loader = FileSystemLoader(searchpath=self.template_search_dir)
        template_env = Environment(loader=template_loader)
        template = template_env.get_template(TEMPLATE_FILE)

        as_whois = WhoIsHandler(dict["asn"])
        whois_dict = as_whois.who_is_to_dict()

        cnpj = None if as_whois.is_foreign() else whois_dict['ownerid']

        org_name = whois_dict['OrgName'] if 'OrgName' in whois_dict.keys() \
            else None

        org_mail = whois_dict['OrgTechEmail'] if 'OrgTechEmail' in \
                                                 whois_dict.keys() else None

        org_phone = whois_dict['OrgTechPhone'] if 'OrgTechPhone' in \
                                                  whois_dict.keys() else None

        template_vars = {
            "id": ticket_id,
            "asn": dict["asn"],
            "pix": dict["pix"],
            "ix": ix_codigo,
            "entity_name": dict["asn_nome"],
            "short_name": dict["asn_nome_curto"],
            "as_cnpj": cnpj,
            "site": dict["asn_url"],
            "street": dict["logradouro"],
            "number": dict["numero"],
            "compl": dict["complemento"],
            "neighbor": dict["bairro"],
            "city": dict["cidade"],
            "zip": dict["cep"],
            "state": dict["uf"],
            "country": dict["pais"],
            "adm_name": dict["adm_nome"],
            "adm_mail": dict["adm_email"],
            "adm_phone": dict["adm_tel"],
            "com_name": dict["com_nome"],
            "com_mail": dict["com_email"],
            "com_phone": dict["com_tel"],
            "noc_name": dict["noc_inoc"],
            "noc_mail": dict["noc_email"],
            "noc_phone": dict["noc_tel"],
            "peer_name": dict["peering_nome"],
            "peer_mail": dict["peering_email"],
            "peer_phone": dict["peering_tel"],
            "org_name": org_name,
            "org_mail": org_mail,
            "org_phone": org_phone
        }

        return template.render(template_vars)


class DBQueries(object):
    """
    Class used to return queries
    """
    def __init__(self, fields):
        """

        Args:
            fields: List with all columns to query from database
        """
        self.fields_to_fetch = ", ".join(fields)

    def query_all_tickets(self):
        """ Select to gather all tickets from database (open and closed)

        Returns: A Query string to be used by a database connection

        """
        query = "SELECT " + self.fields_to_fetch + " FROM ptt.pedido order " \
                                                   "by date_created DESC"

        return query

    def query_close_ticket(self):
        """ Select to gather all closed tickets from database

        Returns: A Query string to be used by a database connection

        """
        query = "SELECT " + self.fields_to_fetch + " FROM ptt.pedido WHERE " \
                                                   "status='fechado' order " \
                                                   "by date_created ASC"

        return query

    def query_open_ticket(self):
        """ Select to gather all open tickets from database

        Returns: A Query string to be used by a database connection

        """

        query = "SELECT " + self.fields_to_fetch + " FROM ptt.pedido WHERE " \
                                                   "status='aberto' order by " \
                                                   "date_created DESC"
        return query

    def query_ticket_detail(self, ticket_id):
        """ Select detailed information about a given ticket

        Args:
            ticket_id: Ticket to query from database

        Returns: A Query string to be used by a database connection

        """

        query = "SELECT * FROM ptt.form_conexao where asn IN (SELECT asn " \
                "FROM ptt.pedido where pedido_id = " + ticket_id + ")"

        return query

    def query_ix_codigo(self, ticket_id):
        """ Select to gather ptt_id from a given ticket

        Args:
            ticket_id: Ticket to query from database

        Returns: A Query string to be used by a database connection

        """

        query = "SELECT codigo from ptt.ptt where ptt_id in (SELECT ptt_id " \
                "from ptt.pedido where pedido_id = " + ticket_id + ");"

        return query
